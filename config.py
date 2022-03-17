import os
import json


class Config:
    def __init__(self):
        """Initializes the config class.
        """
        config_path = os.path.join('resources', 'config.json')
        # open the config if it exists
        if os.path.isfile(config_path):
            with open(config_path) as config:
                self.config = json.load(config)
        else:
            # if config doesn't exist, create it and write brackets so it can be loaded by the json module
            with open(config_path, 'w') as config:
                config.write(config := '{}')
                self.config = json.loads(config)

        resourcepath = lambda x: os.path.join('resources', x)
        fileexists = lambda x: os.path.isfile(resourcepath(x))
        if self.read_keys() is None:
            if fileexists('unfixed-info.bin') and fileexists('locked-secret.bin'):
                self.write_key_paths(resourcepath('unfixed-info.bin'), resourcepath('locked-secret.bin'))
            elif fileexists('key_retail.bin'):
                self.write_key_paths(resourcepath('key_retail.bin'))

        if self.get_region_path() is None:
            if fileexists('regions.json'):
                self.write_region_path(resourcepath('regions.json'))
            elif fileexists('regions.txt'):
                self.write_region_path(resourcepath('regions.txt'))

        if self.get_update_status() is None:
            self.set_update(True)

        if self.get_color() is None:
            self.write_color('DarkBlue3')

    def write_key_paths(self, *key_paths):
        """Writes the key path(s) to the config file.

        Args:
            key_paths: One or more key paths for the config to write.
        """
        config = self.config
        # if there is more than one key path, parse into unfixed info and locked secret and remove key retail from config
        if len(key_paths) > 1:
            for path in key_paths:
                basename = os.path.basename(path)
                if basename == 'unfixed-info.bin':
                    config['unfixed-info'] = path
                elif basename == 'locked-secret.bin':
                    config['locked-secret'] = path

            config.pop('keys', None)
        elif key_paths:
            # if there isn't, do some assuming
            path = key_paths[0]
            basename = os.path.basename(path)
            if basename == 'key_retail.bin':
                config['keys'] = path
                config.pop('unfixed-info', None)
                config.pop('locked-secret', None)
            elif basename == 'unfixed-info.bin':
                config['unfixed-info'] = path
                config['locked-secret'] = os.path.join(os.path.dirname(path), 'locked-secret.bin')
                config.pop('keys', None)
            elif basename == 'locked-secret.bin':
                config['locked-secret'] = path
                config['unfixed-info'] = os.path.join(os.path.dirname(path), 'unfixed-info.bin')
                config.pop('keys', None)

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
        with open(os.path.join('resources', 'config.json'), 'w') as cfg:
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
