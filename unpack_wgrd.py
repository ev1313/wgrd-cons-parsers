#!/usr/bin/env python3

import pdb

import os
import sys
import argparse
import pathlib
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("wgrd_path", type=pathlib.Path, help="path to the wgrd game files")

    args = parser.parse_args()

    for root, dirs, files in os.walk(args.wgrd_path):
        for file in files:
            if file.endswith(".dat"):
                filepath = os.path.join(root, file)
                outpath = os.path.join("./out/", os.path.relpath(filepath, args.wgrd_path))
                print()
                print(filepath)

                os.system(f"python3 -m wgrd_cons_parsers.edat -o '{outpath}' '{filepath}'")
