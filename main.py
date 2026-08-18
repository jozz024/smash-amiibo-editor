from utils import region_parse as parse
import FreeSimpleGUI as sg
from utils.virtual_amiibo_file import VirtualAmiiboFile, JSONVirtualAmiiboFile, InvalidAmiiboDump, AmiiboHMACTagError, AmiiboHMACDataError, InvalidMiiSizeError
from utils.updater import Updater
from utils.config import Config
import os
from tkinter import filedialog
from windows import template
from copy import deepcopy
from windows import hexview
from utils.section_manager import ImplicitSumManager
from windows import about
from windows import metadata_transplant
from windows import initialize
from windows import theme
import ctypes

myappid = u'sae.editor.sae.1.7.0'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

def get_menu_def(update_available: bool, amiibo_loaded: bool, ryujinx: bool = False):
    """
    Creates menu definition for window
    """
    if amiibo_loaded:
        file_tab = ['&Archivo', ['&Abrir (CTRL+O)', '&Guardar', 'Guardar &Como (CTRL+S)', 'Copiar &Valores', '---', '&Transplantar Metadatos', '&Ver Hex']]
        mii_tab = ["&Mii", ["&Exportar Mii", "&Cargar Mii"]]
        if ryujinx:
            file_tab = ['&Archivo', ['&Abrir (CTRL+O)', '&Guardar', 'Guardar &Como (CTRL+S)', 'Copiar &Valores', '---', '&Transplantar Metadatos', '!&Ver Hex']]
            mii_tab = ["!&Mii", ["&Exportar Mii", "&Cargar Mii"]]
    else:
        file_tab = ['&Archivo', ['&Abrir (CTRL+O)', '!&Guardar', '!Guardar &Como (CTRL+S)', '!Copiar &Valores', '---', '&Transplantar Metadatos', '!&Ver Hex']]
        mii_tab = ["!&Mii", ["&Exportar Mii", "&Cargar Mii"]]

    template_tab = ['&Plantilla', ['&Crear', '&Editar', '&Cargar (CTRL+L)']]
    if update_available:
        settings_tab = ['&Ajustes', ['Seleccionar &Clave(s)', 'Seleccionar &Regiones', '---', '&Actualizar', '&Cambiar Tema', '&Acerca de']]
    else:
        settings_tab = ['&Ajustes', ['Seleccionar &Clave(s)', 'Seleccionar &Regiones', '---', '!&Actualizar', '&Cambiar Tema', '&Acerca de']]
    return file_tab, mii_tab, template_tab, settings_tab


def create_window(sections, column_key, update, location=None, size=None):
    section_layout, last_key = create_layout_from_sections(sections)
    menu_def = get_menu_def(update, False)

    layout = [[sg.Menu(menu_def)],
              [sg.Text("La personalidad del amiibo es: Ninguna", key="PERSONALITY")],
              [sg.Column(section_layout, size=(None, 180), scrollable=True, vertical_scroll_only=True,
                         element_justification='left', key=column_key, expand_x=True, expand_y=True)],
              [sg.Button("Cargar", key="LOAD_AMIIBO", enable_events=True),
               sg.Button("Guardar", key="SAVE_AMIIBO", enable_events=True, disabled=True),
               sg.Checkbox("Aleatorizar SN", key="SHUFFLE_SN", default=False)]]
    if location is not None:
        window = sg.Window("Editor de Amiibo de Smash", layout, resizable=True, location=location, size=size, icon="SAE.ico")
    else:
        window = sg.Window("Editor de Amiibo de Smash", layout, resizable=True, icon="SAE.ico")

    window.finalize()

    for i in range(1, last_key+1):
        window[str(i)].bind('<KeyPress>', '')
        try:
            window[str(i)].update(disabled=True)
        except TypeError:
            pass

    window.bind('<Control-o>', "Abrir (CTRL+O)")
    window.bind('<Control-l>', "Cargar (CTRL+L)")

    window.set_min_size((700, 500))
    return window


def show_reload_warning():
    popup = sg.PopupOKCancel('Esto reiniciará tu progreso de edición, ¿continuar?')
    return popup

def show_missing_key_warning():
    popup = sg.popup(f"Faltan las claves de encriptación de Amiibo.\nEstas claves sirven para encriptar/desencriptar amiibos.\nPuedes encontrarlas buscando en internet.\nPor favor selecciona las claves en Ajustes > Seleccionar Clave(s)",
                    title="¡Clave faltante!")
    return popup

def reload_window(window, sections, column_key, update):
    window1 = create_window(sections, column_key, update, window.CurrentLocation(), window.size)
    window.close()
    return window1


def create_layout_from_sections(sections):
    output = []
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
    version_number = "1.7.0"

    config = Config()
    update = Updater(version_number, config)
    sg.theme(config.get_color())
    if config.read_keys() is None:
        sg.popup(
            '¡Archivos de claves no encontrados!\nPor favor selecciona las claves en Ajustes > Seleccionar Clave(s)')

    if config.get_region_path() is None:
        sg.popup('¡Archivo de regiones no encontrado! Coloca un regions.txt o regions.json en la carpeta resources.')

    updatePopUp = update.check_for_update()

    implicit_sums = None

    try:
        if config.get_region_type() == 'txt':
            sections = parse.load_from_txt(config.get_region_path())
        elif config.get_region_type() == 'json':
            sections, implicit_sums = parse.load_from_json(config.get_region_path())
        else:
            sg.popup("No se pudo cargar ninguna región")
            exit()
    except FileNotFoundError:
        sg.popup("No se encontró el archivo de regiones, revisa tu configuración.")
        exit()
    config.save_config()
    window = create_window(sections, column_key, updatePopUp)

    amiibo = None
    implicit_sum_manager = ImplicitSumManager(implicit_sums, sections)

    while True:
        event, values = window.read()
        match event:
            case "LOAD_AMIIBO" | "Abrir (CTRL+O)":
                if config.read_keys() is None:
                    show_missing_key_warning()
                    continue
                path = filedialog.askopenfilename(filetypes=(('Archivos amiibo', '*.json;*.bin'), ))
                if path == '':
                    continue
                try:
                    try:
                        if path.endswith(".json"):
                            amiibo = JSONVirtualAmiiboFile(path, config.read_keys())
                            ryujinx_loaded = True
                        else:
                            amiibo = VirtualAmiiboFile(path, config.read_keys())
                            if amiibo.is_initialized() == False:
                                amiibo = initialize.open_initialize_amiibo_window(amiibo)
                            ryujinx_loaded = False
                            if amiibo == None:
                                continue
                    except (InvalidAmiiboDump, AmiiboHMACTagError, AmiiboHMACDataError):
                        sg.popup("Dump de amiibo inválido.", title='¡Dump incorrecto!')
                        continue
                    for section in sections:
                        section.update(event, window, amiibo, None)
                    implicit_sum_manager.update(event, window, amiibo)
                    window["PERSONALITY"].update(f"La personalidad del amiibo es: {amiibo.get_personality()}")

                    if ryujinx_loaded is not True:
                        window[0].update(get_menu_def(updatePopUp, True))
                    else:
                        window[0].update(get_menu_def(updatePopUp, True, True))
                    window["SAVE_AMIIBO"].update(disabled=False)
                    window.bind('<Control-s>', "Guardar Como (CTRL+S)")
                    for i in range(1, int(sections[-1].get_keys()[-1])+1):
                        try:
                            window[str(i)].update(disabled=False)
                        except TypeError:
                            pass

                    window.refresh()

                except FileNotFoundError:
                    sg.popup(
                        f"Faltan las claves de encriptación de Amiibo.\nEstas claves sirven para encriptar/desencriptar amiibos.\nPuedes encontrarlas buscando en internet.\nPor favor selecciona las claves en Ajustes > Seleccionar Clave(s)",
                        title="¡Clave faltante!")

            case "Guardar":
                if amiibo is not None:
                    if values['SHUFFLE_SN']:
                        amiibo.randomize_sn()
                    amiibo.save_bin(path)
                else:
                    sg.popup("Debes cargar un amiibo antes de poder guardarlo.", title="Error")
            case "SAVE_AMIIBO" | "Guardar Como (CTRL+S)":
                if ryujinx_loaded is True:
                    path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=(('Archivos JSON', '*.json'),))
                else:
                    path = filedialog.asksaveasfilename(defaultextension='.bin', filetypes=(('Archivos BIN', '*.bin'),))
                if path == '':
                    continue

                elif amiibo is not None:
                    if values['SHUFFLE_SN']:
                        amiibo.randomize_sn()
                    amiibo.save_bin(path)
                else:
                    sg.popup("Debes cargar un amiibo antes de poder guardarlo.", title="Error")
            case "Copiar Valores":
                output = ""
                for section in sections:
                    if type(section) == parse.percentage:
                        current_val = section.get_value_from_bin(amiibo)
                    elif type(section) == parse.ImplicitSum:
                        current_val = values[section.name]
                    else:
                        continue
                    output += f"{section}: {current_val}\n"

                sg.clipboard_set(output)

            case 'Seleccionar Regiones':
                regions = filedialog.askopenfilename(filetypes=(('Cualquier Región', '*.json;*.txt'),))
                if regions == '':
                    continue
                reloadwarn = show_reload_warning()
                if reloadwarn == 'OK':
                    config.write_region_path(regions)
                    config.save_config()
                    if config.get_region_type() == 'txt':
                        sections = parse.load_from_txt(config.get_region_path())
                        implicit_sums = None
                    elif config.get_region_type() == 'json':
                        sections, implicit_sums = parse.load_from_json(config.get_region_path())
                    implicit_sum_manager = ImplicitSumManager(implicit_sums, sections)
                    window = reload_window(window, sections, column_key, updatePopUp)
                else:
                    continue
            case 'Seleccionar Clave(s)':
                keys = filedialog.askopenfilenames(filetypes=(('Archivos BIN', '*.bin'),))
                if keys == '':
                    continue
                config.write_key_paths(*keys)
                config.save_config()
            case "Exportar Mii":
                path = filedialog.asksaveasfilename(defaultextension='.bin', filetypes=(('Archivos BIN', '*.bin'),))
                if path == "":
                    continue
                amiibo.dump_mii(path)
            case "Cargar Mii":
                mii_path =  filedialog.askopenfilename(filetypes=(('Archivos BIN', '*.bin'),))
                if mii_path == "":
                    continue
                try:
                    amiibo.set_mii(mii_path)
                except InvalidMiiSizeError:
                    sg.popup("¡El dump del Mii es demasiado grande!", title='¡Dump de Mii incorrecto!')
                    continue
                for section in sections:
                    section.update("LOAD_AMIIBO", window, amiibo, None)
            case "Actualizar":
                config.set_update(True)
                release = update.get_release()
                assets = update.get_assets(release)
                update.update(assets)
                config.save_config()
            case "Acerca de":
                about.open_about_window(version_number)
            case "Cambiar Tema":
                warning = theme.open_theme_window(config, show_reload_warning)
                if warning == "OK":
                    window = reload_window(window, sections, column_key, updatePopUp)
            case "Ver Hex":
                if amiibo is None:
                    pass
                hexview.show_hex(amiibo.get_data())
            case "Cargar (CTRL+L)":
                selected_template = template.run_load_window()
                if selected_template is not None:
                    template_values, template_name = selected_template
                    for signature in template_values:
                        for section in sections:
                            if section.get_signature() == signature:
                                try:
                                    section.update("TEMPLATE", window, amiibo, template_values[signature])
                                except (KeyError, IndexError, ValueError):
                                    continue
                    implicit_sum_manager.update(event, window, amiibo)

            case "Editar":
                template.run_edit_window(sections, amiibo)
            case "Crear":
                template.run_create_window(deepcopy(sections), amiibo)

            case "Transplantar Metadatos":
                if config.read_keys() is None:
                    show_missing_key_warning()
                    continue
                outcome = metadata_transplant.open_metadata_window(config)
                if outcome == "OK":
                    sg.Popup("¡Éxito!")

            case sg.WIN_CLOSED:
                break
            case _:
                try:
                    for section in sections:
                        if event in section.get_keys():
                            section.update(event, window, amiibo, values[event])
                    implicit_sum_manager.update(event, window, amiibo)
                    if amiibo is not None:
                        window["PERSONALITY"].update(f"La personalidad del amiibo es: {amiibo.get_personality()}")
                except KeyError:
                    pass

    window.close()


if __name__ == "__main__":
    main()