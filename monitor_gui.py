#!/usr/bin/env python
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-

from tkinter import *

class Monitor(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.geometry("1000x500") # Window size
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        # First label
        self.first_label = Label(self, text="Wow Agile")
        self.first_label.pack()

        # Hi there (hello world) button
        self.hi_there = Button(self)
        self.hi_there["text"] = "Hello World\n(click me)"
        self.hi_there["command"] = self.say_hi
        self.hi_there.pack(side="top")

        # Quit button
        self.quit = Button(self, text="QUIT", fg="red", command=self.master.destroy)
        self.quit.pack(side="bottom")

        # Input field
        self.var_text = StringVar()
        self.input_field = Entry(self, textvariable=self.var_text, width=30)
        self.input_field.pack()

        # Listbox
        self.list = Listbox(self)
        self.list.pack()

        # Listbox population
        self.list.insert(END, "Server 1")
        self.list.insert(END, "Server 2")


    def say_hi(self):
        print("hi there, everyone! Text of the input field: " + self.var_text.get())



def main():
    root = Tk()
    app = Monitor(master=root)
    app.mainloop()

if __name__ == '__main__':
	main()