import region_parse as parse
import PySimpleGUI as sg
from virtual_amiibo_file import VirtualAmiiboFile
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
    load_btn_name = "Load"
    save_btn_name = "Save"
    column_key = "COLUMN"

    # temp reads regions into class
    sections = parse.load_from_txt(r"C:\Users\dmasi\Powersaves For AMIIBO\!CODING\win-unpacked\regions builds\regions_3.3.txt")

    section_layout = create_layout_from_sections(sections)

    menu_def = ['&File', ['&Open', '&Save', 'Save &As']], \
               ['&Config', ['Select &Key', 'Select &Regions']], \
               ['&Template', ['&Create', '&Edit', '&Load']], \
               ['About', ['Info']]

    layout = [[sg.Menu(menu_def)],
                [sg.Column(section_layout, size=(None, 200), scrollable=True, vertical_scroll_only=True, element_justification='left', key=column_key, expand_x=True, expand_y=True)],
                [sg.Button(load_btn_name, key="LOAD_AMIIBO", enable_events=True), sg.Button(save_btn_name, key="SAVE_AMIIBO", enable_events=True)]]
    window = sg.Window("Smash Amiibo Editor", layout)

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
                amiibo = VirtualAmiiboFile(path)

                for section in sections:
                    section.update(event, window, amiibo, None)
                window.refresh()

            except FileNotFoundError:
                sg.popup(f"Amiibo encryption key(s) are missing.\nPlease place your key(s) at {os.path.join(os.getcwd(),'resources')}", title="Missing Key!")
        elif event == "SAVE_AMIIBO" or event == "Save As":
            # file explorer
            path = filedialog.asksaveasfilename(defaultextension='.bin', filetypes=(('BIN files', '*.bin'),))
            # if cancelled don't try to save bin
            if path == '':
                continue

            if amiibo is not None:
                amiibo.save_bin(path)
            else:
                sg.popup("An amiibo bin has to be loaded before it can be saved.", title="Error")
        elif event == sg.WIN_CLOSED:
            break
        # every other event is a section being updated
        else:
            for section in sections:
                if event in section.get_keys():
                    section.update(event, window, amiibo, values[event])

    window.close()


if __name__ == "__main__":
    main()
