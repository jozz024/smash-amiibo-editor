import region_parse as parse
import PySimpleGUI as sg
from virtual_amiibo_file import VirtualAmiiboFile
from updater import Updater
from config import Config
import os
from tkinter import filedialog
import webbrowser
import template
from copy import deepcopy


def createwindow(sections, column_key, location = None):
    section_layout = create_layout_from_sections(sections)
    menu_def = ['&File', ['&Open', '&Save', 'Save &As']], \
               ['&Config', ['Select &Key', 'Select &Regions', 'Color &Picker']], \
               ['&Template', ['&Create', '&Edit', '&Load']], \
               ['About', ['Check &for Update', 'Info']]

    layout = [[sg.Menu(menu_def)],
              [sg.Column(section_layout, size=(None, 200), scrollable=True, vertical_scroll_only=True,
                         element_justification='left', key=column_key, expand_x=True, expand_y=True)],
              [sg.Button("Load", key="LOAD_AMIIBO", enable_events=True),
               sg.Button("Save", key="SAVE_AMIIBO", enable_events=True),
               sg.Checkbox("Shuffle SN", key="SHUFFLE_SN", default=True)]]
    if location is not None:
        window = sg.Window("Smash Amiibo Editor", layout, resizable=True, location=location)
    else:
        window = sg.Window("Smash Amiibo Editor", layout, resizable=True)

    window.finalize()
    
    # needed or else window will be super small (because of menu items?)
    window.set_min_size((700, 300))
    return window

def reloadwindow(window, sections, column_key):
    ok_cancel = sg.PopupOKCancel('Doing this will reset your editing progress, continue?')
    if ok_cancel == 'OK':
        window1 = createwindow(sections, column_key, window.CurrentLocation())
        window.close()
        return window1
    else:
        return window


def create_layout_from_sections(sections):
    """
    Creates GUI objects from section list

    :param sections: list of section classes
    :return: List of lists of gui widgets
    """
    output = []

    # key index 0 is reserved for menu items
    key_index = 1
    for section in sections:
        layout, new_index = section.get_widget(key_index)
        output += layout
        key_index = new_index

    return output


def main():
    column_key = "COLUMN"
    version_number = "0.0.1"
    # initializes the config class
    config = Config()
    update = Updater(version_number, config)

    sg.theme(config.get_color())
    # if keys don't exist, tell the user
    if config.read_keys() is None:
        sg.popup(
            'Key files not present! Please put a key_retail.bin or the locked-secret.bin and unfixed-info.bin files in the resources folder.')

    # if regions don't exist, tell the user
    if config.get_region_path() is None:
        sg.popup('Region file not present! Please put a regions.txt or regions.json in the resources folder.')

    # for now, don't check for updates as it will error since the repo isn't public
    # update.check_for_update()

    # temp reads regions into class
    # if region type is txt load, if not exit the application
    if config.get_region_type() == 'txt':
        sections = parse.load_from_txt(config.get_region_path())
    else:
        os._exit(0)
    # saves config
    config.save_config()

    window = createwindow(sections, column_key)

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
                sg.popup(
                    f"Amiibo encryption key(s) are missing.\nPlease place your key(s) at {os.path.join(os.getcwd(), 'resources')}",
                    title="Missing Key!")
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
            # write regions path to file and resinstate window
            regions = filedialog.askopenfilename(filetypes=(('txt files', '*.txt'), ('json files', '*.json'),))
            if regions == '':
                continue
            config.write_region_path(regions)
            config.save_config()
            if config.get_region_type() == 'txt':
                sections = parse.load_from_txt(config.get_region_path())
            else:
                os._exit(0)
            window = reloadwindow(window, sections, column_key)
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
        elif event == "Info":
            mide_link = r"https://github.com/MiDe-S"
            jozz_link = r"https://github.com/jozz024"
            info_layout = [[sg.Text(f"Smash Amiibo Editor Version {version_number}.\n\nCreated by:")],
                           [sg.Text("MiDe:"), sg.Text(mide_link, enable_events=True, tooltip="Click Me", font=("Arial", 10, "underline"))],
                           [sg.Text("jozz:"), sg.Text(jozz_link, enable_events=True, tooltip="Click Me", font=("Arial", 10, "underline"))],
                           [sg.Text("View Repo", enable_events=True, tooltip="Click Me", font=("Arial", 10, "underline"))],
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
        elif event == "Color Picker":
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
                        sg.theme(values['-LIST-'][0])
                        config.write_color(values['-LIST-'][0])
                        config.save_config()
                        color_window.close()
                        window = reloadwindow(window, sections, column_key)
                        break
                elif event is None or event == "Cancel":
                    color_window.close()
                    break
        elif event == "Load":
            template_values = template.run_load_window()
            if template_values is not None:
                for signature in template_values:
                    for section in sections:
                        if section.get_template_signature() == signature:
                            section.update("TEMPLATE", window, amiibo, template_values[signature])

        elif event == "Edit":
            template.run_edit_window(sections)
        elif event == "Create":
            input_values = []
            for section in sections:
                input_values.append(section.get_value_from_bin(amiibo))
            template.run_create_window(deepcopy(sections), input_values)

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
