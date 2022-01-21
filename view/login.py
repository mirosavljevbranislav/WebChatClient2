import json
import tkinter
from tkinter import *

import requests

from view import home_page
from view.global_chat import GlobalPage

from uuid import uuid4


class LoginWindow(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self.geometry('700x250')
        self.title('Login')
        self.resizable(False, False)

        Label(self, text="Name").pack()
        self.username_text = Text(self, bg="gray", height=1, width=20)
        self.username_text.pack()

        Label(self, text="Password").pack()
        self.password_text = Entry(self, )
        self.password_text.configure(bg="gray", show="*")
        self.password_text.place(height=1)
        self.password_text.pack()

        Button(self, text="Forgot password", command=self.forgot_password).place(anchor='e', relx=0.85, rely=0.3)

        Button(self, text="Login", command=self.send_login_info).pack()

        self.forgot_password_label = Label(self, text="Username: ")
        self.forgot_password_text = Text(self, height=1, width=10)
        self.forgot_password_button = Button(self, text="Send recovery mail", command=self.hide_forgot_password)

        # Recovery part

        self.recovery_token_label = Label(self, text="Token: ")
        self.recovery_token_text = Text(self, height=1, width=20)
        self.recovery_token_button = Button(self, text="Confirm", command=self.reset_password)

        # Successful recovery

        self.successful_recovery_label = Label(self, text="Please enter your username")
        self.successful_recovery_text = Text(self, height=1, width=20)
        self.new_password_label = Label(self, text="Enter your new password")
        self.new_password_text = Entry(self)
        self.new_password_button = Button(self, text="Confirm", command=self.send_new_password)

        home_page.destroy_home_window()
        self.mainloop()

    def send_login_info(self):
        """
        Upon login sends info of user to server to check if it's right
        :return: None
        """
        username = self.username_text.get("1.0", "end-1c")
        password = self.password_text.get()

        data = {"username": username, "password": password}

        request = requests.post("http://127.0.0.1:8000/login", data=json.dumps(data))
        if request:
            json_request = request.json()
            access_token = json_request['access_token']
            logged_user = requests.get(f"http://127.0.0.1:8000/get_logged_user/{access_token}",
                                       headers={'WWW-Authorization': f'Bearer <{access_token}>'})
            self.destroy()
            username = logged_user.json()['username']
            first_name = logged_user.json()['full_name']
            last_name = logged_user.json()['last_name']

            global_page = GlobalPage(username=username, first_name=first_name, last_name=last_name)
            global_page.update()
            global_page.update_idletasks()
        else:
            self.wrong_info_popup()

    def wrong_info_popup(self):
        popup = Toplevel(self)
        popup.geometry("400x70")
        popup.title("Wrong info")
        Label(popup, text="Incorrect username or password", font='Mistral 12 bold').pack()
        Button(popup, text="Okay", command=popup.destroy).pack()
        self.mainloop()

    def forgot_password(self):
        self.forgot_password_label.place(anchor='e', relx=0.67, rely=0.45)
        self.forgot_password_text.place(anchor='e', relx=0.95, rely=0.45, width=200)
        self.forgot_password_button.place(anchor='e', relx=0.85, rely=0.6)

    def hide_forgot_password(self):
        recovery_username = self.forgot_password_text.get("1.0", "end-1c")
        user = requests.get("http://127.0.0.1:8000/get_user", params={"username": recovery_username}).json()
        self.recovery_token = str(uuid4())
        recovery_data = {"recipient": user['email'],
                         "recovery_token": self.recovery_token}
        requests.post("http://127.0.0.1:8000/send_mail", data=json.dumps(recovery_data))
        self.forgot_password_label.place_forget()
        self.forgot_password_text.place_forget()
        self.forgot_password_button.place_forget()
        self.recovery_token_label.place(anchor='e', relx=0.7, rely=0.45)
        self.recovery_token_text.place(anchor='e', relx=0.95, rely=0.45)
        self.recovery_token_button.place(anchor='e', relx=0.85, rely=0.6)

    def reset_password(self):
        if self.recovery_token == self.recovery_token_text.get("1.0", "end-1c"):
            self.recovery_token_label.place_forget()
            self.recovery_token_text.place_forget()
            self.recovery_token_button.place_forget()

            self.successful_recovery_label.place(anchor='e', relx=0.65, rely=0.65)
            self.successful_recovery_text.place(anchor='e', relx=0.9, rely=0.65)
            self.new_password_label.place(anchor='e', relx=0.65, rely=0.75)
            self.new_password_text.place(anchor='e', relx=0.9, rely=0.75, height=25)
            self.new_password_text.configure(show="*")
            self.new_password_button.place(anchor='e', relx=0.85, rely=0.9)
        else:
            self.recovery_token_label.place_forget()
            self.recovery_token_text.place_forget()
            self.recovery_token_button.place_forget()
            self.forgot_password_label.place(anchor='e', relx=0.65, rely=0.45)
            self.forgot_password_text.place(anchor='e', relx=0.95, rely=0.45, width=200)
            self.forgot_password_button.place(anchor='e', relx=0.85, rely=0.6)
            self.forgot_password_text.delete('1.0', 'end')
            self.forgot_password_text.insert("end", "Try again, wrong code!")

    def send_new_password(self):
        new_data = {"username": self.successful_recovery_text.get("1.0", "end-1c"),
                    "new_password": self.new_password_text.get()}
        requests.put("http://127.0.0.1:8000/restore_password", data=json.dumps(new_data))
        self.successful_recovery_label.place_forget()
        self.successful_recovery_text.place_forget()
        self.new_password_label.place_forget()
        self.new_password_text.place_forget()
        self.new_password_button.place_forget()
