from github import Github
import os
import PySimpleGUI as sg
import requests
from config import Config

class Updater():
    def __init__(self, ver_num, config: Config):
        # the github class, used to get the data we need
        self.git = Github()

        self.config = config

        self.version_number = ver_num
    def check_for_update(self):
        try:
            # grabs the latest release and assets
            release = self.get_release()
            assets = self.get_assets(release)

            do_update = False
            check_update = False
            #checks for version difference, it can probably be done better but i havent figured out a way yet
            if release.tag_name[1:].split('.')[0] > self.version_number.split('.')[0]: 
                check_update = True
            elif release.tag_name[1:].split('.')[1] > self.version_number.split('.')[1]: 
                check_update = True
            elif release.tag_name[1:].split('.')[2] > self.version_number.split('.')[2]: 
                check_update = True
            else:
                return False
            # if an update was previously blocked, dont check
            if self.config.get_update_status() == False:
                check_update = False
                return True
            #check for update if there was a version difference and config 
            if check_update == True:
                do_update = self.show_update_prompt()

            if do_update == True:
                self.update(assets)

            if do_update == False:
                self.config.set_update(False)
            return True
        except:
            return False
        

    def update(self, assets):
            # if update is true, get the file data and write it to the zip file
            r = requests.get(assets.browser_download_url)
            open(f'temp.{assets.name.split(".")[1]}', 'wb').write(r.content)
            # run the updater exe and exit 
            os.startfile(os.path.join('resources', 'update.exe'))
            os._exit(0)

    def get_release(self):
        release = self.git.get_repo('jozz024/smash-amiibo-editor').get_latest_release()
        return release
        
    def get_assets(self, release):
        assets = release.get_assets()[0]
        return assets
        
    def show_update_prompt(self):
        # sets the window up
        window = sg.Window('Update', [[sg.Text('Would you like to update the program?')], [sg.Button('yes', key= 'YES', enable_events=True), sg.Button('no', key = "NO", enable_events=True)]])
        window.finalize()
        # opens the window
        event, values = window.read()
        #if yes is selected, return true
        if event == 'YES':
            return True
        elif event == 'NO':
            window.close()
            return False
        else:
            return False


# upd = Updater('0.0.1')
# upd.check_for_update()