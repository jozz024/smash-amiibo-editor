import region_parse as parse
import PySimpleGUI as sg
from virtual_amiibo_file import VirtualAmiiboFile


def main():
    #temporary
    key_path = r"C:\Users\dmasi\Powersaves For AMIIBO\!CODING\key_retail.bin"

    #sections = parse.load_from_txt(r"C:\Users\dmasi\Powersaves For AMIIBO\!CODING\win-unpacked\regions builds\regions_3.3.txt")
    load_btn_name = "Load"
    save_btn_name = "Save"

    layout = [[sg.FileBrowse(load_btn_name, target="LOAD_AMIIBO", file_types=(('Bin Files', '*.bin'),), enable_events=True), sg.FileSaveAs(save_btn_name, target="SAVE_AMIIBO", file_types=(('Bin Files', '*.bin'),), enable_events=True)],
              [sg.Input(key="LOAD_AMIIBO", visible=False, enable_events=True)], [sg.Input(key="SAVE_AMIIBO", visible=False, enable_events=True)]]
    window = sg.Window("Smash Amiibo Editor", layout, resizable=True)

    # initialize amiibo file variable
    amiibo = None

    while True:
        event, values = window.read()
        if event == "LOAD_AMIIBO":
            amiibo = VirtualAmiiboFile(values[load_btn_name], key_path)
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