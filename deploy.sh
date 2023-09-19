#!/usr/bin/env sh

VERSION=$(rg -o 'version = "([^"]*)"' -r '$1' pyproject.toml) 
WINDOWS_PATH="wgrd-cons-parsers-${VERSION}-windows.zip"
LINUX_PATH="wgrd-cons-parsers-${VERSION}-linux.zip"

mkdir -p out
cd out/
gh run list -L 1 | cut -f 7 | xargs -n 1 gh run download

mkdir -p windows
mv artifact/*.exe windows/
mkdir -p linux
mv artifact/* linux/

zip -r ${WINDOWS_PATH} windows/
zip -r ${LINUX_PATH} linux/

gh release create $(rg -o 'version = "([^"]*)"' -r '$1' ../pyproject.toml) -F RELEASE.md "${WINDOWS_PATH}#Windows Binaries" "${LINUX_PATH}#Linux Binaries"

