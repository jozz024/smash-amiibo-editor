import webbrowser
import FreeSimpleGUI as sg

def open_about_window(version_number):
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