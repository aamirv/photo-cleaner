import datetime
import imghdr
import logging
import os
from datetime import datetime

import piexif
from PIL import Image

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class PhotoCleaner:
    PATH_STRINGS_TO_SKIP = ["/Users/aamir/Dropbox (Personal)/Photos/Aamir Virani - 4048", "/Originals"]
    DEBUG_MODE = True

    def process_directory(self, dirpath, new_date_time):
        """
        Updates the JPEGs in a given directory with the given creation date.

        :param dirpath: directory to process - note this method is NOT recursive
        :param new_date_time: the date_time to update the images with
        :returns: None
        """
        autoskip = any(s in dirpath for s in self.PATH_STRINGS_TO_SKIP)
        if autoskip:
            logging.debug('Directory {} skipped - in default skip list.'.format(dirpath))
            return

        dt_string = new_date_time.strftime("%Y:%m:%d %H:%M:%S")
        logging.debug("Processing dir {} with date {}".format(dirpath, dt_string))

        filenames = os.listdir(dirpath)
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            filetype = imghdr.what(filepath)
            if filetype not in ['jpeg']:
                logging.debug('File {} skipped - filetype is {}.'.format(filepath, filetype))
                continue

            self.process_photo(filepath, new_date_time)

    def process_photo(self, filepath, new_date_time):
        """
        Updates the given JPEG with the given creation date.

        Useful link to review: https://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/EXIF.html

        :param filepath: file to process
        :param new_date_time: the date_time to update the image with
        :returns: None
        """
        filetype = imghdr.what(filepath)
        if filetype not in ['jpeg']:
            logging.error('Can only process JPEGs.')
            return

        dt_string = new_date_time.strftime("%Y:%m:%d %H:%M:%S")
        logging.debug("Processing photo {} with date {}".format(filepath, dt_string))

        if self.DEBUG_MODE:
            logging.debug('Not writing exif - debug mode.')
            return

        image = Image.open(filepath)
        exif_dict = piexif.load(image.info["exif"])
        exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = dt_string
        exif_bytes = piexif.dump(exif_dict)
        image.save(filepath, exif=exif_bytes)
