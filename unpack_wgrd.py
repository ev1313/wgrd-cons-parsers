#!/usr/bin/env python3

import pdb

import os
import sys
import argparse
import pathlib
import sys

def unpack_file(module, outpath, filepath):
    ret = os.system(f"python3 -m wgrd_cons_parsers.{module} -o '{outpath}' '{filepath}'")
    if ret != 0:
        print(f"failed at {filepath}")
        exit(ret)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("wgrd_path", type=pathlib.Path, help="path to the wgrd game files")
    parser.add_argument("output_path", type=pathlib.Path, help="unpack directory", nargs='?', default="./out/")

    args = parser.parse_args()

    for root, dirs, files in os.walk(args.wgrd_path):
        for file in files:
            if file.endswith(".dat"):
                filepath = os.path.join(root, file)
                outpath = os.path.join(args.output_path, os.path.relpath(filepath, args.wgrd_path))
                #print()
                #print(filepath)

                #os.system(f"python3 -m wgrd_cons_parsers.edat -o '{outpath}' '{filepath}'")

    # we do not need full recursion, because there're no dat files in dats except mpk
    for root, dirs, files in os.walk(args.output_path):
        for file in files:
            if file.endswith(".mpk"):
                filepath = os.path.join(root, file)
                outpath = os.path.dirname(filepath)
                #print(filepath)
                #print(outpath)

                #os.system(f"python3 -m wgrd_cons_parsers.edat -o '{outpath}' '{filepath}'")
    # here all files are already unpacked
    for root, dirs, files in os.walk(args.output_path):
        for file in files:
            filepath = os.path.join(root, file)
            outpath = os.path.dirname(filepath)
            if file.endswith(".ndfbin"):
                pass
            if file.endswith(".dic"):
                pass
            if file.endswith(".sformat"):
                unpack_file("sformat", outpath, filepath)
            if file.endswith(".ess"):
                unpack_file("ess", outpath, filepath)

