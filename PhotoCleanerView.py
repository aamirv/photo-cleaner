import logging
import os
from datetime import datetime

import pytz

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class PhotoCleanerView:
    DEFAULT_TIME_ZONE = "US/Central"
  
    def show_welcome(self):
        print("------------------------")
        print("Welcome to PhotoCleaner!")
        print("------------------------")

    def show_menu(self):
        print("""Menu:
        [1] Change created date for a photo
        [2] Change created date for all files in a directory
        [q] Quit
        """)
  
    def ask_user_for_menu(self):
        result = ""
        while result not in ['q', '1', '2']:
            result = input('? ').lower()
        return result
  
    def ask_user_for_date(self):
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
  
    def ask_user_for_file(self):
        result = ""
        while not os.path.isfile(result) and result.lower() != "q":
            result = input("File [q to quit]? ")
            if not os.path.isfile(result):
                print("Please enter a valid filename.")
    
        if result.lower() == "q":
            result = None

        return result # will be either None to quit or valid string for file
  
    def ask_user_for_dir(self):
        result = ""
        while not os.path.isdir(result) and result.lower != "q":
            result = input("Directory (includes all subdirectories or q to quit)? ")
            if not os.path.isdir(result):
                print("Please enter a valid directory.")
    
        if result.lower() ==  "q":
            result = None

        return result # will be either None to quit or valid string for dir
