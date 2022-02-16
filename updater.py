from github import Github
from main import version_number
import PySimpleGUI as sg
import requests
from zipfile import ZipFile

class Updater():
    def init(self):
        self.git = Github()
    def check_for_update(self):
        release = self.git.get_repo('jozz024/smash-amiibo-editor').get_latest_release()
        assets = release.get_assets()[0]
        upd = False
        if release.tag_name[1:].split('.')[0] > version_number.split('.')[0]: 
            upd = self.show_update_prompt()
        if release.tag_name[1:].split('.')[1] > version_number.split('.')[1]: 
            upd = self.show_update_prompt()
        if release.tag_name[1:].split('.')[2] > version_number.split('.')[2]: 
            upd = self.show_update_prompt()
        
        if upd == True:
            r = requests.get(assets.browser_download_url)
            zip = open(f'temp.{assets.name.split(".")[1]}', 'wb').write(r.content)
            



    def show_update_prompt(self):
        window = sg.Window('Update', [[sg.Text('Would you like to update the program?')], [sg.Button('yes', key= 'YES', enable_events=True), sg.Button('no', key = "NO", enable_events=True)]])
        window.finalize()
        event, values = window.read()
        if event == 'YES':
            return True
        else:
            return False


upd = Updater()
upd.check_for_update()