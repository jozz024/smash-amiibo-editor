from zipfile import ZipFile
import os

#extracts the file into the cwd, which will be the main dir because its getting executed in main.exe
with ZipFile('temp.zip', 'r') as zip:
    zip.extractall()
#deletes the zip after extraction
os.remove('temp.zip')