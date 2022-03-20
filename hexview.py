import os
import sys
from tkinter import *
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as filedialog
try:
    Spinbox = ttk.Spinbox
except AttributeError:
    Spinbox = tk.Spinbox


APPNAME = "Hex View"
BLOCK_WIDTH = 23
BLOCK_HEIGHT = 32
BLOCK_SIZE = BLOCK_WIDTH * BLOCK_HEIGHT

class MainWindow:

    def __init__(self, parent, path):
        self.parent = parent
        self.create_variables()
        self.create_widgets()
        self.create_layout()
        self._open(path)

    def create_variables(self):
        self.filename = None
        self.offset = tk.IntVar()
        self.offset.set(0)

    def create_widgets(self):
        frame = self.frame = ttk.Frame(self.parent)
        self.create_view()

    def create_view(self):
        self.viewText = tk.Text(self.frame, height=BLOCK_HEIGHT,
                                width=2 + (BLOCK_WIDTH * 2))
        #self.viewText.config(state = DISABLED)
        self.viewText.tag_configure("error", foreground="red")

    def create_layout(self):
        self.viewText.grid(row=1, column=0, columnspan=6, sticky=tk.NSEW)
        self.frame.grid(row=0, column=0, sticky=tk.NSEW)

    def show_block(self, *args):
        self.viewText.delete("1.0", "end")
        if not self.filename:
            return
        try:
            self.filename.seek(self.offset.get(), os.SEEK_SET)
            block = self.filename.read(BLOCK_SIZE)
        except ValueError: # Empty offsetSpinbox
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


    def open(self, *args):
        self.viewText.delete("1.0", "end")
        self.offset.set(0)
        filename = filedialog.askopenfilename(title="Open — {}".format(
                                              APPNAME))
        self._open(filename)

    def _open(self, filename):
            self.parent.title("Hex View")
            size = filename.getbuffer().nbytes
            size = (size - BLOCK_SIZE if size > BLOCK_SIZE else
                    size - BLOCK_WIDTH)
            self.filename = filename
            self.show_block()
            self.viewText.config(state = DISABLED)

    def quit(self, event=None):
        self.parent.destroy()

def show_hex(path):
    app = tk.Tk()
    app.title("Hex View")
    window = MainWindow(app, path)
    app.protocol("WM_DELETE_WINDOW", window.quit)
    app.resizable(width=False, height=False)
    app.mainloop()

