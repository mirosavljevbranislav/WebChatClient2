from tkinter import *
from view.login import LoginWindow
from view.register import RegisterWindow

tkWindow = Tk()


def open_register_window():
    rw = RegisterWindow()
    rw.update()
    rw.update_idletasks()


def open_login_window():
    lw = LoginWindow()
    lw.update()
    lw.update_idletasks()


def destroy_home_window():
    tkWindow.destroy()


def create_home_page():
    tkWindow.geometry('700x250')
    tkWindow.title('WebChatApp')

    Button(tkWindow, text="Register", command=open_register_window, height=1, width=15).pack()
    Button(tkWindow, text="Login", command=open_login_window, height=1, width=15).pack()

    tkWindow.mainloop()
