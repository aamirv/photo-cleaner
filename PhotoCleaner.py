import datetime
import os
import re
import yaml
import pytz
from datetime import datetime
from PIL import Image
import piexif
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class PhotoCleaner:
  DEFAULT_ROOT = "/Users/aamir/Dropbox (Personal)/Photos"
  DEFAULT_TIME_ZONE = "US/Central"

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
      result = input("File [q]? ")
    
    if result.lower() == "q":
      result = None

    return result # will be either None to quit or valid string for file
  
  def ask_user_for_dir(self):
    result = ""
    while not os.path.isdir(result) and result.lower != "q":
      result = input("Directory (includes all subdirectories or q to quit)? ")
    
    if result.lower() ==  "q":
      result = None

    return result # will be either None to quit or valid string for dir

  def load_dir_to_skip(self):
    #try:
      # stream = file('settings.yaml', 'r')
      # data = yaml.load (stream)
      # and then later to print
      # stream = file('settings.yaml', 'w')
      # yaml.dump(data, stream)
      #yaml.load("""
      #directories_to_process:
      #processed_directories:
      #path_strings_to_skip:
      #""")
    # catch:
    #   pass
    # if a file exists then load it
    # else make it None
    self.dir_to_skip = None
  
  def create_dir_to_skip(self, ask_user=True):
    PATH_STRINGS_TO_SKIP = ["/Users/aamir/Dropbox (Personal)/Photos/Aamir Virani - 4048", "/Originals"]
    self.dir_to_skip = {}
    for dir_name, _, _ in os.walk(self.root):
      autoskip = any(s in dir_name for s in PATH_STRINGS_TO_SKIP)
      if autoskip:
        self.dir_to_skip[dir_name] = autoskip
      else:
        skip = True
        if ask_user:
          text = input('Skip {}? [n]'.format(dir_name))
          skip = 'Y' in text.upper()
        
        self.dir_to_skip[dir_name] = skip
  
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
  
  def process_directory(self, dir_name, new_date_time, new_location=None):
    dt_string = new_date_time.strftime("%Y:%m:%d %H:%M:%S")
    logging.debug("Processing dir {} with date {}".format(dir_name, dt_string))
    # TODO: update given user-based request
    #(folder_date, folder_location) = self.parse_directory_name(dir_name)
    #print(folder_date, folder_location)
    # get photo list from this directory
    # for each photo p
      # process_photo(p, d, l)

  # https://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/EXIF.html
  def process_photo(self, file_name, new_date_time, new_location=None):
    dt_string = new_date_time.strftime("%Y:%m:%d %H:%M:%S")
    logging.debug("Processing photo {} with date {}".format(file_name, dt_string))
    #image = Image.open(file_name)
    #exif_dict = piexif.load(image.info["exif"])
    #exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = dt_string
    ##FIXME: mess with location
    #exif_bytes = piexif.dump(exif_dict)
    #image.save(file_name, exif=exif_bytes)
    
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
