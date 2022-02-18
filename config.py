import os
import json

class Config():
    def __init__(self):
        # opens the config if it exists
        if os.path.exists(os.path.join('resources', 'config.json')):
            with open(os.path.join('resources', 'config.json')) as config:
                self.config = json.load(config)
        else:
            # if config doesnt exist, create it and write brackets so it can be loaded by the json module
            open(os.path.join('resources', 'config.json'), 'w+').write('{}')
            with open(os.path.join('resources', 'config.json')) as config:
                self.config = json.load(config)

        if self.read_keys() is None:
            if os.path.exists(os.path.join('resources', 'unfixed-info.bin')) and os.path.exists(os.path.join('resources', 'locked-secret.bin')):
                self.write_key_path((os.path.join('resources', 'unfixed-info.bin'), os.path.join('resources', 'locked-secret.bin')))
            elif os.path.exists(os.path.join('resources', 'key_retail.bin')):
                self.write_key_path([os.path.join('resources', 'key_retail.bin')])

        if self.get_region_path() is None:
            if os.path.exists(os.path.join('resources', 'regions.json')):
                self.write_region_path(os.path.join('resources', 'regions.json'))
            elif os.path.exists(os.path.join('resources', 'regions.txt')):
                self.write_region_path(os.path.join('resources', 'regions.txt'))
        if self.get_update_status() is None:
            self.set_update(True)

    def write_key_path(self, key_path: tuple):
        #if there is more than one key path, parse into unfixed info and locked secret and remove key retail from config
        if len(key_path) != 1:
            for keys in key_path:
                if os.path.split(keys)[1] == 'unfixed-info.bin':
                    self.config['unfixed-info'] = keys
                if os.path.split(keys)[1] == 'locked-secret.bin':
                    self.config['locked-secret'] = keys

            if 'keys' in self.config:
                del self.config['keys']
        else:
            #if there isnt, write the only key under the assumption that it's key_retail and remove separated keys
            self.config['keys'] = key_path[0]

            if 'unfixed-info' in self.config:
                del self.config['unfixed-info']
            if 'locked-secret' in self.config:
                del self.config['locked-secret']

    def read_keys(self):
        #if keys in config, return that path
        if 'keys' in self.config:
            return self.config['keys']
        #if keys isnt in config, check if the separated keys are there and return them if they are
        elif 'unfixed-info' in self.config and 'locked-secret' in self.config:
            return [self.config['unfixed-info'], self.config['locked-secret']]
        #if none of them are there, return none
        else:
            return None

    def write_region_path(self, region_path):
        #writes the given region path to regions
        self.config['regions'] = region_path

    def get_region_type(self):
        #check if regions exist
        if 'regions' in self.config:
            #returns the path extension
            return self.config['regions'].split('.')[-1]
        else:
            #if no regions, return none
            return None

    def get_region_path(self):
        #check if regions exist
        if 'regions' in self.config:
            #return region path
            return self.config['regions']
        else:
            #if no regions, return none
            return None

    def save_config(self):
        #saves the config file
        with open(os.path.join('resources', 'config.json'), 'w+') as cfg:
            json.dump(self.config, cfg, indent = 4)

    def set_update(self, truefalse: bool):
        #set update status to given bool
        self.config['update'] = truefalse
        
    def get_update_status(self):
        #check if updates are allowed
        if 'update' in self.config:
            return self.config['update']
        else:
            return None
