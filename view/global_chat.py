import json
import threading
import tkinter
import tkinter.scrolledtext

import asyncio

import requests
import websockets

from functools import partial

from tkinter import *


class GlobalPage(tkinter.Tk):

    def __init__(self, username, first_name, last_name):
        super().__init__()
        self.username_label = Label(self, text=f"Username: {username}")
        self.name_label = Label(self, text=f"Name: {first_name}")
        self.last_name_label = Label(self, text=f"Last name: {last_name}")

        self.new_group_name = Text(self, height=1, width=30)
        self.new_group_desc = Text(self, height=5, width=20)

        self.text_area = tkinter.scrolledtext.ScrolledText(self)
        self.input_area = Text(self, height=5)
        self.send_button = Button(self, text="Send", command=partial(self.send_message_no_await, username))

        threading.Thread(target=self.receive_no_await).start()
        threading.Thread(target=self.gui_creation(username=username)).start()

    def gui_creation(self, username):
        threading.Thread(target=self.load_group_chats(group_admin=username)).start()
        self.geometry("1200x800")
        self.title("Global chat")
        self.resizable(False, False)

        self.username_label.pack(padx=1, pady=2, side=TOP, anchor=NW)
        self.name_label.pack(padx=1, pady=2, side=TOP, anchor=NW)
        self.last_name_label.pack(padx=1, pady=2, side=TOP, anchor=NW)

        Label(self, text="New group: ").pack(padx=1, pady=2, side=TOP, anchor=NW)
        self.new_group_name.pack(padx=1, pady=2, side=TOP, anchor=NW)

        Label(self, text="Description: ").pack(padx=1, pady=2, side=TOP, anchor=NW)
        self.new_group_desc.pack(padx=1, pady=2, side=TOP, anchor=NW)

        Button(self, text="+", command=partial(self.create_group_frame, username)).pack(padx=1, pady=2, side=TOP, anchor=NW)

        self.text_area.place(anchor='n', relx=0.5, rely=0.001)
        self.text_area.config(state="disabled")

        self.input_area.place(anchor='sw', rely=1)

        self.send_button.place(anchor='s', relx=0.6, rely=0.96)

        self.mainloop()

    def load_group_chats(self, group_admin: str):
        print("This happened")
        groups = requests.get("http://127.0.0.1:8000/get_all_gc", params={"username": group_admin})
        print(groups.text)
        if len(list(groups)) > 0:
            for i in range(len(list(groups))):
                parent_frame = LabelFrame(self, text="TEST" + "-" + group_admin)
                parent_frame.pack(padx=1, pady=2, side=TOP, anchor=NW)
                Label(parent_frame, text="TEST").pack()

    def create_group_frame(self, group_admin: str):
        """
        On + button press, it creates new LabelFrame that represents group
        :param group_admin: name of group admin
        :return: None
        """
        group_name = self.new_group_name.get('1.0', 'end-1c')
        group_desc = self.new_group_desc.get('1.0', 'end-1c')
        parent_frame = LabelFrame(self, text=group_name + "-" + group_admin)
        parent_frame.pack(padx=1, pady=2, side=TOP, anchor=NW)
        Label(parent_frame, text=group_desc).pack()
        data = {"admin": group_admin,
                "name": group_name,
                "description": group_desc,
                "users": []}
        requests.post("http://127.0.0.1:8000/store_gc", data=json.dumps(data))

    def receive_no_await(self):
        """
        Function that runs receive function with no await
        :return: None
        """
        asyncio.run(self.receive())

    def send_message_no_await(self, username: str):
        """
        Function that is called on button press so that send_message function doesn't have to be awaited
        :return: None
        """
        written_message = self.input_area.get("1.0", 'end-1c')
        asyncio.run(request_message(written_message, username=username))

    async def receive(self):
        """
        Function for receiving messages from server
        :return:
        """
        async with websockets.connect("ws://localhost:8000/ws/{username}") as websocket:
            while True:
                try:
                    message = await websocket.recv()
                    self.text_area.config(state='normal')
                    self.text_area.insert('end', f"\n{str(message)}")
                    self.text_area.yview('end')
                    self.text_area.config(state='disabled')
                    self.input_area.delete('1.0', 'end')
                except:
                    continue


async def request_message(message: str, username: str):
    """
    Requests message to server
    :param message: message that has ben sent
    :param username: username of user
    :return: None
    """
    async with websockets.connect(f"ws://localhost:8000/ws/{username}") as websocket:
        await websocket.send(message)
