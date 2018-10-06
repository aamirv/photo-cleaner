import datetime
import os
import re
import yaml
import pytz
from datetime import datetime
from PIL import Image
import piexif
import logging
import imghdr

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class PhotoCleaner:
  DEFAULT_ROOT = "/Users/aamir/Dropbox (Personal)/Photos"
  DEFAULT_TIME_ZONE = "US/Central"
  PATH_STRINGS_TO_SKIP = ["/Users/aamir/Dropbox (Personal)/Photos/Aamir Virani - 4048", "/Originals"]
  DEBUG_MODE = True

  def __init__(self, root=DEFAULT_ROOT):
    # if root is not legal directory should quit
    if not os.path.isdir(root):
      raise NotADirectoryError

    self.root = root
    self.dir_to_skip = None
  
  def show_welcome(self):
    print("Welcome to PhotoCleaner!")

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
  
  def start(self):
    self.show_welcome()
    done = False
    while not done:
      self.show_menu()
      menu = self.ask_user_for_menu()
      if menu == 'q':
        done = True
      elif menu == '1': #photo
        logging.debug('Processing photo.')
        fn = self.ask_user_for_file()
        if fn is None:
          continue
        dt = self.ask_user_for_date()
        self.process_photo(fn, dt)
      elif menu == '2': #directory
        logging.debug('Processing directory.')
        dn = self.ask_user_for_dir()
        if dn is None:
          continue
        dt = self.ask_user_for_date()
        self.process_directory(dn, dt)
  
  def process_directory(self, root, new_date_time):
    dt_string = new_date_time.strftime("%Y:%m:%d %H:%M:%S")
    for (dirpath, _, filenames) in os.walk(root):
      autoskip = any(s in dirpath for s in self.PATH_STRINGS_TO_SKIP)
      if autoskip:
        logging.debug('Directory {} skipped - in default skip list.'.format(dirpath))
        continue

      text = input('Process directory {} [n, q to stop]? '.format(dirpath))
      if text.lower() != 'y':
        if text.lower() == 'q':
          logging.debug('Process directory stopping - user said so.')
          return
          
        logging.debug('Directory {} skipped - user said so.'.format(dirpath))
        continue

      logging.debug("Processing dir {} with date {}".format(dirpath, dt_string))
      for filename in filenames:
        filepath = os.path.join(dirpath, filename)
        filetype = imghdr.what(filepath)
        if filetype not in ['jpeg']:
          logging.debug('File {} skipped - filetype is {}.'.format(filepath, filetype))
          continue

        self.process_photo(filepath, new_date_time)

  # https://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/EXIF.html
  def process_photo(self, file_name, new_date_time):
    dt_string = new_date_time.strftime("%Y:%m:%d %H:%M:%S")
    logging.debug("Processing photo {} with date {}".format(file_name, dt_string))

    if self.DEBUG_MODE:
      logging.debug('Not writing exif - debug mode.')
      return

    image = Image.open(file_name)
    exif_dict = piexif.load(image.info["exif"])
    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = dt_string
    #FIXME: mess with location
    exif_bytes = piexif.dump(exif_dict)
    image.save(file_name, exif=exif_bytes)
    
  def parse_directory_name(self, dir_name):
    date_result = None
    location_result = None
    folder_name = dir_name.split(os.path.sep)[-1]
    
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
        # l = convert to gps_coordinates?

    return (date_result, location_result)

if __name__ == "__main__":
  pc = PhotoCleaner()
  pc.start()
