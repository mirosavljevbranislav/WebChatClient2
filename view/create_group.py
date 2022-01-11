import tkinter
from tkinter import *


class GroupChat(tkinter.Tk):
    def __init__(self, group_admin: str):
        super().__init__()
        self.geometry("300x200")
        self.title("Create group")
        self.resizable(False, False)

        Label(self, text="Admin: " + group_admin).pack()
        Label(self, text="Group name").pack()
        Text(self, height=1).pack()
        Label(self, text="Group description").pack()
        Text(self, height=2).pack()
        Button(self, text="Confirm").pack()

        self.mainloop()

    def destroy_window(self):
        self.destroy()
