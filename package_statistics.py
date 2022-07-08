#!/usr/bin/env python3
"""
This script outputs the top Debian packages that have most files associated with them, based
on the contents index available at http://ftp.uk.debian.org/debian/dists/stable/main/.
"""

__author__ = "Francisco Carrola"
__version__ = "1.0"

import argparse
import gzip
import os
from typing import Dict, List
import sys
import re
import requests

ARCH_CHOICES = [
    "amd64",
    "arm64",
    "armel",
    "armhf",
    "i386",
    "mips64el",
    "mipsel",
    "ppc64el",
    "s390x",
]
CONTENT_INDICE_MIRROR = "http://ftp.uk.debian.org/debian/dists/stable/main/"


def parse_arguments():
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "arch", nargs="?", choices=ARCH_CHOICES, default="amd64", help="Architecture"
    )

    return parser.parse_args()


class ContentIndice:
    """
    Class to hold the content inside contents index file.
    :param arch: architecture
    :type arch: str
    """

    FILE_NAME = "Contents-{}.gz"

    def __init__(self, arch: str) -> None:
        self.file_name = ContentIndice.FILE_NAME.format(arch)
        self.url = CONTENT_INDICE_MIRROR + self.file_name
        self.parsed_content: Dict[str, List[str]] = {}

    def get_file(self) -> None:
        """
        Method to get the contents index file.
        """
        # Check if file already exists. If so, delete it
        if os.path.exists(self.file_name):
            os.remove(self.file_name)
        # Download file
        file_content = requests.get(self.url, stream=True).content
        with open(self.file_name, "wb") as out_file:
            out_file.write(file_content)

    def parse_file(self) -> None:
        """
        Method to parse the contents index file and organize its content in a dictionary that
        holds all packages and the filenames associated with each of them.
        """
        with gzip.open(self.file_name, "rt") as file:
            lines = file.readlines()
            for line in lines:
                parsed_line = re.split(r"\s{1,}", line)
                packages_file = parsed_line[0]
                packages_list = parsed_line[1].split(",")
                # Iterate through all the packages that have a certain file
                for package in packages_list:
                    # If the package name key already exists, just append the filename
                    if package in self.parsed_content:
                        self.parsed_content[package].append(packages_file)
                    # If not, create a new key
                    else:
                        self.parsed_content[package] = [packages_file]

    def get_top_packages(self, number: int) -> None:
        """
        Method that retrieves the top packages with the most files associated with them.
        :param number: number of packages to show in the top list
        :type number: int
        """
        packages_list: List[str] = []
        occurrence_list: List[int] = []
        for key, value in self.parsed_content.items():
            # Populate auxiliary lists
            packages_list.append(key)
            occurrence_list.append(len(value))
        for i in range(number):
            # Get index of elements with most occurrences
            index = occurrence_list.index(max(occurrence_list))
            # Print the package info based on the index
            print(
                "{}. {} -> {}".format(
                    i + 1, packages_list[index], occurrence_list[index]
                )
            )
            # Remove elements from auxiliary lists
            occurrence_list.pop(index)
            packages_list.pop(index)


def main():
    """
    Entry point.
    """
    args = parse_arguments()

    try:
        content = ContentIndice(args.arch)

        content.get_file()
        content.parse_file()
        content.get_top_packages(10)

    except (IOError, ValueError) as err:
        print(err)
        sys.exit(1)


if __name__ == "__main__":
    main()
