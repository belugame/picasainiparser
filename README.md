# Picasa ini parser

A quickly put-together script that helps if you switch from organizing your photos in Picasa to another software like shotwell on Linux. Since Picasa does not write metadata like the star rating and album belonging to the file itself, the information is not visible to other software. pictureparser will recursively parse picasa.ini files in your photo collection and write the album and star metadata to the IPTC keywords field. Shotwell then recognizes and groups the photo like they were tagged.

__This was written and tested only on Ubuntu with Python 2.7. Please make a backup of your photos beforehand and use at own risk!__

PIP Dependencies:
  - [configparser](<https://pypi.python.org/pypi/configparser> )
  - [IPTCinfo](https://pypi.python.org/pypi/IPTCInfo/)

### Usage:

```sh
$ cp -r ~/Pictures ~/Pictures.bak  # make a backup of your photos
$ git clone https://github.com/belugame/picasainiparser.git
$ pip install iptcinfo configparser
$ cd picasainiparser
$ python pictureparser.py -vv ~/Pictures  # scans directory verbosely, outputs metadata found
$ python pictureparser.py ~/Pictures  --write # scans directory, writes metadata to photo files
```

