import PySimpleGUI as sg
import json
import os

try:
    conf = open('resources/config.json')
    theme = json.load(conf)
    if 'theme' in theme:
        sg.theme(theme['theme'])
except FileNotFoundError:
    sg.theme('DarkBlue3')


def run_create_window(sections, input_values):
    section_layout = []

    # key index 0 is reserved for menu items
    key_index = 1
    for i, section in enumerate(sections):
        check_box = sg.Checkbox("", key=key_index, default=True, enable_events=True)
        key_index += 1

        layout = [check_box, sg.Text(section.get_name()), sg.Input(input_values[i], key=key_index)]
        key_index += 1

        section_layout.append(layout)

    create_layout = [[sg.Text("Template Name:"), sg.Input(key="TEMPLATE_NAME")],
                     [sg.Column(section_layout, size=(None, 200), scrollable=True, vertical_scroll_only=True,
                                element_justification='left', expand_x=True, expand_y=True)],
                     [sg.Button("Select All"), sg.Button("Deselect All")],
                     [sg.Submit("Create"), sg.Cancel("Cancel")]]
    create_window = sg.Window("Select Template", create_layout, element_justification='center')

    while True:
        event, values = create_window.read()

        if event == "Create":
            # some fancy saving thing
            if values["TEMPLATE_NAME"] == "":
                sg.popup("Please give your template a name", title="Missing Name")
                continue

            template_values = {}
            for i in range(1, len(sections) * 2, 2):
                # if checkbox enabled
                if values[i]:
                    # set region signature = value in input
                    template_values[sections[i // 2].get_template_signature()] = values[i + 1]

            path = os.path.join("templates", values["TEMPLATE_NAME"])
            path += ".json"
            with open(path, 'w+') as fp:
                fp.write(json.dumps(template_values))

            create_window.close()
            break
        elif event == "Select All":
            # checkboxes have odd key values
            for i in range(1, len(sections) * 2, 2):
                create_window[i].update(True)
                create_window[i + 1].update(disabled=False)
        elif event == "Deselect All":
            # checkboxes have odd key values
            for i in range(1, len(sections) * 2, 2):
                create_window[i].update(False)
                create_window[i + 1].update(disabled=True)

        elif event == sg.WIN_CLOSED or event == "Cancel":
            create_window.close()
            break
        else:
            try:
                if event % 1 == 0:
                    create_window[event + 1].update(disabled=not values[event])
            except TypeError:
                pass


def run_load_window():
    templates = []
    files = os.listdir("templates")
    for file in files:
        if file[-4:] == "json":
            templates.append(file[:-5])
    load_layout = [[sg.Listbox(templates, select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, size=(50, 5))],
                   [sg.Submit("Select"), sg.Cancel("Cancel")]]
    load_window = sg.Window("Select Template", load_layout, element_justification='center')
    while True:
        event, values = load_window.read()

        if event == "Select":
            # since no keys are specified key defaults to 0
            # listbox returns list, but only 1 option is selectable so it's [0]
            path = os.path.join("templates", values[0][0])
            path += ".json"
            load_window.close()
            with open(path, 'r') as fp:
                template_values = json.load(fp)
                return template_values
        elif event == sg.WIN_CLOSED or event == "Cancel":
            load_window.close()
            break
    return None


def run_edit_window(sections):
    path = run_load_window()
    if path is None:
        return None
