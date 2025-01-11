from github import Github
import os
import FreeSimpleGUI as sg
import requests
from .config import Config
import sys
import shutil
class Updater():
    def __init__(self, ver_num: str, config: Config):
        """Initializes the updater class.

        Args:
            ver_num (str): The version number of the program.
            config (Config): The config object.
        """
        # the github class, used to get the data we need
        self.git = Github()

        self.config = config

        self.version_number = ver_num
    def check_for_update(self):
        """Checks for an update in the program.

        Returns:
            bool: Whether or not there is an update available.
        """
        try:
            # grabs the latest release and assets
            release = self.get_release()
            assets = self.get_assets(release)

            do_update = False
            check_update = False
            # checks for version difference
            if release.tag_name.split('.') > self.version_number.split('.'):
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
        """Updates the program.

        Args:
            assets (assets): The assets object to download from
        """
        # if update is true, get the file data and write it to the zip file
        r = requests.get(assets.browser_download_url)
        open(f'temp.{assets.name.split(".")[1]}', 'wb').write(r.content)
        # run the updater exe and exit
        base_path = sys._MEIPASS
        shutil.copy(os.path.join(base_path, "resources", 'update.exe'), "update.exe")
        os.startfile("update.exe")
        os._exit(0)

    def get_release(self):
        """Gets the latest release of the program.

        Returns:
            release: The latest release of the program.
        """
        release = self.git.get_repo('jozz024/smash-amiibo-editor').get_latest_release()
        return release

    def get_assets(self, release):
        """Gets the assets from the given release.

        Args:
            release: The release to get the assets from.

        Returns:
            assets: The assets object.
        """
        assets = release.get_assets()[0]
        return assets

    def show_update_prompt(self):
        """Shows the update prompt of the program.

        Returns:
            bool: If they said yes or no to the update.
        """
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