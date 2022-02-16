from zipfile import ZipFile
import os
import copy

config_file = False
template_file = False
if os.path.exists('resources/config.json'):
    config_file = True
    config = open('resources/config.json')
    config_ = copy.deepcopy(config)
    config.close()
if os.path.exists('resources/templates.json'):
    template_file = True
    templates = open('resources/config.json')
    templates_ = copy.deepcopy(templates)
    templates.close()
#extracts the file into the cwd, which will be the main dir because its getting executed in main.exe
with ZipFile('temp.zip', 'r') as zip:
    zip.extractall()

if config_file == True:
    with open('resources/config.json', 'w+') as config:
        config.write(config_)

if template_file == True:
    with open('resources/templates.json', 'w+') as templates:
        templates.write(templates_)

#deletes the zip after extraction
os.remove('temp.zip')
#starts the program again
os.startfile('SmashAmiiboEditor.exe')