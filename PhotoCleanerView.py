import logging
import os
from datetime import datetime

import pytz

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class CleanerAction:
    Quit = 'q'
    ChangePhoto = '1'
    ChangePhotosInDirectory = '2'
    WalkDirectory = '3'
    LoginForUpload = '4'
    UploadDirectory = '5'

class PhotoCleanerView:
    DEFAULT_TIME_ZONE = "US/Central"
  
    def show_welcome(self):
        print("------------------------")
        print("Welcome to PhotoCleaner!")
        print("------------------------")

    def show_menu(self):
        print("Menu:")
        print("[{}] Change created date for a photo".format(CleanerAction.ChangePhoto))
        print("[{}] Change created date for all files in a directory".format(CleanerAction.ChangePhotosInDirectory))
        print("[{}] Walk directory and change dates".format(CleanerAction.WalkDirectory))
        print("[{}] Log into Google Photos".format(CleanerAction.LoginForUpload))
        print("[{}] Upload directory to Google Photos".format(CleanerAction.UploadDirectory))
        print("[{}] Quit".format(CleanerAction.Quit))

    def ask_user_for_menu(self):
        """ Asks user to choose a valid menu option. """
        result = ""
        while result not in [CleanerAction.Quit,
                             CleanerAction.ChangePhoto,
                             CleanerAction.ChangePhotosInDirectory,
                             CleanerAction.WalkDirectory,
                             CleanerAction.LoginForUpload,
                             CleanerAction.UploadDirectory]:
            result = input('? ').lower()
        return result
  
    def ask_user_for_date(self, default_dt=None):
        """
        Asks user for date and returns it.  If you pass a default value, it will
        ask user if it should be used.

        :param default_dt: default datetime to use if user says so
        :returns: datetime
        """
        if default_dt:
            is_using_default = input('Use default value ({})? [y]'.format(default_dt))
            if is_using_default.lower() in ['y', '']:
                return default_dt

        done = False
        result = None
        while not done:
            year_str = input("Year? ")
            month_str = input("Month? ")
            day_str = input("Day? ")
            timezone_str = input("Timezone [{}] ?".format(self.DEFAULT_TIME_ZONE))
            try:
                year = int(year_str)
                month = int(month_str)
                day = int(day_str)
                tz = pytz.timezone(self.DEFAULT_TIME_ZONE)
                if not timezone_str or len(timezone_str) == 0:
                    timezone_str = self.DEFAULT_TIME_ZONE
                else:
                    tz = pytz.timezone(timezone_str)
                    result = datetime(year, month, day, tzinfo=tz)
                    done = True
            except ValueError:
                print("Please enter valid numbers.")
            except pytz.UnknownTimeZoneError:
                print("Unrecognized time zone.")

        return result

    def __ask_user_for_valid_X(self, descriptor, validating_method):
        result = ""
        while not validating_method(result) and result.lower() != "q":
            result = input("{} [q to quit]? ".format(descriptor.capitalize()))
            if not validating_method(result):
                print("Please enter a valid {}.".format(descriptor))
    
        if result.lower() == "q":
            result = None

        return result

    def ask_user_for_file(self):
        """
        Asks user for filename, and returns validated filename or None if user cancels.

        :returns: None
        """
        return self.__ask_user_for_valid_X("filename", os.path.isfile)
  
    def ask_user_for_dir(self):
        """
        Asks user for directory, and returns validated directory or None if user cancels.

        :returns: None
        """
        return self.__ask_user_for_valid_X("directory", os.path.isdir)
