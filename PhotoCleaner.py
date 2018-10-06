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
