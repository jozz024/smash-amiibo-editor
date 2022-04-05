import os
from tkinter import *
import tkinter as tk
import PySimpleGUI as sg

APPNAME = "Hex View"
BLOCK_WIDTH = 23
BLOCK_HEIGHT = 34
BLOCK_SIZE = BLOCK_WIDTH * BLOCK_HEIGHT


class MainWindow:
    def __init__(self, path):
        layout = [[sg.Canvas(key='-canvas-', background_color="white")]]

        window = sg.Window(APPNAME, layout, finalize=True)

        self.canvas = window['-canvas-'].TKCanvas

        self.viewText = tk.Text(self.canvas, height=BLOCK_HEIGHT,
                                width=2 + (BLOCK_WIDTH * 2))
        self.viewText.tag_configure("error", foreground="red")

        self.offset = tk.IntVar()
        self.offset.set(0)

        self.filename = path

        self._open()

    def create_layout(self):
        self.viewText.grid(row=1, column=0, columnspan=6, sticky=tk.NSEW)
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)

    def show_block(self):
        self.viewText.delete("1.0", "end")
        if not self.filename:
            return
        try:
            self.filename.seek(self.offset.get(), os.SEEK_SET)
            block = self.filename.read(BLOCK_SIZE)
        except ValueError:  # Empty offsetSpinbox
            return
        rows = [block[i:i + BLOCK_WIDTH]
                for i in range(0, len(block), BLOCK_WIDTH)]
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
        # defines sections to highlight
        self.viewText.tag_add("settings", "1.678", "1.680")
        self.viewText.tag_add("spirits", "1.681", "1.683")
        self.viewText.tag_add("spirits", "1.708", "1.716")
        self.viewText.tag_add("settings", "1.717", "1.728")
        self.viewText.tag_add("fighter mii", "1.729", "1.995")
        self.viewText.tag_add("exp", "1.996", "1.1008")
        self.viewText.tag_add("spirits", "1.1008", "1.1019")
        self.viewText.tag_add("misc", "1.1026", "1.1073")
        self.viewText.tag_add("behavior data", "1.1080", "1.1175")
        self.viewText.tag_add("grounded moves", "1.1176", "1.1214")
        self.viewText.tag_add("aerial moves", "1.1215", "1.1241")
        self.viewText.tag_add("additional behaviors", "1.1242", "1.1253")
        self.viewText.tag_add("settings", "1.1254", "1.1259")
        self.viewText.tag_add("spirits", "1.1260", "1.1271")
        # sets colors of sections
        self.viewText.tag_configure("settings", background="coral", foreground="black")
        self.viewText.tag_configure("fighter mii", background="LightBlue", foreground="black")
        self.viewText.tag_configure("exp", background="gold", foreground="black")
        self.viewText.tag_configure("spirits", background="palegreen", foreground="black")
        self.viewText.tag_configure("misc", background="cyan", foreground="black")
        self.viewText.tag_configure("behavior data", background="plum1", foreground="black")
        self.viewText.tag_configure("grounded moves", background="red2", foreground="black")
        self.viewText.tag_configure("aerial moves", background="grey50", foreground="black")
        self.viewText.tag_configure("additional behaviors", background="slateblue1", foreground="black")

        self.viewText.config(state=DISABLED)
        self.viewText.pack()


def show_hex(path):
    MainWindow(path)
