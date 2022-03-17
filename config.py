import os
import json


class Config:
    def __init__(self):
        """Initializes the config class.
        """
        # opens the config if it exists
        if os.path.exists(os.path.join('resources', 'config.json')):
            with open(os.path.join('resources', 'config.json')) as config:
                self.config = json.load(config)
        else:
            # if config doesn't exist, create it and write brackets so it can be loaded by the json module
            with open(os.path.join('resources', 'config.json'), "w") as config:
                config.write(config := "{}")
                self.config = json.loads(config)

        if self.read_keys() is None:
            if os.path.exists(os.path.join('resources', 'unfixed-info.bin')) and os.path.exists(
                    os.path.join('resources', 'locked-secret.bin')):
                self.write_key_path(
                    (os.path.join('resources', 'unfixed-info.bin'), os.path.join('resources', 'locked-secret.bin')))
            elif os.path.exists(os.path.join('resources', 'key_retail.bin')):
                self.write_key_path((os.path.join('resources', 'key_retail.bin'), ))

        if self.get_region_path() is None:
            if os.path.exists(os.path.join('resources', 'regions.json')):
                self.write_region_path(os.path.join('resources', 'regions.json'))
            elif os.path.exists(os.path.join('resources', 'regions.txt')):
                self.write_region_path(os.path.join('resources', 'regions.txt'))

        if self.get_update_status() is None:
            self.set_update(True)

        if self.get_color() is None:
            self.write_color('DarkBlue3')

    def write_key_path(self, key_path: tuple):
        """Writes the key path(s) to the config file.

        Args:
            key_path (tuple): One or more key paths for the config to write.
        """
        # if there is more than one key path, parse into unfixed info and locked secret and remove key retail from config
        if len(key_path) != 1:
            for keys in key_path:
                if os.path.split(keys)[1] == 'unfixed-info.bin':
                    self.config['unfixed-info'] = keys
                if os.path.split(keys)[1] == 'locked-secret.bin':
                    self.config['locked-secret'] = keys

            if 'keys' in self.config:
                del self.config['keys']
        else:
            # if there isn't, do some assuming
            for keys in key_path:
                if os.path.split(keys)[1] == 'key_retail.bin':
                    self.config['keys'] = key_path[0]

                    if 'unfixed-info' in self.config:
                        del self.config['unfixed-info']
                    if 'locked-secret' in self.config:
                        del self.config['locked-secret']
                elif os.path.split(keys)[1] == 'unfixed-info.bin':
                    self.config['unfixed-info'] = keys
                    self.config['locked-secret'] = os.path.join(os.path.split(keys)[0],  'locked-secret.bin')
                    if 'keys' in self.config:
                        del self.config['keys']
                elif os.path.split(keys)[1] == 'locked-secret.bin':
                    self.config['locked-secret'] = keys
                    self.config['unfixed-info'] = os.path.join(os.path.split(keys)[0], 'unfixed-info.bin')
                    if 'keys' in self.config:
                        del self.config['keys']
    def read_keys(self):
        """Reads the key file path(s) from config.

        Returns:
            list: List of key files if found.
        """
        # if keys in config, return that path
        if 'keys' in self.config:
            return self.config['keys']
        # if keys isn't in config, check if the separated keys are there and return them if they are
        elif 'unfixed-info' in self.config and 'locked-secret' in self.config:
            return [self.config['unfixed-info'], self.config['locked-secret']]
        # if none of them are there, return none
        else:
            return None

    def write_region_path(self, region_path):
        """Writes the region path given to config.

        Args:
            region_path (str): Path to regions file.
        """
        # writes the given region path to regions
        self.config['regions'] = region_path

    def get_region_type(self):
        """Gets the region type from config.

        Returns:
            str: Region filetype.
        """
        # check if regions exist
        if 'regions' in self.config:
            # returns the path extension
            return self.config['regions'].split('.')[-1]
        else:
            # if no regions, return none
            return None

    def get_region_path(self):
        """Gets the region path from config.

        Returns:
            str: Region path.
        """
        # check if regions exist
        if 'regions' in self.config:
            # return region path
            return self.config['regions']
        else:
            # if no regions, return none
            return None

    def save_config(self):
        """Saves the configuration file.
        """
        # saves the config file
        with open(os.path.join('resources', 'config.json'), 'w+') as cfg:
            json.dump(self.config, cfg, indent=4)

    def set_update(self, truefalse: bool):
        """Sets the update prompt config.

        Args:
            truefalse (bool): Whether to set it to true or false.
        """
        # set update status to given bool
        self.config['prompt_update'] = truefalse

    def get_update_status(self):
        """_summary_

        Returns:
            bool: If the program should show the update prompt.
        """
        # check if updates are allowed
        if 'prompt_update' in self.config:
            return self.config['prompt_update']
        else:
            return None

    def write_color(self, color):
        """Writes the given color to config.

        Args:
            color (str): PSG Theme str.
        """
        # writes the theme given.
        self.config['theme'] = color

    def get_color(self):
        """Gets the color from config.

        Returns:
            str: PSG Theme Str
        """
        if 'theme' in self.config:
            return self.config['theme']
        else:
            return None
