from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from oauth2client import file, client, tools
from oauth2client.client import flow_from_clientsecrets
import http.client
import httplib2

import argparse
from oauth2client import tools
from oauth2client.file import Storage
import logging
import os
import time
import random
import requests

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class GooglePhotosClient:
    # scopes defined here: https://developers.google.com/photos/library/guides/authentication-authorization
    SCOPES = [
        'https://www.googleapis.com/auth/photoslibrary.appendonly',
        'https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata'
    ]
    REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
    CLIENT_CREDENTIALS_FILE = 'client_credentials.json'
    USER_CREDENTIALS_FILE = 'user_credentials.json'
    API_SERVICE_NAME = 'photoslibrary'
    API_VERSION = 'v1'

    # Maximum number of times to retry before giving up.
    MAX_RETRIES = 10

    RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, http.client.NotConnected,
    http.client.IncompleteRead, http.client.ImproperConnectionState,
    http.client.CannotSendRequest, http.client.CannotSendHeader,
    http.client.ResponseNotReady, http.client.BadStatusLine)

    # Always retry when an apiclient.errors.HttpError with one of these status
    # codes is raised.
    RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

    def __init__(self):
        self._storage = Storage(self.USER_CREDENTIALS_FILE) # will create file if needed
        self._user_credentials = self._storage.get() # returns None if file empty
    
    # command line discussion here: https://developers.google.com/api-client-library/python/guide/aaa_oauth
    def login_from_commandline(self):
        flow = flow_from_clientsecrets(self.CLIENT_CREDENTIALS_FILE,
            scope=self.SCOPES,
            redirect_uri=self.REDIRECT_URI)

        # there should be no command line arguments but just keeping up with template
        parser = argparse.ArgumentParser(parents=[tools.argparser])
        flags = parser.parse_args()

        self._user_credentials = tools.run_flow(flow, self._storage, flags)

    def get_service(self):
        http = httplib2.Http()
        http = self._user_credentials.authorize(http)
        service = build(self.API_SERVICE_NAME, self.API_VERSION, http=http)
        return service
    
    def get_album_list(self):
        if not self._user_credentials:
            logging.debug("Please login first and get user credentials.")
            return

        service = self.get_service()
        results = service.albums().list( # pylint: disable=no-member
            pageSize=10, fields="nextPageToken,albums(id,title)").execute()
        items = results.get('albums', [])
        if not items:
            print('No albums created by this app found.')
        else:
            print('Albums:')
            for item in items:
                print('{0} ({1})'.format(item['title'].encode('utf8'), item['id']))
    
    # this API explorer is critical: https://developers.google.com/apis-explorer/#p/discovery/v1/discovery.apis.getRest

    # here is what comes back:
    # the YouTube example was helpful: https://github.com/youtube/api-samples/blob/master/python/add_channel_section.py
    # {'id': 'ADrQQk66v4c7mlJ6On0KmITCHbqAStdoecai0iu7wTsn2h92_Sc35HSLFjRJ0RoB4JQPUDZ0OoC8',
    # 'title': 'this is a test',
    # 'productUrl': 'https://photos.google.com/lr/album/ADrQQk66v4c7mlJ6On0KmITCHbqAStdoecai0iu7wTsn2h92_Sc35HSLFjRJ0RoB4JQPUDZ0OoC8'}
    def create_album_in_library(self, title):
        # only need to provide title
        body = dict(album=dict(title=title))

        service = self.get_service() # service is discovery.Resource()
        results = service.albums().create(body=body).execute() # pylint: disable=no-member

        return results

    # copied from: https://github.com/youtube/api-samples/blob/master/python/upload_video.py
    # # This method implements an exponential backoff strategy to resume a failed upload.
    def _resumable_upload(self, request):
        response = None
        error = None
        retry = 0
        while response is None:
            try:
                logging.debug('Uploading file...')
                _, response = request.next_chunk()
                if response is not None:
                    if 'id' in response:
                        upload_token = response['id']
                        logging.debug('Video id "%s" was successfully uploaded.' % upload_token)
                        return upload_token
                    else:
                        exit('The upload failed with an unexpected response: %s' % response)
            except HttpError as e:
                if e.resp.status in self.RETRIABLE_STATUS_CODES:
                    error = 'A retriable HTTP error %d occurred:\n%s' % (e.resp.status,
                                                                        e.content)
                else:
                    raise
            except self.RETRIABLE_EXCEPTIONS as e:
                error = 'A retriable error occurred: %s' % e

            if error is not None:
                logging.error(error)
                retry += 1
                if retry > self.MAX_RETRIES:
                    exit('No longer attempting to retry.')

                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                logging.debug('Sleeping %f seconds and then retrying...' % sleep_seconds)
                time.sleep(sleep_seconds)

    # https://developers.google.com/photos/library/guides/upload-media
    # the Drive example was helpful: https://developers.google.com/drive/api/v3/manage-uploads
    def upload(self, filepath):
        name = os.path.basename(filepath)
        body = dict(name=name)
        media_body = MediaFileUpload(filepath, mimetype='image/jpeg')

        service = self.get_service()
        request = service.uploads().create( # pylint: disable=no-member
            body=body,
            media_body=media_body,
            fields='id').execute()
        
        upload_token = self._resumable_upload(request)
        return upload_token

    # https://developers.google.com/photos/library/reference/rest/v1/mediaItems/batchCreate
    # album_id should be string
    # media_items should be list of media_items objects: dict of description (if needed) and simpleMediaItem, which is just dict of uploadToken
    def attach_uploads_to_album(self, album_id, upload_tokens):
        new_media_items = dict()
        for upload_token in upload_tokens:
            #new_media_items['description'] = '' # I don't think we need this
            new_media_items['simpleMediaItem'] = dict(uploadToken=upload_token)
        body = dict(
            albumId=album_id, 
            newMediaItems=new_media_items) # not including position so will go at end
        
        service = self.get_service()
        results = service.mediaItems().batchCreate(body=body).execute() # pylint: disable=no-member
        # returns array of newMediaItemResults = dict(uploadToken, status, mediaItem)
        # where status is dict(code, message, details)
        logging.debug(results)

        # return value will have status we should keep an eye on

    # from StackOverflow - https://stackoverflow.com/questions/51746830/can-upload-photo-when-using-the-google-photos-api
    # I think discovery API is not returning the uploads() section of the API
    # Compare to https://developers.google.com/photos/library/guides/upload-media to ensure headers.
    def upload_alt(self, filepath):
        filename = os.path.basename(filepath)
        service = self.get_service()
        f = open(filepath, 'rb').read()

        url = 'https://photoslibrary.googleapis.com/v1/uploads'
        headers = {
            'Authorization': "Bearer " + service._http.request.credentials.access_token,
            'Content-type': 'application/octet-stream',
            'X-Goog-Upload-File-Name': filename,
            'X-Goog-Upload-Protocol': "raw",
        }

        response = requests.post(url, data=f, headers=headers)
        upload_token = response.text
        logging.debug('Upload token: %s' % upload_token)
        return upload_token

if __name__ == "__main__":
    gpc = GooglePhotosClient()
    gpc.login_from_commandline()
    gpc.create_album_in_library('this is a test')
