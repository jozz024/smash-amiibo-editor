import region_parse as parse
import PySimpleGUI as sg
from virtual_amiibo_file import VirtualAmiiboFile
import os


def create_layout_from_sections(sections):
    """
    Creates GUI objects from section list

    :param sections: list of section classes
    :return: List of lists of gui widgets
    """
    output = []

    for section in sections:
        output.append(section.get_widget())

    return output


def main():
    load_btn_name = "Load"
    save_btn_name = "Save"
    column_key = "COLUMN"

    # temp reads regions into class
    sections = parse.load_from_txt(r"C:\Users\dmasi\Powersaves For AMIIBO\!CODING\win-unpacked\regions builds\regions_3.3.txt")

    section_layout = create_layout_from_sections(sections)

    layout = [[sg.Column(section_layout, size=(None, 200), scrollable=True, vertical_scroll_only=True, element_justification='left', key=column_key, expand_x=True, expand_y=True)],
        [sg.FileBrowse(load_btn_name, target="LOAD_AMIIBO", file_types=(('Bin Files', '*.bin'),), enable_events=True), sg.FileSaveAs(save_btn_name, target="SAVE_AMIIBO", file_types=(('Bin Files', '*.bin'),), enable_events=True)],
              [sg.Input(key="LOAD_AMIIBO", visible=False, enable_events=True)], [sg.Input(key="SAVE_AMIIBO", visible=False, enable_events=True)]]
    window = sg.Window("Smash Amiibo Editor", layout, resizable=True)

    # initialize amiibo file variable
    amiibo = None

    while True:
        event, values = window.read()
        if event == "LOAD_AMIIBO":
            try:
                amiibo = VirtualAmiiboFile(values[load_btn_name])

                for i, row in enumerate(window[column_key].Rows):
                    row[-1].update(sections[i].get_value_from_bin(amiibo))
                window.refresh()

            except FileNotFoundError:
                sg.popup(f"Amiibo encryption key(s) are missing.\nPlease place your key(s) at {os.path.join(os.getcwd(),'resources')}", title="Missing Key!")
        elif event == "SAVE_AMIIBO":
            if amiibo is not None:
                amiibo.save_bin(values[save_btn_name])
            else:
                sg.popup("An amiibo bin has to be loaded before it can be saved.", title="Error")
        elif event == sg.WIN_CLOSED:
            break

    window.close()


if __name__ == "__main__":
    main()