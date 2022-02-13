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
            #options = load_ability_file()
            #section = ENUM(parts[1], 16, section_type[0], parts[-1], options)
            section = None

        elif section_type[1].strip() == "ENUM":
            # bit length is calculated by byte end - byte start * 8
            if 'b' in parts[2] or 'b' in parts[1]:
                end_loc = parts[2].split('b')
                start_loc = parts[1].split('b')
                # bit end + 8 - bit start + byte end - byte start - 1
                # -1 is to account for byte included with bits
                bit_length = int(end_loc[1]) + 8 - int(start_loc[1]) + 8*(int(end_loc[0], 16) - int(start_loc[0], 16)) - 8
            else:
                bit_length = 8*(int(parts[2], 16) - int(parts[1], 16))

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

            section = ENUM(parts[1], bit_length, section_type[0], parts[-1], options)

        elif section_type[1].strip() == "u8":
            section = unsigned(parts[1], 8, section_type[0], parts[-1])

        elif section_type[1].strip() == "u16":
            section = unsigned(parts[1], 16, section_type[0], parts[-1])

        elif section_type[1].strip() == "i8":
            section = signed(parts[1], 8, section_type[0], parts[-1])

        elif section_type[1].strip() == "i16":
            section = signed(parts[1], 16, section_type[0], parts[-1])

        elif section_type[1].strip() == "bits":
            if 'b' in parts[2] or 'b' in parts[1]:
                end_loc = parts[2].split('b')
                start_loc = parts[1].split('b')
                # bit end + 8 - bit start + byte end - byte start - 1
                # -1 is to account for byte included with bits
                bit_length = int(end_loc[1]) + 8 - int(start_loc[1]) + 8*(int(end_loc[0], 16) - int(start_loc[0], 16)) - 8
            else:
                bit_length = 8*(int(parts[2], 16) - int(parts[1], 16))
            section = bits(parts[1], bit_length, section_type[0], parts[-1])

        else:
            pass
        if section is not None:
            sections.append(section)
    return sections


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
    pass

    def get_widget(self):
        return [sg.Text(self.name), sg.Slider(range=(0, 2**self.length), orientation='horizontal', default_value=0)]

    def get_value_from_bin(self, amiibo):
        return 0


class signed(Section):
    pass

    def get_widget(self):
        return [sg.Text(self.name), sg.Slider(range=(0, 2**self.length), orientation='horizontal', default_value=0)]

    def get_value_from_bin(self, amiibo):
        return 0


class bits(Section):
    pass

    def get_widget(self):
        return [sg.Text(self.name), sg.Slider(range=(0, 100), orientation='horizontal', resolution=1/self.length*100, default_value=0)]

    def get_value_from_bin(self, amiibo):
        return 0


class ENUM(Section):
    def __init__(self, start_location, length, name, description, options):
        super().__init__(start_location, length, name, description)
        self.options = options

    def get_widget(self):
        option_list = list(self.options.keys())
        return [sg.Text(self.name), sg.Combo(option_list, default_value=option_list[0])]

    def get_value_from_bin(self, amiibo):
        return 0
