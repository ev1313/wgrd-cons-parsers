# Wargame: Red Dragon Parsers

This is a collection of parsers for the gamefiles of the game "Wargame Red Dragon" by Eugen Systems.

They may or may not work for previous / future games in the series.

The parsers are written in Python 3.11 and use the [conshex](https://github.com/conshex/conshex) library for parsing the
gamefiles, a fork of the Construct library.

The parsers are not complete yet, if you encounter any issues, please open an issue on GitHub.

## Usage

``` sh
pip install wgrd_cons_parsers

# unpack gamefile
python -m wgrd_cons_parsers.edat NDF_Win.dat
# repack gamefile from the out/ directory
python -m wgrd_cons_parsers.edat -p out/NDF_Win.dat.xml
```

## Performance

It is recommended to use the pypy3 Python runtime, because it significantly increases the performance:

https://www.pypy.org/

## Development

If you want to change the scripts easily, you can install them locally:

``` sh
git clone https://github.com/ev1313/wgrd-cons-parsers.git
cd wgrd-cons-parsers
pip install -e .

# unpack gamefile
python -m wgrd_cons_parsers.edat NDF_Win.dat
# repack gamefile from the out/ directory
python -m wgrd_cons_parsers.edat -p out/NDF_Win.dat.xml
```

With this setup you can modify the scripts and still use them.

## Tests

For running the tests, a working Wargame Red Dragon installation is required.

Install the [wgrd-cons-tools](https://github.com/ev1313/wgrd-cons-tools) and run the unpacker on the gamefiles:

``` sh
python -m wgrd_cons_tools.unpack_wgrd <path-to-wargame-red-dragon> -o tests/files/
```

Then run the tests:

``` sh"
cd tests
pytest --pdb *.py
```
