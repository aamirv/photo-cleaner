from googleapiclient.discovery import build
from oauth2client import file, client, tools
from oauth2client.client import flow_from_clientsecrets
import httplib2

import argparse
from oauth2client import tools
from oauth2client.file import Storage
import logging

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
        # the below lint is okay - TODO figure out how to remove
        results = service.albums().list(
            pageSize=10, fields="nextPageToken,albums(id,title)").execute()
        items = results.get('albums', [])
        if not items:
            print('No albums created by this app found.')
        else:
            print('Albums:')
            for item in items:
                print('{0} ({1})'.format(item['title'].encode('utf8'), item['id']))
    
    def create_album_in_library(self, title):
        # only need to provide title

        # return
        album_id = None
        album_url = None
        return (album_id, album_url, title)
    
    def upload_photo_to_library(self):
        pass

if __name__ == "__main__":
    gpc = GooglePhotosClient()
    gpc.login_from_commandline()
    gpc.get_album_list()
