## Wargame EDat Files

### EDat Files

EDat files are the main container for any files in Eugen Games. To unpack an edat file, you can use the following command:

``` bash
python3 -m wgrd_cons_parsers.edat <Path to edat file> -o <output folder>
```

This will create a folder structure representing the one used by the game and a XML file with the following structure:

``` xml
<EDat sectorSize="8192">
  <File path="pc\ndf\nonpatchable\clusterbootstrapgame.ndfbin" />
  <File path="pc\ndf\nonpatchable\clusterbootstrapgameimpl.ndfbin" />
  <File path="pc\ndf\nonpatchable\clusterbootstraplaunchallmap.ndfbin" />
  <File path="pc\ndf\nonpatchable\clusterinitialisationnonpatchable.ndfbin" />
  <File path="pc\ndf\nonpatchable\clustermaingamerun.ndfbin" />
  <File path="pc\ndf\nonpatchable\clustermainlaunchallmap.ndfbin" />
  <File path="pc\ndf\nonpatchable\clusteroptions.ndfbin" />
  <File path="pc\ndf\nonpatchable\clusterrunallgamemaploop_step2.ndfbin" />
  <File path="pc\ndf\nonpatchable\clusterversionoptions.ndfbin" />
	...
```

You can add new files by adding a new `<File>` tag to the XML file and then repacking the EDat file with the following command:

``` xml
<EDat sectorSize="8192">
	...
  <File path="pc\test\test.ndfbin" />
</EDat>
```

``` bash
python3 -m wgrd_cons_parsers.edat -p <Path to XML file> -o <output folder>
```

### Directory Structure

The directory structure of Wargame is as follows:

- Data/
    - PC/
        - PC contains older revisions of the WarGame3.exe for replays every folderid marks a svn revision number of Eugens SVN
        - 48574/ 
        - 49125/
        - 49964/
        - 58710/
        - 59095/
        - 59638/
        - 68335/ 
    - WarGame/PC/
        - 48574/
             - every folder contains a folder with the next svn revision number
             - The files contained here get also loaded, the foldersr in the main dir only contain a NDF_Win.dat
             - 49125/
             - Data.dat - fonts and videos
             - DataMap.dat - maps and campaigns
             - NDF_NotFinal.dat - ndf files for scenarios?
             - NDF_Win.dat - ndf files for ui / scenery / everything
             - ZZ_1.dat - assets, texture ndfbins, ppk files, spk files
             - ZZ_2.dat - textures
             - ZZ_3a.dat - textures
             - ZZ_3b.dat - textures
             - ZZ_4.dat - some ppk files
        - 49125/

        - 49964/58710
	     - Where latest ZZ files are except ZZ_1
        - 58710/

        - 59095/
        - 59638/
        - 68335/
        - 72352/
             - Current latest folder for NDF_Win.dat

- Maps/Wargame/PC/
    - for each map / campaign one dat file

### Wargame3.exe

Every Wargame3.exe has a SVN Revision encoded in it. The current game version for example has this at 
position 0x0151FE18.

If you change the revision number with a hexeditor to for example 80000, it is possible to create a new
version of the game. For this you need to copy the following files:

- create a new folder Data/PC/80000
- copy atimgpud.dll, steam_api.dll and Wargame3.exe (unmodified!) to Data/PC/80000
    - this is for running vanilla replays - new replays get the new revision number attached to them
- create a new folder Data/WARGAME/72352/80000
- copy all files from Data/WARGAME/68335/72352 to Data/WARGAME/72352/80000
- create a new folder Data/WARGAME/80000
- copy NDF_Win.dat from Data/WARGAME/72352 to Data/WARGAME/80000

Now you can mod your files in the 72352/80000 or 80000 folders and the game will load them correctly.

