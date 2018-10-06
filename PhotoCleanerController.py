import logging

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
            menu = self.view.ask_user_for_menu()
            if menu == 'q':
                done = True
            elif menu == '1': #photo
                logging.debug('Processing photo.')
                fn = self.view.ask_user_for_file()
                if fn is None:
                    continue
                
                dt = self.view.ask_user_for_date()
                self.model.process_photo(fn, dt)
            elif menu == '2': #directory
                logging.debug('Processing directory.')
                dn = self.view.ask_user_for_dir()
                if dn is None:
                    continue
                
                dt = self.view.ask_user_for_date()
                self.model.process_directory(dn, dt)
