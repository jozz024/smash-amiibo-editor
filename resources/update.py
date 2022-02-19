from zipfile import ZipFile
import os
import copy
import json

config_file = False
template_file = False
if os.path.exists(os.path.join('resources', 'config.json')):
    config_file = True
    config = open(os.path.join('resources', 'config.json'))
    config_ = json.loads(config.read())
    config_ = copy.deepcopy(config_)
    config.close()
if os.path.exists(os.path.join('resources', 'templates.json')):
    template_file = True
    templates = open(os.path.join('resources', 'templates.json'))
    templates_ = copy.deepcopy(templates)
    templates.close()
#extracts the file into the cwd, which will be the main dir because its getting executed in main.exe
with ZipFile('temp.zip', 'r') as zip:
    zip.extractall()

if config_file == True:
    with open(os.path.join('resources', 'config.json'), 'w+') as config:
        #set updates to true and write config to file
        config_['prompt_update'] = True
        json.dump(config_, config)

if template_file == True:
    with open(os.path.join('resources', 'templates.json'), 'w+') as templates:
        templates.write(templates_)

#deletes the zip after extraction
os.remove('temp.zip')
#starts the program again
os.startfile('SmashAmiiboEditor.exe')