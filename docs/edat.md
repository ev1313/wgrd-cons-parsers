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

### Other filetypes

There are a couple of other filetypes also using the edat file format:
 - mpk (containing the sformat files for sound)
 - ppk (only *some* of the, containing tgv files for textures)

