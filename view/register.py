import json
import tkinter

from tkinter import *

import requests


class RegisterWindow(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self.logged_label = Label(self, text="")
        self.unavailable_username = Label(self, text="")
        self.geometry('700x300')
        self.title('Register')
        self.resizable(False, False)

        Label(self, text="                                ").grid(column=0, row=0)
        Label(self, text="                                ").grid(column=1, row=1)

        self.username_label = Label(self, text="Username")
        self.username_label.grid(column=2, row=0)
        self.username_entry = Text(self, bg="gray", height=1, width=20)
        self.username_entry.grid(column=2, row=1)

        Label(self, text="Password").grid(column=2, row=2)
        self.password_entry = Entry(self, )
        self.password_entry.configure(bg="gray", show="*")
        self.password_entry.place(height=1)
        self.password_entry.grid(column=2, row=3)

        Label(self, text="Name").grid(column=2, row=4)
        self.fullname_entry = Text(self, bg="gray", height=1, width=20)
        self.fullname_entry.grid(column=2, row=5)

        Label(self, text="Last name").grid(column=2, row=6)
        self.lastname_entry = Text(self, bg="gray", height=1, width=20)
        self.lastname_entry.grid(column=2, row=7)

        Label(self, text="Email").grid(column=2, row=8)
        self.email_entry = Text(self, bg="gray", height=1, width=25)
        self.email_entry.grid(column=2, row=9)

        self.empty_fields_label = Label(self, text="All fields must be filled.", foreground="red")
        Button(self, text="Register", command=self.store_user_request).grid(column=2, row=10)
        self.mainloop()

    def store_user_request(self):
        """
        Takes text from text-fields and adds them to dictionary and then passes it to request
        :return: None
        """
        username = self.username_entry.get("1.0", "end-1c")
        password = self.password_entry.get()
        fullname = self.fullname_entry.get("1.0", "end-1c")
        lastname = self.lastname_entry.get("1.0", "end-1c")
        email = self.email_entry.get("1.0", "end-1c")

        data = {"username": username,
                "password": password,
                "full_name": fullname,
                "last_name": lastname,
                "email": email,
                "friends": []}
        if not self.empty_fields_check():
            self.empty_fields_label.grid(column=1, row=10)
        else:
            r = requests.post("http://127.0.0.1:8000/register", data=json.dumps(data))
            if r.json() == "False":
                self.username_label.config(foreground="red")
                self.logged_label.grid_forget()
                self.empty_fields_label.grid_forget()
                self.create_unavailable_username_label()
            elif r.json() == "True":
                self.username_label.config(foreground="black")
                self.unavailable_username.grid_forget()
                self.empty_fields_label.grid_forget()
                self.create_successfully_registered_label()

    def create_unavailable_username_label(self):
        self.unavailable_username = Label(self, text="Username already in use", foreground="red")
        self.username_entry.delete("1.0", "end")
        self.unavailable_username.grid(column=3, row=1)
        self.mainloop()

    def create_successfully_registered_label(self):
        self.username_entry.delete("1.0", "end")
        self.password_entry.delete(0, "end")
        self.fullname_entry.delete("1.0", "end")
        self.lastname_entry.delete("1.0", "end")
        self.logged_label = Label(self, text="Successfully registered!", foreground="green")
        self.logged_label.grid(column=3, row=8, pady=18)
        self.mainloop()

    def empty_fields_check(self):
        if len(self.username_entry.get("1.0", "end")) > 1 and len(self.password_entry.get()) > 1 and \
                len(self.fullname_entry.get("1.0", "end")) > 1 and len(self.lastname_entry.get("1.0", "end")) > 1 and \
                len(self.email_entry.get("1.0", "end")) >= 10:
            return True
        else:
            return False
