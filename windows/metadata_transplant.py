import FreeSimpleGUI as sg
from tkinter import filedialog
import os

from utils.ssbu_amiibo import InvalidAmiiboDump
from utils.virtual_amiibo_file import VirtualAmiiboFile

def open_metadata_window(config):
    outcome = None
    recieverBin = None
    recieverName = "Not seleced"
    donorBin = None
    DONOR_NAME_KEY = "donor_name"
    RECIEVER_NAME_KEY = "reciver_name"
    TRANSPLANT_SAVE_KEY = "save_location"


    layout = [[sg.Text("Donor is from the figure you want to transplant to.")],
            [sg.Text("Reciever has the training data you want on the figure.")],
            [sg.Button("Donor"), sg.Text("Not selected", key=DONOR_NAME_KEY)],
            [sg.Button("Reciever"), sg.Text("Not selected", key=RECIEVER_NAME_KEY)],
            [sg.Column([[sg.FileSaveAs("Transplant Figure Metadata", target="SaveTrigger", key=TRANSPLANT_SAVE_KEY, file_types=(('Bin Files', '*.bin'),), default_extension=".bin", disabled=True)]], justification='r'), sg.Input(key="SaveTrigger", enable_events=True, visible=False)],
            [sg.HorizontalSeparator()],
            [sg.Text("In order to restore with powersaves, bin file name must be formatted to match that of the donor bin.")],
            [sg.Text("(like AMIIBO_1a2345_2024_01_01_[])")]]
    window = sg.Window("Smash Amiibo Editor", layout,  element_justification='center', resizable=True)
    window.finalize()
    
    while True:
        event, values = window.read()

        match event:
            case "Donor":
                path = filedialog.askopenfilename(filetypes=(('amiibo files', '*.json;*.bin'), ))
                # if cancelled don't try to open bin
                if path == '':
                    continue
                window[DONOR_NAME_KEY].update(os.path.basename(path))
                donorBin = path
                if recieverBin and donorBin:
                    window[TRANSPLANT_SAVE_KEY].update(disabled=False)
            case "Reciever":
                path = filedialog.askopenfilename(filetypes=(('amiibo files', '*.json;*.bin'), ))
                # if cancelled don't try to open bin
                if path == '':
                    continue
                window[RECIEVER_NAME_KEY].update(os.path.basename(path))
                recieverBin = path
                if recieverBin and donorBin:
                    window[TRANSPLANT_SAVE_KEY].update(disabled=False)

            case "SaveTrigger":
                if values[TRANSPLANT_SAVE_KEY] == '':
                    continue
                donor = VirtualAmiiboFile(donorBin, config.read_keys())
                reciever = VirtualAmiiboFile(recieverBin, config.read_keys())
                try:
                    reciever.recieve_metadata_transplant(donor)
                    reciever.save_bin(values[TRANSPLANT_SAVE_KEY])
                    window.close()
                    outcome = "OK"
                    break
                except InvalidAmiiboDump:
                    sg.popup("Please initialize both bins in SSBU before transplanting")
            case sg.WIN_CLOSED:
                break
    return outcome

