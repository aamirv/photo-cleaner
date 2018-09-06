import os
import re
from datetime import datetime

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

  return (date_result, location_result)

  # location_string
  # l = convert to gps_coordinates?
  # return (d, l)

rootDir = ("/Users/aamir/Dropbox (Personal)/Photos")
for dirName, subdirList, fileList in os.walk(rootDir):
  if dirName.startswith("/Users/aamir/Dropbox (Personal)/Photos/Aamir Virani - 4048") or "Originals" in dirName:
    continue
  
  (folder_date, folder_location) = parse_directory_name(dirName)

## process_directory(dir)
  # (default_date, default_location) = parse_directory_name(dir)
  # for each photo p
    # process_photo(p, d, l)

## process_photo(file)
    # parse createddate from exif
    # parse takendate from exif
    # parse location from exif
    # update createddate for file using exif (i.e., return to old value)
    # update takendate for exif from file
    # if location does not exist or is default value
      # update location for exif from user
