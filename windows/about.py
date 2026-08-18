import webbrowser
import FreeSimpleGUI as sg

def open_about_window(version_number):
    mide_link = r"https://github.com/MiDe-S"
    jozz_link = r"https://github.com/jozz024"
    info_layout = [[sg.Text(f"Editor de Amiibo de Smash Versión {version_number}.\n\nCreado por: ", font=("Arial", 10, "bold"))],
                   [sg.Text("MiDe: "), sg.Text(mide_link, enable_events=True, tooltip="Haz clic aquí",
                                                font=("Arial", 10, "underline"))],
                   [sg.Text("jozz: "), sg.Text(jozz_link, enable_events=True, tooltip="Haz clic aquí",
                                                font=("Arial", 10, "underline"))],
                   [sg.Text("Ver Repositorio", enable_events=True, tooltip="Haz clic aquí",
                            font=("Arial", 10, "underline"))],
                   [sg.Submit("Aceptar")]]
    info_window = sg.Window("Información", info_layout, element_justification='center')
    while True:
        event, values = info_window.read()
        if event == mide_link:
            webbrowser.open(mide_link)
        elif event == jozz_link:
            webbrowser.open(jozz_link)
        elif event == "Ver Repositorio":
            webbrowser.open(r'https://github.com/jozz024/smash-amiibo-editor')
        elif event == sg.WIN_CLOSED or event == "Aceptar":
            info_window.close()
            break