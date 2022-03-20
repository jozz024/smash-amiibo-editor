import io
import region_parse as parse
import PySimpleGUI as sg
from virtual_amiibo_file import VirtualAmiiboFile, JSONVirtualAmiiboFile, InvalidAmiiboDump, AmiiboHMACTagError, AmiiboHMACDataError
from updater import Updater
from config import Config
import os
from tkinter import filedialog
import webbrowser
import template
from copy import deepcopy
import hexview

def get_menu_def(update_available: bool, amiibo_loaded: bool, ryujinx: bool = False):
    """
    Creates menu definition for window

    :param bool update_available: If update is available or not
    :param bool amiibo_loaded: If amiibo has been loaded or not
    :return: tuple of menu
    """
    if amiibo_loaded:
        file_tab = ['&File', ['&Open (CTRL+O)', '&Save', 'Save &As (CTRL+S)', '---', '&View Hex']]
        if ryujinx:
            file_tab = ['&File', ['&Open (CTRL+O)', '&Save', 'Save &As (CTRL+S)', '---', '!&View Hex']]
    else:
        file_tab = ['&File', ['&Open (CTRL+O)', '!&Save', '!Save &As (CTRL+S)', '---', '!&View Hex']]
    template_tab = ['&Template', ['&Create', '&Edit', '&Load (CTRL+L)']]

    if update_available:
        settings_tab = ['&Settings', ['Select &Key(s)', 'Select &Regions', '---', '&Update',  '&Change Theme', '&About']]
    else:
        settings_tab = ['&Settings', ['Select &Key(s)', 'Select &Regions', '---', '!&Update', '&Change Theme', '&About']]
    return file_tab, template_tab, settings_tab


def create_window(sections, column_key, update, location=None, size=None):
    """
    Creates the window of the application

    :param List[Sections] sections: list of section objects
    :param str column_key: key for column
    :param bool update: whether or not an update is available
    :param Tuple(int, int) location: window location to use
    :param Tuple(int, int) size: window size to use
    :return: window object
    """
    section_layout, last_key = create_layout_from_sections(sections)
    menu_def = get_menu_def(update, False)

    layout = [[sg.Menu(menu_def)],
              [sg.Text("The amiibo's personality is: None", key="PERSONALITY")],
              [sg.Column(section_layout, size=(None, 180), scrollable=True, vertical_scroll_only=True,
                         element_justification='left', key=column_key, expand_x=True, expand_y=True)],
              [sg.Button("Load", key="LOAD_AMIIBO", enable_events=True),
               sg.Button("Save", key="SAVE_AMIIBO", enable_events=True, disabled=True),
               sg.Checkbox("Shuffle SN", key="SHUFFLE_SN", default=True)]]
    if location is not None:
        window = sg.Window("Smash Amiibo Editor", layout, resizable=True, location=location, size=size)
    else:
        window = sg.Window("Smash Amiibo Editor", layout, resizable=True)

    window.finalize()

    for i in range(1, last_key+1):
        window[str(i)].bind('<KeyPress>', '')

    # for windows Control works, for MacOS change to Command

    # hot key for opening
    window.bind('<Control-o>', "Open (CTRL+O)")
    # hot key for loading template
    window.bind('<Control-l>', "Load (CTRL+L)")
    # hot key for saving gets set when an amiibo is loaded

    # needed or else window will be super small (because of menu items?)
    window.set_min_size((700, 500))
    return window


def show_reload_warning():
    """
    Runs a pop up window that asks user if it's okay to reset editing progress

    :return: Ok or Cancel input from popup window
    """
    popup = sg.PopupOKCancel('Doing this will reset your editing progress, continue?')
    return popup


def reload_window(window, sections, column_key, update):
    """
    Reloads the window

    :param sg.Window window: old window
    :param list[Section()] sections: list of section objects
    :param str column_key: key for column
    :param bool update: whether or not it should be updated
    :return: newly created window
    """
    window1 = create_window(sections, column_key, update, window.CurrentLocation(), window.size)
    window.close()
    return window1


def create_layout_from_sections(sections):
    """
    Creates GUI objects from section list

    :param list[Section()] sections: list of section objects
    :return: List of lists of gui widgets, last key index used
    """
    output = []

    # key index 0 is reserved for menu items
    key_index = 1
    for section in sections:
        layout, new_index = section.get_widget(key_index)
        output += layout
        key_index = new_index

    return output, key_index - 1


def main():
    if os.path.isfile(os.path.join(os.getcwd(), "update.exe")):
        os.remove(os.path.join(os.getcwd(), "update.exe"))

    column_key = "COLUMN"
    version_number = "1.1.0"
    # initializes the config class
    config = Config()
    update = Updater(version_number, config)
    sg.theme(config.get_color())
    # if keys don't exist, tell the user
    if config.read_keys() is None:
        sg.popup(
            'Key files not present!\nPlease select key(s) using Settings > Select Key(s)')

    # if regions don't exist, tell the user
    if config.get_region_path() is None:
        sg.popup('Region file not present! Please put a regions.txt or regions.json in the resources folder.')

    # If an update is found, prompt user if they want to update
    updatePopUp = update.check_for_update()

    # temp reads regions into class
    if config.get_region_type() == 'txt':
        sections = parse.load_from_txt(config.get_region_path())
    elif config.get_region_type() == 'json':
        sections = parse.load_from_json(config.get_region_path())
    else:
        sg.popup("No region could be loaded")
        exit()
    # saves config
    config.save_config()
    # impossible for sections to not be loaded when this is reached
    # noinspection PyUnboundLocalVariable
    window = create_window(sections, column_key, updatePopUp)

    # initialize amiibo file variable
    amiibo = None

    while True:
        event, values = window.read()
        # need to change it from FileBrowse to normal button, call browse here
        if event == "LOAD_AMIIBO" or event == "Open (CTRL+O)":
            if config.read_keys() is None:
                sg.popup(
                    f"Amiibo encryption key(s) are missing.\nThese keys are for encrypting/decrypting amiibo.\nYou can get them by searching for them on the internet.\nPlease select keys using Settings > Select Key",
                    title="Missing Key!")
                continue
            # file explorer
            path = filedialog.askopenfilename(filetypes=(('amiibo files', '*.json;*.bin'), ))
            # if cancelled don't try to open bin
            if path == '':
                continue
            try:
                try:
                    if path.endswith(".json"):
                        amiibo = JSONVirtualAmiiboFile(path, config.read_keys())
                        ryujinx_loaded = True
                    else:
                        amiibo = VirtualAmiiboFile(path, config.read_keys())
                        ryujinx_loaded = False
                except (InvalidAmiiboDump, AmiiboHMACTagError, AmiiboHMACDataError):
                        sg.popup("Invalid amiibo dump.", title='Incorrect Dump!')
                        continue

                for section in sections:
                    section.update(event, window, amiibo, None)
                window["PERSONALITY"].update(f"The amiibo's personality is: {amiibo.get_personality()}")
                # update menu to include save options
                if ryujinx_loaded is not True:
                    window[0].update(get_menu_def(updatePopUp, True))
                else:
                    window[0].update(get_menu_def(updatePopUp, True, True))
                # update save button to be clickable
                window["SAVE_AMIIBO"].update(disabled=False)
                # hot key for saving enabled
                window.bind('<Control-s>', "Save As (CTRL+S)")

                window.refresh()

            except FileNotFoundError:
                sg.popup(
                    f"Amiibo encryption key(s) are missing.\nThese keys are for encrypting/decrypting amiibo.\nYou can get them by searching for them on the internet.\nPlease select keys using Settings > Select Key",
                    title="Missing Key!")



        elif event == "Save":
            if amiibo is not None:
                if values['SHUFFLE_SN']:
                    # if shuffle checkbox selected, shuffle the serial number
                    amiibo.randomize_sn()
                # this event is not reachable until bin is loaded (which sets path)
                # noinspection PyUnboundLocalVariable
                amiibo.save_bin(path)


            else:
                sg.popup("An amiibo has to be loaded before it can be saved.", title="Error")
        elif event == "SAVE_AMIIBO" or event == "Save As (CTRL+S)":
            # file explorer
            if ryujinx_loaded is True:
                path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=(('JSON files', '*.json'),))
            else:
                path = filedialog.asksaveasfilename(defaultextension='.bin', filetypes=(('BIN files', '*.bin'),))
            # if cancelled don't try to save bin
            if path == '':
                continue

            elif amiibo is not None:
                if values['SHUFFLE_SN']:
                    # if shuffle checkbox selected, shuffle the serial number
                    amiibo.randomize_sn()
                amiibo.save_bin(path)
            else:
                sg.popup("An amiibo has to be loaded before it can be saved.", title="Error")
        elif event == 'Select Regions':
            # write regions path to file and reinstate window
            regions = filedialog.askopenfilename(filetypes=(('Any Region', '*.json;*.txt'),))
            if regions == '':
                continue
            reloadwarn = show_reload_warning()
            if reloadwarn == 'OK':
                config.write_region_path(regions)
                config.save_config()
                if config.get_region_type() == 'txt':
                    sections = parse.load_from_txt(config.get_region_path())
                elif config.get_region_type() == 'json':
                    sections = parse.load_from_json(config.get_region_path())
                window = reload_window(window, sections, column_key, updatePopUp)
            else:
                continue
        elif event == 'Select Key(s)':
            # write keys path to file
            keys = filedialog.askopenfilenames(filetypes=(('BIN files', '*.bin'),))
            if keys == '':
                continue
            config.write_key_paths(*keys)
            config.save_config()
        elif event == 'Update':
            config.set_update(True)
            release = update.get_release()
            assets = update.get_assets(release)
            update.update(assets)
            config.save_config()
        elif event == "About":
            mide_link = r"https://github.com/MiDe-S"
            jozz_link = r"https://github.com/jozz024"
            info_layout = [[sg.Text(f"Smash Amiibo Editor Version {version_number}.\n\nCreated by:", font=("Arial", 10, "bold"))],
                           [sg.Text("MiDe:"), sg.Text(mide_link, enable_events=True, tooltip="Click Me",
                                                      font=("Arial", 10, "underline"))],
                           [sg.Text("jozz:"), sg.Text(jozz_link, enable_events=True, tooltip="Click Me",
                                                      font=("Arial", 10, "underline"))],
                           [sg.Text("View Repo", enable_events=True, tooltip="Click Me",
                                    font=("Arial", 10, "underline"))],
                           [sg.Submit("Okay")]]
            info_window = sg.Window("Info", info_layout, element_justification='center')
            while True:
                event, values = info_window.read()
                if event == mide_link:
                    webbrowser.open(mide_link)
                elif event == jozz_link:
                    webbrowser.open(jozz_link)
                elif event == "View Repo":
                    webbrowser.open(r'https://github.com/jozz024/smash-amiibo-editor')
                elif event == sg.WIN_CLOSED or event == "Okay":
                    info_window.close()
                    break
        elif event == "Change Theme":
            color_list = sg.list_of_look_and_feel_values()
            color_list.sort()
            layout = [[sg.Text('Color Browser')],
                      [sg.Text("Click a color to set it as the editor's color")],
                      [sg.Listbox(values=color_list,
                                  size=(20, 12), key='-LIST-', enable_events=True)],
                      [sg.Button('Okay'), sg.Button('Cancel')]]

            color_window = sg.Window('Color Browser', layout)
            while True:  # Event Loop
                event, values = color_window.read()
                if event == 'Okay':
                    if len(values['-LIST-']) != 0:
                        reloadwarn = show_reload_warning()
                        if reloadwarn == 'OK':
                            sg.theme(values['-LIST-'][0])
                            config.write_color(values['-LIST-'][0])
                            config.save_config()
                            color_window.close()
                            window = reload_window(window, sections, column_key, updatePopUp)
                            break
                        else:
                            color_window.close()
                            break
                elif event is None or event == "Cancel":
                    color_window.close()
                    break
        elif event == "View Hex":
            if amiibo is None:
                pass
            hexview.show_hex(io.BytesIO(amiibo.get_data()))
        elif event == "Load (CTRL+L)":
            selected_template = template.run_load_window()
            if selected_template is not None:
                template_values, template_name = selected_template
                for signature in template_values:
                    for section in sections:
                        if section.get_template_signature() == signature:
                            try:
                                section.update("TEMPLATE", window, amiibo, template_values[signature])
                            except (KeyError, IndexError, ValueError):
                                continue

        elif event == "Edit":
            template.run_edit_window(sections, amiibo)
        elif event == "Create":
            template.run_create_window(deepcopy(sections), amiibo)

        elif event == sg.WIN_CLOSED:
            break
        # every other event is a section being updated
        else:
            try:
                for section in sections:
                    if event in section.get_keys():
                        section.update(event, window, amiibo, values[event])
                if amiibo is not None:
                    window["PERSONALITY"].update(f"The amiibo's personality is: {amiibo.get_personality()}")
            except KeyError:
                pass

    window.close()


if __name__ == "__main__":
    main()
