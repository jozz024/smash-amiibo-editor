# **Smash Amiibo Editor**

### *DISCLAIMER: Do not use edited amiibo in tournaments unless the TO explicitly allows them. Doing so can result in a permanent tournament ban.*

## [Click Here to Download](https://github.com/jozz024/smash-amiibo-editor/releases/latest/download/SmashAmiiboEditor.zip)

## Encryption Keys

Encryption/Decryption keys are needed to edit amiibo. Smash Amiibo Editor supports both key_retail.bin and locked-secret.bin + unfixed-info.bin. Either place them in the resources folder or select them upon program startup.
**You have to obtain the keys yourself, we will not provide them.**

## Regions

Smash Amiibo Editor uses a .json file compiled with the latest amiibo knowledge for your editing ease. We provide a regions file with the most up to date amiibo research.
If you would like to create a region json of your own (or append to the end of one), use [this tool](https://github.com/jozz024/sae-region-maker/releases/latest).

It also has backwards compatibility with [amiibox](https://github.com/fudgepop01/amiibox)'s regions.txt format, but it is strongly suggested to use the one we provide.

## Watermark

Smash Amiibo Editor comes with an amiibo watermark.
It only gets triggered when you edit training data sections, so if you're just trying to edit your spirits, make sure to not touch any of those.
To validate any amiibo edited by this application, use the [amiibo validator](https://fudgepop01.github.io/amiibox/)

## Templates

Templates are a new tool to assist in amiibo research. They can be used to apply pre-configured values to specific sections of a regions file. The provided templates are: max, min, and default. Max maximizes every value, min minimizes every value, and default sets every value to what is thought to be "default" values. You can also make your own templates!

## Mii

With release 1.6.0 of Smash Amiibo Editor, we now support registering amiibo, and dumping/loading your miis. To dump your mii, simply load an amiibo, go to the `Mii` tab, and hit `Dump Mii`. To change an amiibo's mii, load the amiibo, go to the `Mii` tab, click `Load Mii`, and select the previously dumped mii file.

## Amiibo Research Document

The region files included with the releases of Smash Amiibo Editor are heavily based on the data from [this document](https://docs.google.com/document/d/1L3c-QKr46ATTSxaicPHNFq5uW-uRytVViPRvdM93IQo/). DM `@MiDe#9934` / `mide.` on discord if you have any questions/comments/concerns about this project, or any new research to add.

## Credits
Developed by [MiDe](https://github.com/MiDe-S) and jozz.

Special thanks to untitled1991 and [Ske](https://twitter.com/floofstrid).

## Building

### Use Pyinstaller 5.13.2 to avoid false positive from Windows Defender
To build the application, you must have pyinstaller + the dependencies in requirements.txt installed.
1. `pyinstaller --onefile resources/update.py`
2. Move update.exe from dist to the resources folder
3. `pyinstaller main.spec`.
