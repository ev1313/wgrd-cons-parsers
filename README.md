# Wargame Red Dragon Parsers

This is a collection of parsers for the gamefiles of the game "Wargame Red Dragon" by Eugen Systems.

They may or may not work for previous / future games in the series.

The parsers are written in Python 3.11 and use the [dingsda](https://github.com/ev1313/dingsda) library for parsing the
gamefiles, a fork of the Construct library.

The parsers are not complete yet, if you encounter any issues, please open an issue on GitHub.

## Usage

``` sh
pip install -r requirements.txt
pip install wgrd_cons_parser

# unpack gamefile
python -m wgrd_cons_parser.edat NDF_Win.dat
# repack gamefile from the out/ directory
python -m wgrd_cons_parser.edat -p out/NDF_Win.dat.xml
```

## Performance

Currently unpacking the everything.ndfbin uses about 14 GB of RAM and takes about 2 minutes on my machine.

It is recommended to use the pypy3 Python runtime, because it significantly increases the performance:

https://www.pypy.org/

