import os
import re
from datetime import datetime

class PhotoCleaner:

  def __init__(self, root="/Users/aamir/Dropbox (Personal)/Photos"):
    if root is None:
      pass # should quit and say not allowed

    # if root is not legal directory should quit

    self.root = root
    self.dir_to_skip = None
  
  def load_dir_to_skip(self):
    # if a file exists then load it
    # else make it None
    self.dir_to_skip = None
  
  def create_dir_to_skip(self, ask_user=True):
    self.dir_to_skip = {}
    for dir_name, _, _ in os.walk(self.root):
      if dir_name.startswith("/Users/aamir/Dropbox (Personal)/Photos/Aamir Virani - 4048"):
        self.dir_to_skip[dir_name] = True
      if "Originals" in dir_name:
        self.dir_to_skip[dir_name] = True
      else:
        skip = True
        if ask_user:
          text = input('Skip {}? [n]'.format(dir_name))
          skip = 'y' in text or 'Y' in text
        
        self.dir_to_skip[dir_name] = skip
  
  def start(self):
    self.load_dir_to_skip()
    if self.dir_to_skip is None:
      self.create_dir_to_skip()

    for k,v in self.dir_to_skip.items():
      if v:
        print('skipping {}'.format(k))
      else:
        process_directory(k)
  
def process_directory(dir_name):
  (folder_date, folder_location) = parse_directory_name(dir_name)
  print(folder_date, folder_location)
  # get photo list from this directory
  # for each photo p
    # process_photo(p, d, l)

def process_photo(file_name):
  pass
  # parse createddate from exif
  # parse takendate from exif
  # parse location from exif
  # update createddate for file using exif (i.e., return to old value)
  # update takendate for exif from file
  # if location does not exist or is default value
    # update location for exif from user
  
def parse_directory_name(dir_name):
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