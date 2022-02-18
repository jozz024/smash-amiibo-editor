import region_parse as parse
import PySimpleGUI as sg
from virtual_amiibo_file import VirtualAmiiboFile
from updater import Updater
from config import Config
import os
from tkinter import filedialog


def create_layout_from_sections(sections):
    """
    Creates GUI objects from section list

    :param sections: list of section classes
    :return: List of lists of gui widgets
    """
    output = []

    key_index = 0
    for section in sections:
        layout, new_index = section.get_widget(key_index)
        output += layout
        key_index = new_index

    return output


def main():
    column_key = "COLUMN"
    version_number = "0.0.1"
    update = Updater(version_number)
    # initializes the config class
    config = Config()

    #if keys dont exist, open file dialog and write given paths
    if config.read_keys() == None:
        keys = filedialog.askopenfilenames(filetypes=(('BIN files', '*.bin'),))
        config.write_key_path(keys)
    
    #if regions dont exist, open file dialog and write given paths
    if config.get_region_path() == None:
        regions = filedialog.askopenfilename(filetypes=(('txt files', '*.txt'), ('json files', '*.json'),))
        config.write_region_path(regions)
    #for now, dont check for updates as it will error since the repo isnt public
    # update.check_for_update()

    # temp reads regions into class
    # if region type is txt load, if not exit the application
    if config.get_region_type() == 'txt':
        sections = parse.load_from_txt(config.get_region_path())
    else:
        os._exit(0)
    #saves config
    config.save_config()

    section_layout = create_layout_from_sections(sections)

    menu_def = ['&File', ['&Open', '&Save', 'Save &As']], \
               ['&Config', ['Select &Key', 'Select &Regions']], \
               ['&Template', ['&Create', '&Edit', '&Load']], \
               ['Update', ['Check &for Update']], \
               ['About', ['Info']]

    layout = [[sg.Menu(menu_def)],
                [sg.Column(section_layout, size=(None, 200), scrollable=True, vertical_scroll_only=True, element_justification='left', key=column_key, expand_x=True, expand_y=True)],
                [sg.Button("Load", key="LOAD_AMIIBO", enable_events=True), sg.Button("Save", key="SAVE_AMIIBO", enable_events=True), sg.Checkbox("Shuffle SN", key="SHUFFLE_SN")]]
    window = sg.Window("Smash Amiibo Editor", layout, resizable=True)
    window.finalize()
    # needed or else window will be super small (because of menu items?)
    window.set_min_size((700, 300))

    # initialize amiibo file variable
    amiibo = None

    while True:
        event, values = window.read()
        # need to change it from FileBrowse to normal button, call browse here
        if event == "LOAD_AMIIBO" or event == "Open":
            # file explorer
            path = filedialog.askopenfilename(filetypes=(('BIN files', '*.bin'),))
            # if cancelled don't try to open bin
            if path == '':
                continue

            try:
                amiibo = VirtualAmiiboFile(path, config.read_keys())

                for section in sections:
                    section.update(event, window, amiibo, None)
                window.refresh()

            except FileNotFoundError:
                sg.popup(f"Amiibo encryption key(s) are missing.\nPlease place your key(s) at {os.path.join(os.getcwd(),'resources')}", title="Missing Key!")
        elif event == "Save":
            if amiibo is not None:
                if values['SHUFFLE_SN']:
                    # if shuffle checkbox selected, shuffle the serial number
                    amiibo.randomize_sn()
                amiibo.save_bin(path)
            else:
                sg.popup("An amiibo bin has to be loaded before it can be saved.", title="Error")
        elif event == "SAVE_AMIIBO" or event == "Save As":
            # file explorer
            path = filedialog.asksaveasfilename(defaultextension='.bin', filetypes=(('BIN files', '*.bin'),))
            # if cancelled don't try to save bin
            if path == '':
                continue

            if amiibo is not None:
                if values['SHUFFLE_SN']:
                    # if shuffle checkbox selected, shuffle the serial number
                    amiibo.randomize_sn()
                amiibo.save_bin(path)
            else:
                sg.popup("An amiibo bin has to be loaded before it can be saved.", title="Error")
        elif event == 'Select Regions':
            # write regions path to file and restart program
            regions = filedialog.askopenfilename(filetypes=(('txt files', '*.txt'), ('json files', '*.json'),))
            if regions == '':
                continue
            config.write_region_path(regions)
            config.save_config()
            os.startfile('SmashAmiiboEditor.exe')
            os._exit(0)
        elif event == 'Select Key':
            # write keys path to file
            keys = filedialog.askopenfilenames(filetypes=(('BIN files', '*.bin'),))
            if keys == '':
                continue
            config.write_key_path(keys)
            config.save_config()
        elif event == 'Check for Update':
            config.set_update(True)
            # commented out for now so it doesn't crash when selected
            # update.check_for_update()
            config.save_config()
        elif event == sg.WIN_CLOSED:
            break
        # every other event is a section being updated
        else:
            try:
                if values[event] != '':
                    for section in sections:
                        if event in section.get_keys():
                            section.update(event, window, amiibo, values[event])
            except KeyError:
                pass

    window.close()


if __name__ == "__main__":
    main()
