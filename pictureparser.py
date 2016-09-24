"""Class for parsing picasa ini files to IPTC metadata in photo files."""
import argparse
import fnmatch
import logging
import os
import pprint

import configparser
from iptcinfo import IPTCInfo

log = logging.getLogger()


class PicasaToIPTC(object):

    """
    Parse picasa.ini photo information to IPTC metadata.

    Recursively reads picasa.ini files and writes album belonging and star
    rating to IPTC of given file.
    """

    valid_extensions = ("jpg", "jpeg", "raw", "rw2")
    mandatory_album_keys = set(("name", "token"))
    ini_name = ".picasa.ini"
    albums = {}
    photos = {}
    ini = None

    def __init__(self, write=False):
        """Store write or read-only mode."""
        self.write = write

    def parse_folder(self, folder):
        """Parse picasa info recursively and write to photo files."""
        log.info("Scanning folder: %s", folder)
        files = self.scan_folder_for_inis(folder)
        log.info("Found %s ini files", len(files))

        for ini in files:
            log.info("Parsing file: %s", ini)
            self.ini = ini
            self.parse_ini(ini)

        printer = pprint.PrettyPrinter(indent=2)
        printer.pprint(self.albums)
        printer.pprint(self.photos)
        if self.write:
            self.write_info()

    def scan_folder_for_inis(self, folder):
        """Return array of all picasa info files in given directory."""
        files = []
        for root, _dirs, filenames in os.walk(folder):
            for filename in fnmatch.filter(filenames, self.ini_name):
                files.append(os.path.join(root, filename))
        return files

    def parse_ini(self, ini):
        """Parse picasa ini metadata to dictionary."""
        config = configparser.ConfigParser()
        config.read_file(open(ini))
        self.get_albums(config)

        for name, section in config.iteritems():
            _, ext = os.path.splitext(name.lower())
            if ext:
                if ext[1:] in self.valid_extensions:
                    self.parse_photo(name, section)
                else:
                    log.warning("Ignore unknown format: %s", name)

    def get_albums(self, config):
        """Parse all album names of single ini."""
        for name, section in [i for i in config.iteritems() if
                              i[0].startswith(".album:")]:
            self.parse_album(section)
            config.remove_section(name)

    def parse_album(self, section):
        """Store album name by its unique token."""
        if not self.mandatory_album_keys.issubset(set(section.keys())):
            log.debug("Ignore album uid without mandatory info:"
                      " %s", section.keys())
            return
        token = section["token"]
        if token in self.albums.keys():
            assert self.albums.get(token) == section["name"], \
                "Conflicting album name for uid {}".format(token)
        self.albums[section["token"]] = section["name"]

    def parse_photo(self, name, section):
        """Store photo star rating and album belonging."""
        filename = os.path.join(os.path.dirname(self.ini), name)
        if not os.path.isfile(filename):
            log.info("File does not exist: %s", filename)
            return
        assert filename not in self.photos.keys(), \
            "Duplicate metadata for {}".format(filename)

        for key, value in section.iteritems():
            if key == "albums":
                for uid in value.split(","):
                    album = self.albums.get(uid)
                    if album:
                        photo = self.photos.setdefault(filename, {})
                        photo.setdefault("albums", []).append(album)
            elif key == "star":
                self.photos.setdefault(filename, {})["star"] = True
                self.photos[filename].setdefault("albums", []).append("star")

    def write_info(self):
        """Write picasa album names and star rating to photo's IPTC keywords."""
        for photo, info in self.photos.items():
            photo = IPTCInfo(photo, force=True)
            if "albums" in info:
                photo.keywords = list(set(photo.keywords + info["albums"]))
            print "Write: {}".format(photo.keywords)
            photo.save()


def main():
    """Run parser with CLI arguments."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('folder', default=".", nargs="?")
    parser.add_argument('--verbose', '-v', action='count', default=0)
    parser.add_argument('--write', '-w', action='store_true')
    args = parser.parse_args()

    verbosity = args.verbose > 2 and 2 or args.verbose
    level = [logging.WARNING, logging.INFO, logging.DEBUG][verbosity]
    logging.basicConfig(format='%(levelname)s: %(message)s', level=level)
    PicasaToIPTC(write=args.write).parse_folder(args.folder)

if __name__ == "__main__":
    main()
