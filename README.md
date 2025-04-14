# Icon Fixer for MTS Content Packs

A utility for fixing textures in add-ons for the Minecraft Transport Simulator (MTS) mod when transitioning from version 1.16.5 to 1.20.1.

This tool is based on the original script by [Jabobkrauskopf](https://github.com/JabobKrauskopf) with added GUI and additional functionality.

## What it fixes
1. Changes texture paths from `/textures/items/` to `/textures/item/` to match requirements of newer versions.
2. Creates necessary JSON files for proper texture display.
3. Optionally fixes the mods.toml file by removing letter characters from version numbers.

## Usage
1. Launch the program
2. Select the JAR file of the mod
3. If needed, check the "fix mods.toml" option
4. Click "Process"
5. The fixed file will be saved in the same folder with the "_fixed" suffix

## Important Notice
**This script is FOR PRIVATE USE ONLY and reuploading any converted packs is STRICTLY FORBIDDEN unless explicitly allowed by the respective pack author.**

## Building
To build the executable file, use PyInstaller:
```
pyinstaller "Icon Fixer for MTS Content Packs 1.16.5 to 1.20.1.spec"
```

## Requirements
- Python 3.6+
- tkinter
- tempfile
- pathlib
- zipfile
- re
- json 