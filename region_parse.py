import PySimpleGUI as sg
from virtual_amiibo_file import VirtualAmiiboFile

def load_from_txt(file_path):
    """
    Loads sections from regions.txt

    :param file_path: file path to regions.txt
    :return: list of sections
    """
    sections = []
    with open(file_path, 'r') as fp:
        region_file = fp.read()
        region_file = region_file.split("\n\n")
    for region in region_file:
        parts = region.split('\n')
        section_type = parts[0].split(':')
        if section_type[1].strip() == "ABILITY":
            options = load_ability_file()
            section = ENUM(parts[1], 16, section_type[0], parts[-1], options, 0)

        elif section_type[1].strip() == "ENUM":
            # bit length is calculated by byte end - byte start * 8
            if 'b' in parts[2] or 'b' in parts[1]:
                end_loc = parts[2].split('b')
                start_loc = parts[1].split('b')
                # bit end + 8 - bit start + byte end - byte start - 1
                # -1 is to account for byte included with bits
                bit_length = int(end_loc[1]) + 8 - int(start_loc[1]) + 8*(int(end_loc[0], 16) - int(start_loc[0], 16)) - 8

                # for initializing class
                start_location = start_loc[0]
                bit_start_location = start_loc[1]
            else:
                bit_length = 8*(int(parts[2], 16) - int(parts[1], 16))

                # for initializing class
                start_location = parts[1]
                bit_start_location = 0

            options = {}
            options_found = False
            for line in parts:
                # before so '{' line isn't included
                if line == "}":
                    options_found = False
                if options_found:
                    option = line.split(':')
                    if 'b' in option[1]:
                        value = int(option[1], 2)
                    else:
                        value = int(option[1])
                    options[option[0].strip()] = value
                # after so '{' line isn't included
                if line == '{':
                    options_found = True

            section = ENUM(start_location, bit_length, section_type[0], parts[-1], options, bit_start_location)

        elif section_type[1].strip() == "u8":
            section = unsigned(int(parts[1], 16), 8, section_type[0], parts[-1])

        elif section_type[1].strip() == "u16":
            section = unsigned(int(parts[1], 16), 16, section_type[0], parts[-1])

        elif section_type[1].strip() == "i8":
            section = signed(int(parts[1], 16), 8, section_type[0], parts[-1])

        elif section_type[1].strip() == "i16":
            section = signed(int(parts[1], 16), 16, section_type[0], parts[-1])

        elif section_type[1].strip() == "bits":
            if 'b' in parts[2] or 'b' in parts[1]:
                end_loc = parts[2].split('b')
                start_loc = parts[1].split('b')
                # bit end + 8 - bit start + byte end - byte start - 1
                # -1 is to account for byte included with bits
                bit_length = int(end_loc[1]) + 8 - int(start_loc[1]) + 8 * (
                            int(end_loc[0], 16) - int(start_loc[0], 16)) - 8

                # for initializing class
                start_location = start_loc[0]
                bit_start_location = start_loc[1]
            else:
                bit_length = 8 * (int(parts[2], 16) - int(parts[1], 16))

                # for initializing class
                start_location = parts[1]
                bit_start_location = 0

            section = bits(start_location, bit_length, section_type[0], parts[-1], bit_start_location)

        else:
            pass
        if section is not None:
            sections.append(section)
    return sections

def load_ability_file():
    with open('resources/abilities.txt') as abilities:
        current_ability = 0
        spirit_dict = {}
        for lines in abilities.readlines():
            spirit_dict[lines.replace('â†‘', 'Up ').replace('â†“', 'Down ').strip('\n')] = current_ability
            current_ability += 1
        return spirit_dict

def load_from_json(file_path):
    """
    Loads sections from regions.json

    :param file_path: file path to regions.json
    :return: list of sections
    """
    pass


class Section:
    def __init__(self, start_location, length, name, description):
        self.start_location = start_location
        self.length = length
        self.name = name
        self.description = description

    def get_widget(self):
        return None


class unsigned(Section):
    """
    Unsigned bytes only
    """
    def __init__(self, start_location, length, name, description):
        """

        :param int start_location: start location as int
        :param int length: number of bits as int
        :param str name: name as str
        :param str description: description
        """
        super().__init__(start_location, length, name, description)

    def get_widget(self):
        return [sg.Text(self.name), sg.Slider(range=(0, 2**self.length), orientation='horizontal', default_value=0)]

    def get_value_from_bin(self, amiibo):
        if self.length > 8:
            return int.from_bytes(amiibo.get_bytes(self.start_location, self.start_location+self.length//8), "little")
        else:
            return amiibo.get_bytes(self.start_location)


class signed(Section):
    pass

    def get_widget(self):
        return [sg.Text(self.name), sg.Slider(range=(2**self.length/-2, 2**self.length/2-1), orientation='horizontal', default_value=0)]

    def get_value_from_bin(self, amiibo):
        if self.length > 8:
            return int.from_bytes(amiibo.get_bytes(self.start_location, self.start_location+self.length//8), "little", signed=True)
        else:
            return amiibo.get_bytes(self.start_location)


class bits(Section):
    def __init__(self, start_location, length, name, description, bit_start_location):
        super().__init__(start_location, length, name, description)
        self.bit_start_location = bit_start_location

    def get_widget(self):
        return [sg.Text(self.name), sg.Slider(range=(0, 100), orientation='horizontal', resolution=1/self.length*100, default_value=0)]

    def get_value_from_bin(self, amiibo):
        return 0


class ENUM(Section):
    def __init__(self, start_location, length, name, description, options, bit_start_location):
        super().__init__(start_location, length, name, description)
        self.options = options
        self.bit_start_location = bit_start_location

    def get_widget(self):
        option_list = list(self.options.keys())
        return [sg.Text(self.name), sg.Combo(option_list, default_value=option_list[0])]

    def get_value_from_bin(self, amiibo):
        # for if ENUM is bytewise
        if self.length % 8 == 0 and self.start_location == 0:
            if self.length > 8:
                value = int.from_bytes(amiibo.get_bytes(self.start_location, self.start_location + self.length // 8), "little")
            else:
                value = amiibo.get_bytes(self.start_location)
        else:
            value = amiibo.get_bits(self.start_location, self.bit_start_location, self.length)
        for key in self.options:
            if value == self.options[key]:
                return key
        # if value not found default to first option
        return list(self.options.keys())[0]


