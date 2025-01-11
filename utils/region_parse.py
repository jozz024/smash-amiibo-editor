import FreeSimpleGUI as sg
from re import sub
import json
import textwrap
import sys
import os

# used to load theme for window elements
try:
    conf = open('resources/config.json')
    theme = json.load(conf)
    if 'theme' in theme:
        sg.theme(theme['theme'])
except FileNotFoundError:
    sg.theme('DarkBlue3')


def load_from_txt(file_path):
    """
    Loads sections from regions.txt

    :param str file_path: file path to regions.txt
    :return: list of sections
    """
    sections = []
    with open(file_path, 'r') as fp:
        region_file = fp.read()
        region_file = region_file.split("\n\n")
    for region in region_file:
        section = None
        parts = region.split('\n')
        section_type = parts[0].split(':')
        if section_type[1].strip() == "ABILITY":
            options = load_ability_file()
            section = ENUM(int(parts[1], 16), 8, section_type[0], parts[-1], options, 0)

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
                    elif 'x' in option[1]:
                        value = int(option[1], 16)
                    else:
                        value = int(option[1])
                    options[option[0].strip()] = value
                # after so '{' line isn't included
                if line == '{':
                    options_found = True

            section = ENUM(int(start_location, 16), bit_length, section_type[0], parts[-1], options, int(bit_start_location))

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

            section = bits(int(start_location, 16), bit_length, section_type[0], parts[-1], int(bit_start_location))

        else:
            pass
        if section is not None:
            sections.append(section)
    # Testing nick name text
    # sections.insert(0, Text(0x38, 20*8, "Nickname", "Nickname of the amiibo", True))
    return sections


def load_ability_file():
    """
    Loads the ability file of spirits

    :return: Dictionary of {spirit: value}
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    with open(os.path.join(base_path, "resources", "abilities.txt")) as abilities:
        current_ability = 1
        spirit_dict = {"None": 0}
        spirits = {}
        for lines in abilities.readlines():
            # replace up arrow encoding with up text
            spirit_name = lines.replace('â†‘â†‘', 'Up Up').replace('â†“ â†“', 'Down Down').strip('\n')
            spirit_name = spirit_name.replace('â†‘', 'Up').replace('â†“', 'Down')
            spirits[spirit_name] = current_ability
            current_ability += 1
        # This is a bad practice but will be left for now
        spirits = dict(sorted(spirits.items(), key = lambda ele: (ele[0].isnumeric(), int(ele[0]) if ele[0].isnumeric() else ele[0])))
        spirit_dict.update(spirits)
        return spirit_dict


def load_character_file():
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    with open(os.path.join(base_path, "resources", "characters.json")) as characters:
        chars = json.load(characters)

    return chars["characters"]


def load_from_json(file_path):
    """
    Loads sections from regions.json

    :param str file_path: file path to regions.json
    :return: list of sections
    """
    sections = []
    implicit_sums = []
    with open(file_path) as region_json:
        regions = json.load(region_json)
        for region in regions['regions']:
            if region['type'] == 'ability':
                options = load_ability_file()
                section = ENUM(int(region['start'], 16), region['length'], region['name'], region['description'], options, 0)
            if region['type'] == 'character':
                options = load_character_file()
                section = ENUM(int(region['start'], 16), region['length'], region['name'], region['description'], options, 0)
            elif region['type'] == 'enum':
                section = ENUM(int(region['start'], 16), region['length'], region['name'], region['description'], region['options'], region['bit_start_location'])
            elif region['type'] == 'signed':
                section = signed(int(region['start'], 16), region['length'], region['name'], region['description'])
            elif region['type'] == 'unsigned':
                section = unsigned(int(region['start'], 16), region['length'], region['name'], region['description'])
            elif region['type'] == 'text':
                section = Text(int(region['start'], 16), region['length'], region['name'], region['description'], region['big_endian'])
            elif region['type'] == 'bits':
                section = bits(int(region['start'], 16), region['length'], region['name'], region['description'], region['bit_start_location'])
            elif region['type'] == 'percentage':
                section = percentage(int(region['start'], 16), region['length'], region['name'], region['description'], region['bit_start_location'])
            elif region['type'] == 'implicitsum':
                section = ImplicitSum(region['name'], region['description'], region['counterparts'])
                implicit_sums.append(section)
            if section is not None:
                sections.append(section)
    return sections, implicit_sums


class Section:
    """
    Base virtual class used for all sections
    """
    def __init__(self, start_location, length, name, description):
        """
        Initializes the class

        :param int start_location: start location in bin
        :param int length: length of section in bits
        :param str name: Name of section
        :param str description: Description of section
        """
        self.start_location = start_location
        self.length = length
        # capitalizes names
        self.name = name.title()
        # wraps text
        self.description = "\n".join(textwrap.wrap(description, 100))

        self.primary_input_key = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def get_widget(self, key_index):
        """
        Creates widget to be displayed in GUI

        :param int key_index: key index to be used for input fields
        :return: sg widget element
        """
        self.primary_input_key = str(key_index)
        key_index += 1
        return [[sg.Text(self.name + ":", font=("Arial", 10, "bold"))],
                [sg.Text(self.description, pad=(5, (3, 15)))]], key_index

    def get_keys(self):
        """
        Gets keys for elements this section controls

        :return: list of keys
        """
        return [self.primary_input_key]

    def get_signature(self):
        """
        Generates signature of this section used to define it in regions

        :return: signature string
        """
        return f"{self.start_location}-{self.length}"

    def get_name(self):
        """
        Returns name of section

        :return: name string
        """
        return self.name


class ByteWise(Section):
    """
    Responsible for integer sections that follow byte boundaries (lengths of 8, 16, 24, etc.)
    """
    def __init__(self, start_location, length, name, description, maximum, minimum=0):
        """
        Initializes the class

        :param int start_location: start location as int
        :param int length: number of bits as int
        :param str name: name as str
        :param str description: description
        :param int maximum: range maximum
        :param int minimum: range minimum
        """
        super().__init__(start_location, length, name, description)
        self.max = maximum
        self.min = minimum

    def validate_input(self, value):
        """
        Validates user input

        :param str value: user input
        :return: validated input as string
        """
        value = sub("[^-\d]", '', value)
        while value.rfind('-') > 0:
            value = ''.join(value.rsplit('-', 1))

        if value == '' or value == '-':
            return value
        value = int(value)

        if value > self.max:
            value = self.max
        elif value < self.min:
            value = self.min

        return str(value)

    def get_widget(self, key_index):
        """
        Creates widget to be displayed in GUI

        :param int key_index: key index to be used for input fields
        :return: sg widget element
        """
        layout, new_index = super().get_widget(key_index)

        # noinspection PyTypeChecker
        layout[0].append(sg.Spin([str(i) for i in range(self.min, self.max+1)], enable_events=True, key=self.primary_input_key, initial_value=0, size=(10, None)))
        return layout, new_index

    def update(self, event_key, window, amiibo, value):
        """
        Updates all amiibo bits/elements that correspond to this section

        :param str event_key: event that called this function
        :param sg.Window window: window where elements are to be updated
        :param VirtualAmiiboFile amiibo: amiibo file to be updated
        :param str value: value to update window/amiibo with
        :return: validated input
        """
        # handles when bin is first loaded
        if event_key == "LOAD_AMIIBO" or event_key == "Open (CTRL+O)":
            window[self.primary_input_key].update(value)
            # no need to validate since value came from bin
            validated = value
        elif event_key == "TEMPLATE":
            window[self.primary_input_key].update(value)
            validated = value
        else:
            validated = self.validate_input(value)

            if validated != value:
                window[self.primary_input_key].update(validated)
            if validated == "" or validated == "-":
                validated = 0
        return validated

    def get_signature(self):
        """
        Generates signature of this section used to define it in regions

        :return: signature string
        """
        return super().get_signature()


class unsigned(ByteWise):
    """
    Responsible for unsigned bytes only
    """
    def __init__(self, start_location, length, name, description):
        """
        Initializes the function

        :param int start_location: start location as int
        :param int length: number of bits as int
        :param str name: name as str
        :param str description: description
        """
        super().__init__(start_location, length, name, description, 2 ** length - 1)

    def get_widget(self, key_index):
        """
        Creates widget to be displayed in GUI

        :param int key_index: key index to be used for input fields
        :return: sg widget element
        """
        return super().get_widget(key_index)

    def get_value_from_bin(self, amiibo):
        """
        Gets value of this section from amiibo

        :param VirtualAmiiboFile amiibo: amiibo to get data from
        :return: value as int
        """
        if amiibo is None:
            return 0
        if self.length > 8:
            return int.from_bytes(amiibo.get_bytes(self.start_location, self.start_location+self.length//8), "little")
        else:
            return amiibo.get_bytes(self.start_location)

    def set_value_in_bin(self, amiibo, value):
        """
        Sets value in amiibo corresponding to this section

        :param VirtualAmiiboFile amiibo: amiibo to set data in
        :param int value: value to set
        :return: None
        """
        amiibo.set_bytes(self.start_location, value.to_bytes(self.length//8, 'little'))

    def update(self, event_key, window, amiibo, value):
        """
        Updates all amiibo bits/elements that correspond to this section

        :param str event_key: event that called this function
        :param sg.Window window: window where elements are to be updated
        :param VirtualAmiiboFile amiibo: amiibo file to be updated
        :param str value: value to update window/amiibo with
        :return: None
        """
        if event_key == "LOAD_AMIIBO" or event_key == "Open (CTRL+O)":
            value = self.get_value_from_bin(amiibo)
        value = super().update(event_key, window, amiibo, value)
        if amiibo is not None:
            self.set_value_in_bin(amiibo, int(value))

    def get_signature(self):
        """
        Generates signature of this section used to define it in regions

        :return: signature string
        """
        parent = super().get_signature()
        return "unsigned-" + parent


class signed(ByteWise):
    """
    Responsible for signed byte sections
    """
    def __init__(self, start_location, length, name, description):
        """
        Initializes section

        :param int start_location: start location as int
        :param int length: number of bits as int
        :param str name: name as str
        :param str description: description
        """
        super().__init__(start_location, length, name, description, 2 ** length // 2 - 1, 2 ** length // -2)

    def get_widget(self, key_index):
        """
        Creates widget to be displayed in GUI

        :param int key_index: key index to be used for input fields
        :return: sg widget element
        """
        return super().get_widget(key_index)

    def get_value_from_bin(self, amiibo):
        """
        Gets value of this section from amiibo

        :param VirtualAmiiboFile amiibo: amiibo to get data from
        :return: value as int
        """
        if amiibo is None:
            return 0
        if self.length > 8:
            return int.from_bytes(amiibo.get_bytes(self.start_location, self.start_location+self.length//8), "little", signed=True)
        else:
            return amiibo.get_bytes(self.start_location)

    def set_value_in_bin(self, amiibo, value):
        """
        Sets value in amiibo corresponding to this section

        :param VirtualAmiiboFile amiibo: amiibo to set data in
        :param int value: value to set
        :return: None
        """
        amiibo.set_bytes(self.start_location, value.to_bytes(self.length//8, 'little', signed=True))

    def update(self, event_key, window, amiibo, value):
        """
        Updates all amiibo bits/elements that correspond to this section

        :param str event_key: event that called this function
        :param sg.Window window: window where elements are to be updated
        :param VirtualAmiiboFile amiibo: amiibo file to be updated
        :param str value: value to update window/amiibo with
        :return: None
        """
        if event_key == "LOAD_AMIIBO" or event_key == "Open (CTRL+O)":
            value = self.get_value_from_bin(amiibo)
        value = super().update(event_key, window, amiibo, value)
        if amiibo is not None:
            self.set_value_in_bin(amiibo, int(value))

    def get_signature(self):
        """
        Generates signature of this section used to define it in regions

        :return: signature string
        """
        parent = super().get_signature()
        return "signed-" + parent


class bits(Section):
    """
    Responsible for all bitwise sections that are interpreted as raw binary
    """
    def __init__(self, start_location, length, name, description, bit_start_location):
        """
        Initializes section

        :param int start_location: start location as int
        :param int length: number of bits as int
        :param str name: name as str
        :param str description: description
        :param int bit_start_location: start location of bit in start byte #the left most bit in the section in first byte
        """
        super().__init__(start_location, length, name, description)
        self.bit_start_location = bit_start_location

        self.secondary_input_key = None

    def validate_input(self, value):
        """
        Validates user input

        :param str value: user input
        :return: validated input as string
        """
        # regex for removing all non signed float characters https://regexlib.com/Search.aspx?k=float&AspxAutoDetectCookieSupport=1
        value = sub("[^1|0]", '', value)
        if value == '':
            return ''

        if len(value) > self.length:
            value = value[1:]

        return value

    def get_widget(self, key_index):
        """
        Creates widget to be displayed in GUI

        :param int key_index: key index to be used for input fields
        :return: sg widget element
        """
        layout, key_index = super().get_widget(key_index)
        # noinspection PyTypeChecker
        layout[0].append(sg.Spin([format(i, f"#0{self.length+2}b")[2:] for i in range(0, 2**self.length)], enable_events=True, key=self.primary_input_key, initial_value="0"*self.length, size=(10, None)))
        self.secondary_input_key = str(key_index)
        key_index += 1
        layout[0].append(sg.Text("0", key=self.secondary_input_key))
        return layout, key_index

    def get_value_from_bin(self, amiibo):
        """
        Gets value of this section from amiibo

        :param VirtualAmiiboFile amiibo: amiibo to get data from
        :return: value as binary string
        """
        if amiibo is None:
            return 0
        value = amiibo.get_bits(self.start_location, self.bit_start_location, self.length)
        return format(value, f"#0{self.length+2}b")[2:]

    def set_value_in_bin(self, amiibo, value):
        """
        Sets value in amiibo corresponding to this section

        :param VirtualAmiiboFile amiibo: amiibo to set data in
        :param str value: value to set as binary string
        :return: None
        """
        value = int(value, 2)
        amiibo.set_bits(self.start_location, self.bit_start_location, self.length, value)

    def get_keys(self):
        """
        Gets keys for elements this section controls

        :return: list of keys
        """
        key_list = super().get_keys()
        key_list.append(self.secondary_input_key)
        return key_list

    def update(self, event_key, window, amiibo, value):
        """
        Updates all amiibo bits/elements that correspond to this section

        :param str event_key: event that called this function
        :param sg.Window window: window where elements are to be updated
        :param VirtualAmiiboFile amiibo: amiibo file to be updated
        :param str value: value to update window/amiibo with as binary string
        :return: None
        """
        # handles when bin is first loaded
        if event_key == "LOAD_AMIIBO" or event_key == "Open (CTRL+O)":
            value = self.get_value_from_bin(amiibo)

            window[self.primary_input_key].update(value)
            window[self.secondary_input_key].update(int(value, 2))

        elif event_key == "TEMPLATE":
            window[self.primary_input_key].update(value)
            window[self.secondary_input_key].update(int(value, 2))
            if amiibo is not None:
                self.set_value_in_bin(amiibo, value)
        else:
            validated = self.validate_input(value)
            if validated != value:
                window[self.primary_input_key].update(validated)
            if validated == '':
                validated = "0"
            window[self.secondary_input_key].update(int(validated, 2))

            if amiibo is not None:
                self.set_value_in_bin(amiibo, validated)

    def get_signature(self):
        """
        Generates signature of this section used to define it in regions

        :return: signature string
        """
        parent = super().get_signature()
        return "bits-" + parent + f"-{self.bit_start_location}"


class percentage(Section):
    """
    Responsible for all bitwise sections that are interpreted as percent of max
    """
    def __init__(self, start_location, length, name, description, bit_start_location):
        """
        Initializes section

        :param int start_location: start location as int
        :param int length: number of bits as int
        :param str name: name as str
        :param str description: description
        :param int bit_start_location: start location of bit in start byte #the right most bit in the section in first byte
        """
        super().__init__(start_location, length, name, description)
        self.max = 100
        self.min = 0
        self.resolution = 1/(2**length-1)*100
        self.bit_start_location = bit_start_location

        self.secondary_input_key = None

    def validate_input(self, value):
        """
        Validates user input

        :param str value: user input
        :return: validated input as string
        """
        # regex for removing all non signed float characters https://regexlib.com/Search.aspx?k=float&AspxAutoDetectCookieSupport=1
        value = sub("[^.\d]", '', value)

        while value.count('.') > 1:
            value = ''.join(value.rsplit('.', 1))
        if value == '' or value == '.':
            return str("0.0")

        value = float(value)

        if value > self.max:
            value = self.max
        elif value < self.min:
            value = self.min

        return str(value)

    def get_widget(self, key_index):
        """
        Creates widget to be displayed in GUI

        :param int key_index: key index to be used for input fields
        :return: sg widget element
        """
        layout, key_index = super().get_widget(key_index)
        # noinspection PyTypeChecker
        layout[0].append(
            sg.Slider(key=self.primary_input_key, range=(self.min, self.max), orientation='horizontal', default_value=0,
                      disable_number_display=True, enable_events=True, resolution=round(self.resolution, 5)))
        self.secondary_input_key = str(key_index)
        key_index += 1
        # noinspection PyTypeChecker
        layout[0].append(sg.Spin([str(round(i*self.resolution, 5)) for i in range(0, int(100//self.resolution)+1)], enable_events=True, key=self.secondary_input_key, initial_value=0.0, size=(10, None)))
        return layout, key_index

    def get_value_from_bin(self, amiibo):
        """
        Gets value of this section from amiibo

        :param VirtualAmiiboFile amiibo: amiibo to get data from
        :return: value as float
        """
        if amiibo is None:
            return 0
        value = amiibo.get_bits(self.start_location, self.bit_start_location, self.length, reverse=True)
        return round(value / (2**self.length-1) * 100, 5)

    def set_value_in_bin(self, amiibo, value):
        """
        Sets value in amiibo corresponding to this section

        :param VirtualAmiiboFile amiibo: amiibo to set data in
        :param float value: value to set
        :return: None
        """
        # rounding is needed because int always rounds down
        value = int(round(value / 100 * (2**self.length - 1), 0))
        # write bits backwards for Percentages
        amiibo.set_bits(self.start_location, self.bit_start_location, self.length, value, reverse=True)

    def get_keys(self):
        """
        Gets keys for elements this section controls

        :return: list of keys
        """
        key_list = super().get_keys()
        key_list.append(self.secondary_input_key)
        return key_list

    def update(self, event_key, window, amiibo, value):
        """
        Updates all amiibo bits/elements that correspond to this section

        :param str event_key: event that called this function
        :param sg.Window window: window where elements are to be updated
        :param VirtualAmiiboFile amiibo: amiibo file to be updated
        :param str value: value to update window/amiibo with
        :return: None
        """
        # handles when bin is first loaded
        if event_key == "LOAD_AMIIBO" or event_key == "Open (CTRL+O)":
            value = self.get_value_from_bin(amiibo)

            window[self.primary_input_key].update(value)
            window[self.secondary_input_key].update(value)
        elif event_key == "TEMPLATE":
            value = float(value)
            window[self.primary_input_key].update(value)
            window[self.secondary_input_key].update(value)
        else:
            if event_key == self.secondary_input_key:
                if value == "":
                    value = 0
                    window[self.primary_input_key].update(value)
                else:
                    validated = float(self.validate_input(value))

                    # makes deleting last digit after . possible
                    if value[-1] == '.':
                        window[self.secondary_input_key].update(str(validated)[:-1])
                    # makes deleting last digit before . possible
                    elif value[0] == '.':
                        if str(validated)[1:] == value:
                            validated = 0
                        else:
                            window[self.secondary_input_key].update(str(validated)[1:])
                    # makes deleting . possible
                    elif value == str(int(validated)):
                        window[self.secondary_input_key].update(value)

                    elif str(validated) != value:
                        window[self.secondary_input_key].update(validated)

                    window[self.primary_input_key].update(validated)
                    value = validated
            else:
                # this sets the value to the correct resolution
                value = round(round(value / 100 * (2**self.length - 1), 0) / (2**self.length-1) * 100, 5)
                window[self.secondary_input_key].update(value)

        if amiibo is not None:
            self.set_value_in_bin(amiibo, value)

    def get_signature(self):
        """
        Generates signature of this section used to define it in regions

        :return: signature string
        """
        parent = super().get_signature()
        return "percentage-" + parent + f"-{self.bit_start_location}"


class ENUM(Section):
    """
    Responsible for regions that are interpreted as special values instead of raw string/binary/int/etc
    """
    def __init__(self, start_location, length, name, description, options, bit_start_location):
        """
        Initializes section

        :param int start_location: start location as int
        :param int length: number of bits as int
        :param str name: name as str
        :param str description: description
        :param Dict options: dictionary of enum options {name: value}
        :param int bit_start_location: start location of bit in start byte #the right most bit in the section in first byte
        """
        super().__init__(start_location, length, name, description)
        self.options = options
        self.bit_start_location = bit_start_location

    def get_widget(self, key_index):
        """
        Creates widget to be displayed in GUI

        :param int key_index: key index to be used for input fields
        :return: sg widget element
        """
        layout, new_index = super().get_widget(key_index)
        key_index = new_index
        option_list = list(self.options.keys())
        # noinspection PyTypeChecker
        layout[0].append(sg.Combo(option_list, key=self.primary_input_key, default_value=option_list[0], enable_events=True))
        return layout, key_index

    def get_value_from_bin(self, amiibo):
        """
        Gets value of this section from amiibo

        :param VirtualAmiiboFile amiibo: amiibo to get data from
        :return: value as str
        """
        if amiibo is None:
            return list(self.options.keys())[0]
        # gets exact or closest value lower than current
        value = amiibo.get_bits(self.start_location, self.bit_start_location, self.length)
        closest_lower_key = None
        closest_lower_value = float("-inf")
        for key in self.options:
            if value == self.options[key]:
                return key
            elif value > self.options[key] > closest_lower_value:
                closest_lower_key = key
                closest_lower_value = self.options[key]
        # if value not found default to first option
        if closest_lower_key is None:
            return list(self.options.keys())[0]
        return closest_lower_key

    def set_value_in_bin(self, amiibo, value):
        """
        Sets value in amiibo corresponding to this section

        :param VirtualAmiiboFile amiibo: amiibo to set data in
        :param str value: value to set
        :return: None
        """
        try:
            amiibo.set_bits(self.start_location, self.bit_start_location, self.length, self.options[value])
        # for when value can't be found in self.options
        except KeyError:
            pass

    def get_keys(self):
        """
        Gets keys for elements this section controls

        :return: list of keys
        """
        return super().get_keys()

    def update(self, event_key, window, amiibo, value):
        """
        Updates all amiibo bits/elements that correspond to this section

        :param str event_key: event that called this function
        :param sg.Window window: window where elements are to be updated
        :param VirtualAmiiboFile amiibo: amiibo file to be updated
        :param str value: value to update window/amiibo with
        :return: None
        """
        if event_key == "LOAD_AMIIBO" or event_key == "Open (CTRL+O)":
            window[self.primary_input_key].update(self.get_value_from_bin(amiibo))
        elif event_key == "TEMPLATE":
            window[self.primary_input_key].update(value)
        if amiibo is not None and value is not None:
            # allows searching in drop down list
            if value == '':
                window[self.primary_input_key].update(values=list(self.options.keys()))
            else:
                data = []
                for item in self.options:
                    if value.lower() in item.lower():
                        if value.lower() == item.lower():
                            # when option is selected, show full list instead of sublist
                            window[self.primary_input_key].update(value, values=list(self.options.keys()))
                            self.set_value_in_bin(amiibo, value)
                            return None
                        else:
                            data.append(item)

                window[self.primary_input_key].update(value, values=data)
            self.set_value_in_bin(amiibo, value)

    def get_signature(self):
        """
        Generates signature of this section used to define it in regions

        :return: signature string
        """
        parent = super().get_signature()
        return "ENUM-" + parent + f"-{self.bit_start_location}"


class Text(Section):
    """
    Responsible for bytes encoded as utf-16
    """
    def __init__(self, start_location, length, name, description, big_endian=True):
        """
        Initializes section

        :param int start_location: start location as int
        :param int length: number of bits as int
        :param str name: name as str
        :param str description: description
        :param big_endian: endianess of encoding
        """
        super().__init__(start_location, length, name, description)
        self.big_endian = big_endian

        self.characters = length // 16

    def get_widget(self, key_index):
        """
        Creates widget to be displayed in GUI

        :param int key_index: key index to be used for input fields
        :return: sg widget element
        """
        layout, key_index = super().get_widget(key_index)
        # noinspection PyTypeChecker
        layout[0].append(sg.Input(enable_events=True, key=self.primary_input_key, default_text="", size=(15, None)))

        return layout, key_index

    def get_value_from_bin(self, amiibo):
        """
        Gets value of this section from amiibo

        :param VirtualAmiiboFile amiibo: amiibo to get data from
        :return: value as str
        """
        if amiibo is None:
            return ""
        value = amiibo.get_bytes(self.start_location, self.start_location+self.length//8)

        if self.big_endian:
            value = value.decode('utf-16-be').rstrip('\x00')
        else:
            value = value.decode('utf-16-le').rstrip('\x00')
        return value

    def set_value_in_bin(self, amiibo, value):
        """
        Sets value in amiibo corresponding to this section

        :param VirtualAmiiboFile amiibo: amiibo to set data in
        :param str value: value to set
        :return: None
        """
        if self.big_endian:
            value = value.encode('utf-16-be').ljust(20, b'\x00')
        else:
            value = value.encode('utf-16-le').ljust(20, b'\x00')

        amiibo.set_bytes(self.start_location, value)

    def update(self, event_key, window, amiibo, value):
        """
        Updates all amiibo bits/elements that correspond to this section

        :param str event_key: event that called this function
        :param sg.Window window: window where elements are to be updated
        :param VirtualAmiiboFile amiibo: amiibo file to be updated
        :param str value: value to update window/amiibo with
        :return: None
        """
        # handles when bin is first loaded
        if event_key == "LOAD_AMIIBO" or event_key == "Open (CTRL+O)":
            value = self.get_value_from_bin(amiibo)

            window[self.primary_input_key].update(value)
        elif event_key == "TEMPLATE":
            window[self.primary_input_key].update(value)
        else:
            if len(value) > self.characters:
                value = value[:-1*(len(value)-self.characters)]
                window[self.primary_input_key].update(value)

        if amiibo is not None:
            self.set_value_in_bin(amiibo, value)

    def get_signature(self):
        """
        Generates signature of this section used to define it in regions

        :return: signature string
        """
        parent = super().get_signature()
        return "Text-" + parent


class ImplicitSum:
    """
    Responsible for dealing with implicitly encoded values like jab/nair
    """
    def __init__(self, name, description, counterparts):
        """
        Initializes section

        :param str name: name as str
        :param str description: description
        :param Tuple(str) counterparts: tuple of corresponding section signatures
        """
        self.name = name
        self.description = description
        self.primary_input_key = name
        self.counterparts = counterparts

    def __str__(self):
        return self.name

    def get_counterpart_signatures(self):
        """
        gets all counterpart signatures to sum

        :return: list of str of corresponding signatures
        """
        return self.counterparts

    def get_widget(self, key_index):
        """
        Creates widget to be displayed in GUI

        :param int key_index: key index to be used for input fields
        :return: sg widget element
        """
        # doesn't call super() and doesn't set_primary key, updates are handled via DiffSumManager
        # noinspection PyTypeChecker
        return [[sg.Text(self.name + ":", font=("Arial", 10, "bold")), sg.Input(default_text=100, disabled=True, key=self.primary_input_key, size=(15, None), text_color="black")],
                [sg.Text(self.description, pad=(5, (3, 15)))]], key_index

    def update(self, event, window, amiibo, value):
        """

        :param str event: which event caused an update
        :param Psg window: window containing this section
        :param VirtualAmiiboFile amiibo: amiibo file
        :param double value: value to set sum too
        :return:
        """
        if value is not None:
            window[self.primary_input_key].update(value)

    def get_name(self):
        """
        Returns name of section

        :return: name string
        """
        return self.name

    def get_signature(self):
        """
        Returns a signature, needed for parity but will return None
        :return: None
        """
        return None

    def get_keys(self):
        """
        Returns this sections keys

        :return: list[str]
        """
        return [self.primary_input_key]
