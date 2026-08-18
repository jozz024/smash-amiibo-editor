import FreeSimpleGUI as sg
from tkinter import filedialog
import os
from utils.ssbu_amiibo import InvalidAmiiboDump
from utils.virtual_amiibo_file import VirtualAmiiboFile

def open_metadata_window(config):
    outcome = None
    recieverBin = None
    recieverName = "No seleccionado"
    donorBin = None
    DONOR_NAME_KEY = "donor_name"
    RECIEVER_NAME_KEY = "reciver_name"
    TRANSPLANT_SAVE_KEY = "save_location"
    layout = [[sg.Text( "El Donante es de la figura a la que quieres transplantar. ")],
            [sg.Text( "El Receptor tiene los datos de entrenamiento que quieres en la figura. ")],
            [sg.Button( "Donante "), sg.Text( "No seleccionado ", key=DONOR_NAME_KEY)],
            [sg.Button( "Receptor "), sg.Text( "No seleccionado ", key=RECIEVER_NAME_KEY)],
            [sg.Column([[sg.FileSaveAs( "Transplantar Metadatos de la Figura ", target= "SaveTrigger ", key=TRANSPLANT_SAVE_KEY, file_types=(('Archivos Bin', '*.bin'),), default_extension= ".bin ", disabled=True)]], justification='r'), sg.Input(key= "SaveTrigger ", enable_events=True, visible=False)],
            [sg.HorizontalSeparator()],
            [sg.Text( "Para restaurar con powersaves, el nombre del archivo bin debe coincidir con el del bin donante. ")],
            [sg.Text( "(como AMIIBO_1a2345_2024_01_01_[]) ")]]
    window = sg.Window( "Editor de Amiibo de Smash ", layout,  element_justification='center', resizable=True)
    window.finalize()

    while True:
        event, values = window.read()

        match event:
            case  "Donante ":
                path = filedialog.askopenfilename(filetypes=(('Archivos amiibo', '*.json;*.bin'), ))
                # if cancelled don't try to open bin
                if path == '':
                     continue
                window[DONOR_NAME_KEY].update(os.path.basename(path))
                donorBin = path
                if recieverBin and donorBin:
                    window[TRANSPLANT_SAVE_KEY].update(disabled=False)
            case  "Receptor ":
                path = filedialog.askopenfilename(filetypes=(('Archivos amiibo', '*.json;*.bin'), ))
                # if cancelled don't try to open bin
                if path == '':
                     continue
                window[RECIEVER_NAME_KEY].update(os.path.basename(path))
                recieverBin = path
                if recieverBin and donorBin:
                    window[TRANSPLANT_SAVE_KEY].update(disabled=False)

            case  "SaveTrigger ":
                if values[TRANSPLANT_SAVE_KEY] == '':
                    continue
                donor = VirtualAmiiboFile(donorBin, config.read_keys())
                reciever = VirtualAmiiboFile(recieverBin, config.read_keys())
                try:
                    reciever.recieve_metadata_transplant(donor)
                    reciever.save_bin(values[TRANSPLANT_SAVE_KEY])
                    window.close()
                    outcome =  "OK "
                    break
                except InvalidAmiiboDump:
                    sg.popup( "Por favor inicializa ambos bins en SSBU antes de transplantar ")
            case sg.WIN_CLOSED:
                break
    return outcome