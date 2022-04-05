import os
import tkinter as tk
import PySimpleGUI as sg

APPNAME = "Hex View"
BLOCK_WIDTH = 23
BLOCK_HEIGHT = 39
BLOCK_SIZE = BLOCK_WIDTH * BLOCK_HEIGHT


class HexWindow:
    def __init__(self, dump_data):
        layout = [[sg.Canvas(key='-canvas-', background_color="white")]]

        window = sg.Window(APPNAME, layout, finalize=True)

        self.canvas = window['-canvas-'].TKCanvas

        self.viewText = tk.Text(self.canvas, height=BLOCK_HEIGHT,
                                width=2 + (BLOCK_WIDTH * 2))

        self.data = dump_data

        self._open()

    def show_block(self):
        self.viewText.delete("1.0", "end")

        rows = [self.data[i:i + BLOCK_WIDTH] for i in range(0, len(self.data), BLOCK_WIDTH)]
        for row in rows:
            self.show_bytes(row)

        self.viewText.insert("end", "\n")

    def show_bytes(self, row):
        for byte in row:
            tags = ()
            if byte in b"\t\n\r\v\f":
                tags = ("hexspace", "graybg")
            elif 0x20 < byte < 0x7F:
                tags = ("ascii",)
            self.viewText.insert("end", "{:02X}".format(byte), tags)
            self.viewText.insert("end", " ")
        if len(row) < BLOCK_WIDTH:
            self.viewText.insert("end", " " * (BLOCK_WIDTH - len(row)) * 3)

    def _open(self):
        self.show_block()
        # sets colors of sections
        self.viewText.tag_configure("settings", background="coral", foreground="black")
        self.viewText.tag_configure("fighter_mii", background="LightBlue", foreground="black")
        self.viewText.tag_configure("exp", background="gold", foreground="black")
        self.viewText.tag_configure("spirits", background="palegreen", foreground="black")
        self.viewText.tag_configure("misc", background="cyan", foreground="black")
        self.viewText.tag_configure("behavior_data", background="plum1", foreground="black")
        self.viewText.tag_configure("grounded_moves", background="red2", foreground="black")
        self.viewText.tag_configure("aerial_moves", background="grey50", foreground="black")
        self.viewText.tag_configure("additional_behaviors", background="slateblue1", foreground="black")

        # defines sections to highlight
        self.viewText.tag_add("settings", "1.678", "1.680")
        self.viewText.tag_add("spirits", "1.681", "1.683")
        self.viewText.tag_add("spirits", "1.708", "1.716")
        self.viewText.tag_add("settings", "1.717", "1.728")
        self.viewText.tag_add("fighter_mii", "1.729", "1.995")
        self.viewText.tag_add("exp", "1.996", "1.1008")
        self.viewText.tag_add("spirits", "1.1008", "1.1019")
        self.viewText.tag_add("misc", "1.1026", "1.1073")
        self.viewText.tag_add("behavior_data", "1.1080", "1.1175")
        self.viewText.tag_add("grounded_moves", "1.1176", "1.1214")
        self.viewText.tag_add("aerial_moves", "1.1215", "1.1241")
        self.viewText.tag_add("additional_behaviors", "1.1242", "1.1253")
        self.viewText.tag_add("settings", "1.1254", "1.1259")
        self.viewText.tag_add("spirits", "1.1260", "1.1271")

        # legend
        self.viewText.insert("end", "Settings", "settings")
        self.viewText.insert("end", "  ")
        self.viewText.insert("end", "Spirits", "spirits")
        self.viewText.insert("end", "  ")
        self.viewText.insert("end", "Experience", "exp")
        self.viewText.insert("end", "  ")
        self.viewText.insert("end", "Fighter Mii", "fighter_mii")
        self.viewText.insert("end", "\n")
        self.viewText.insert("end", "Miscellaneous", "misc")
        self.viewText.insert("end", "  ")
        self.viewText.insert("end", "Behaviors", "behavior_data")
        self.viewText.insert("end", "  ")
        self.viewText.insert("end", "Grounded Moves", "grounded_moves")
        self.viewText.insert("end", "\n")
        self.viewText.insert("end", "Aerial Moves", "aerial_moves")
        self.viewText.insert("end", "  ")
        self.viewText.insert("end", "Additional Behaviors", "additional_behaviors")

        # header
        # self.viewText.insert("1.0", "00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F\n")

        self.viewText.pack()


def show_hex(path):
    HexWindow(path)
