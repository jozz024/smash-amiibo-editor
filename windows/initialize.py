import FreeSimpleGUI as sg
from utils.virtual_amiibo_file import InvalidMiiSizeError

def open_amiibo_settings_prompt():
    """
    Runs a pop up window that asks user if they want to register their amiibo.
    :return: Yes or No input from popup window
    """
    popup = sg.PopupYesNo('Este amiibo no está registrado con un mii o nombre. \n¿Te gustaría registrar este amiibo?')
    return popup

def open_initialize_amiibo_window(amiibo):
    # Asks the user if they want to apply a mii and name
    open_settings = open_amiibo_settings_prompt()
    if open_settings ==  "Sí ":
        amiibo_settings_layout = [[sg.Text( "Menú de Ajustes del amiibo ")],
                [sg.Text( "Archivo Mii: "), sg.Button( "Cargar Mii ", key=  "load-mii-key ", enable_events=True)
                ],
                [sg.Text( "Nombre del amiibo: "), sg.Input(key =  "amiibo-name-key ", size=15, enable_events=True)],
                [sg.Button( "Guardar ", key= "save-amiibo-settings-key ", enable_events=True), sg.Button( "Cancelar ", key= "cancel-amiibo-settings-key ", enable_events = True)]]
        amiibo_settings_window = sg.Window( "Ajustes del amiibo ", amiibo_settings_layout)
        while True:
            settings_event, settings_values = amiibo_settings_window.read()
            if settings_event ==  "load-mii-key ":
                # Opens a FileDialog to adk for the mii file
                mii_filename = sg.filedialog.askopenfilename(filetypes=(('Archivos Mii', ' .bin; .ffsd;*.cfsd'), ))
                if mii_filename ==  " ":
                    sg.popup( "¡Por favor selecciona un archivo mii! ", title =  "Seleccionar Mii ")
            if settings_event ==  "amiibo-name-key ":
                amiibo_name: str = settings_values[ "amiibo-name-key "]
            if settings_event ==  "save-amiibo-settings-key ":
                # Passes the data to the initialize function in VirtualAmiiboFile
                try:
                    amiibo.initialize_amiibo(mii_filename, amiibo_name)
                    amiibo_settings_window.close()
                except InvalidMiiSizeError:
                    sg.popup( "¡El dump del Mii es demasiado grande! ", title='¡Dump de Mii incorrecto!')
                    continue
            if settings_event ==  "cancel-amiibo-settings-key ":
                # Sets the amiibo to None on cancel
                amiibo = None
                amiibo_settings_window.close()
            if settings_event == sg.WIN_CLOSED:
                # Sets the amiibo to None on cancel
                amiibo = None
                amiibo_settings_window.close()
                break
    if open_settings ==  "No ":
        amiibo = None
    return amiibo