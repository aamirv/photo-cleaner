import logging
import os
import re
from datetime import datetime

from PhotoCleaner import PhotoCleaner
from PhotoCleanerView import PhotoCleanerView

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class PhotoCleanerController:

    def __init__(self):
        self.view = PhotoCleanerView()
        self.model = PhotoCleaner()
  
    def start(self):
        self.view.show_welcome()
        done = False
        while not done:
            self.view.show_menu()
            action = self.view.ask_user_for_menu()
            if action == 'q':
                done = True
            elif action == '1': #photo
                logging.debug('Processing photo.')
                fn = self.view.ask_user_for_file()
                if fn is None:
                    continue
                
                dt = self.view.ask_user_for_date()
                self.model.process_photo(fn, dt)
            elif action == '2': #directory
                logging.debug('Processing directory.')
                dirname = self.view.ask_user_for_dir()
                if dirname is None:
                    continue
                
                (default_dt, _) = self.parse_directory_name(dirname)
                user_dt = self.view.ask_user_for_date(default_dt)
                self.model.process_directory(dirname, user_dt)

    def parse_directory_name(self, dirname):
        date_result = None
        location_result = None
        folder_name = dirname.split(os.path.sep)[-1]
    
        time_match = re.search("[0-9x]{4,8}", folder_name)
        if time_match:
            s = time_match.group(0)
            if len(s) == 4 and s.isdigit:
                date_result = datetime.strptime(time_match.group(0), "%Y")
            elif len(s) == 6 and s.isdigit:
                date_result = datetime.strptime(time_match.group(0), "%Y%m")
            elif len(s) == 8 and s.isdigit:
                date_result = datetime.strptime(time_match.group(0), "%Y%m%d")
            else:
                print("ERROR: unsupported date format")
    
            index_starting_descriptor = time_match.span()[0]+ time_match.span()[1]
            if index_starting_descriptor < len(folder_name):
                location_result = folder_name[index_starting_descriptor:].lstrip().rstrip()

        return (date_result, location_result)
