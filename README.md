This is a fun little project to edit the exif data in a set of photos.
It can also then upload to your Google Photos account.

Use python3.

    python3 PhotoCleanerController.py

Menu looks like this with related commands you can run:

    ## Welcome to PhotoCleaner!

    Menu:
    [1] Change created date for a photo
    [2] Change created date for all files in a directory
    [3] Walk directory and full process
    [4] Log into Google Photos
    [5] Upload directory to Google Photos
    [6] Logout of Google Photos
    [7] Full process a directory
    [q] Quit

The main one to use is `[7] - full process a directory`.

When you are asked to upload a directory, then, do not escape
characters, just type it out:

    Directory [q to quit]? /Users/aamir/Downloads/Aamir\ 0760\ JPEGs/Final\ Images/19750530\ Dilshad\ Trip/
    Please enter a valid directory.
    Directory [q to quit]? /Users/aamir/Downloads/Aamir 0760 JPEGs/Final Images/19750530 Dilshad Trip
    Use default value (1975-05-30 00:00:00)? [y]
    Create album in Google 19750530 Dilshad Trip? [y]
    Upload photos to Google? [y]
