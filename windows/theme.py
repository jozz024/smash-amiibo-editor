import FreeSimpleGUI as sg

def open_theme_window(config, show_reload_warning):
    reloadwarn = None             
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
                reloadwarn = show_reload_warning()
                if reloadwarn == 'OK':
                    sg.theme(values['-LIST-'][0])
                    config.write_color(values['-LIST-'][0])
                    config.save_config()
                    color_window.close()
                    break
                else:
                    color_window.close()
                    break
        elif event is None or event == "Cancel":
            color_window.close()
            break
    return reloadwarn