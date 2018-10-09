import logging
import os
import re
from datetime import datetime

from PhotoCleaner import PhotoCleaner
from PhotoCleanerView import PhotoCleanerView, CleanerAction
from GooglePhotosClient import GooglePhotosClient

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class PhotoCleanerController:

    def __init__(self):
        self._view = PhotoCleanerView()
        self._model = PhotoCleaner()
        self._uploader = GooglePhotosClient()
    
    def perform_quit(self):
        logging.debug('Quitting...')
    
    def perform_process_photo(self):
        logging.debug('Processing photo.')
        fn = self._view.ask_user_for_file()
        if fn is None:
            return
        
        dt = self._view.ask_user_for_date()
        self._model.update_photo(fn, dt)

    def process_directory(self, dirpath):
        (default_dt, _) = self.parse_directory_name(dirpath)
        user_dt = self._view.ask_user_for_date(default_dt)
        self._model.update_directory(dirpath, user_dt)

    def perform_process_directory(self, dirpath=None):
        logging.debug('Processing directory.')
        if dirpath is None:
            dirpath = self._view.ask_user_for_dir()
        
        if dirpath is None:
            logging.debug('User canceled processing directory.')
            return
        
        self.process_directory(dirpath)
            
    def perform_walk_and_process_directory(self):
        logging.debug('Walking directory')
        user_dirpath = self._view.ask_user_for_dir()
        if user_dirpath is None: 
            logging.debug('User canceled walking directory.')
            return
        
        for (dirpath, _, _) in os.walk(user_dirpath):
            self.process_directory(dirpath)
    
    def perform_login(self):
        logging.debug('Logging into Google Photos...')
        self._uploader.login_from_commandline()
    
    def perform_logout(self):
        logging.debug('Logging out of Google Photos...')
        self._uploader.logout()

    def perform_upload(self, dirpath=None):
        if dirpath is None:
            dirpath = self._view.ask_user_for_dir()
        
        if dirpath is None:
            logging.debug('User canceled upload.')
            return
        
        dirname = dirpath.split(os.path.sep)[-1]
        album_id = self._uploader.create_album_in_library(dirname)
        logging.debug("Created {} in Google Photos: ID {}".format(dirname, album_id))

        upload_tokens = []
        filepaths = sorted(os.listdir(dirpath))
        for filepath in filepaths:
            upload_token = self._uploader.upload_alt(filepath)
            upload_tokens.append(upload_token)

        self._uploader.attach_uploads_to_album(album_id, upload_tokens)
  
    def start(self):
        self._view.show_welcome()
        done = False
        while not done:
            self._view.show_menu()
            action = self._view.ask_user_for_menu()
            if action == CleanerAction.Quit:
                self.perform_quit()
                done = True
            elif action == CleanerAction.ChangePhoto:
                self.perform_process_photo()
            elif action == CleanerAction.ChangePhotosInDirectory:
                self.perform_process_directory()
            elif action == CleanerAction.WalkDirectory:
                self.perform_walk_and_process_directory()
            elif action == CleanerAction.LoginForUpload:
                self.perform_login()
            elif action == CleanerAction.UploadDirectory:
                self.perform_upload()
            elif action == CleanerAction.Logout:
                self.perform_logout()

    def verify_year(self, dt):
        MIN_ALLOWED_YEAR = 1900
        MAX_ALLOWED_YEAR = 2050
        if dt.year < MIN_ALLOWED_YEAR or dt.year > MAX_ALLOWED_YEAR:
            raise ValueError("Unsupported year {}".format(dt.year))

    def parse_directory_name(self, dirpath):
        """
        Takes a given directory path and returns a tuple if it has a date and location in its name.

        If the directory path has no date information, None is returned.
        If it only has a partial (like just year or just year and month), that is all that's returned

        NOTE: this does not validate the directory path itself

        :returns (date_result, location_result): datetime and string suffix for location
        :raises ValueError: if the name is not returning a valid datetime or the year is out of range
        """
        date_result = None
        location_result = None
        dirname = dirpath.split(os.path.sep)[-1]
    
        time_match = re.search("[0-9x]{4,8}", dirname)
        if time_match:
            s = time_match.group(0)
            if len(s) == 4 and s.isdigit:
                date_result = datetime.strptime(time_match.group(0), "%Y")
            elif len(s) == 6 and s.isdigit:
                date_result = datetime.strptime(time_match.group(0), "%Y%m")
            elif len(s) == 8 and s.isdigit:
                date_result = datetime.strptime(time_match.group(0), "%Y%m%d")
            else:
                raise ValueError("Unsupported date format")
            
            self.verify_year(date_result)
    
            index_starting_descriptor = time_match.span()[0]+ time_match.span()[1]
            if index_starting_descriptor < len(dirname):
                location_result = dirname[index_starting_descriptor:].lstrip().rstrip()

        return (date_result, location_result)

if __name__ == "__main__":
    pcc = PhotoCleanerController()
    pcc.start()