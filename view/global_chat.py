import json
import threading
import tkinter
import tkinter.scrolledtext

import asyncio

import requests
import websockets

from functools import partial

from tkinter import *

from .group_chat import GroupChat


class GlobalPage(tkinter.Tk):

    def __init__(self, username, first_name, last_name):
        super().__init__()
        self.username_label = Label(self, text=f"Username: {username}")
        self.name_label = Label(self, text=f"Name: {first_name}")
        self.last_name_label = Label(self, text=f"Last name: {last_name}")

        self.new_group_name_text = Text(self, height=1, width=30)
        self.new_group_desc_text = Text(self, height=5, width=20)
        self.too_long_desc = Label(self, text="Description too long...")

        self.chat_area_text = tkinter.scrolledtext.ScrolledText(self)
        self.send_message_text = Text(self, height=5)
        self.send_button = Button(self, text="Send", command=self.send_message_no_await)

        threading.Thread(target=partial(self.receive_no_await, username)).start()
        threading.Thread(target=self.gui_creation(username=username)).start()

    def gui_creation(self, username):
        self.geometry("1200x800")
        self.title("Global chat")
        self.resizable(False, False)

        self.username_label.pack(padx=1, pady=2, side=TOP, anchor=NW)
        self.name_label.pack(padx=1, pady=2, side=TOP, anchor=NW)
        self.last_name_label.pack(padx=1, pady=2, side=TOP, anchor=NW)

        Label(self, text="New group: ").pack(padx=1, pady=2, side=TOP, anchor=NW)
        self.new_group_name_text.pack(padx=1, pady=2, side=TOP, anchor=NW)

        Label(self, text="Description: ").pack(padx=1, pady=2, side=TOP, anchor=NW)
        self.new_group_desc_text.pack(padx=1, pady=2, side=TOP, anchor=NW)

        Button(self, text="+", command=partial(self.create_group_frame, username)).pack(padx=1, pady=2, side=TOP, anchor=NW)

        self.chat_area_text.place(anchor='n', relx=0.5, rely=0.001)
        self.chat_area_text.config(state="disabled")

        self.send_button.pack(padx=1, pady=2, side=BOTTOM, anchor=S)
        self.send_message_text.pack(padx=1, pady=2, side=BOTTOM, anchor=S)

        groups = requests.get("http://127.0.0.1:8000/get_all_gc", params={"username": username})
        group_list = list(groups.json())

        if len(list(group_list)) > 0:
            for i in range(len(group_list)):
                self.parent_frame = LabelFrame(self, text=str(group_list[i]['name']) + "-" + username, cursor="hand2")
                self.parent_frame.bind("<Button-1>", lambda e: GroupChat(chat_id=group_list[i]["_id"],
                                                                         chat_name=group_list[i]['name'],
                                                                         chat_admin=group_list[i]['admin'],
                                                                         chat_desc=group_list[i]['description'],
                                                                         participants=group_list[i]['users']))
                self.parent_frame.pack(padx=1, pady=2, side=TOP, anchor=NW)
                Label(self.parent_frame, text=group_list[i]['description'], wraplength=250).pack()

        self.mainloop()

    def create_group_frame(self, group_admin: str):
        """
        On + button press, it creates new LabelFrame that represents group
        :param group_admin: name of group admin
        :return: None
        """
        if len(self.new_group_desc_text.get("1.0", 'end-1c')) < 50:
            group_name = self.new_group_name_text.get('1.0', 'end-1c')
            group_desc = self.new_group_desc_text.get('1.0', 'end-1c')
            self.parent_frame = LabelFrame(self,
                                           text=group_name + "-" + group_admin,
                                           cursor="hand2")

            self.parent_frame.pack(padx=1,
                                   pady=2,
                                   side=TOP,
                                   anchor=NW)
            Label(self.parent_frame,
                  text=group_desc).pack()
            data = {"admin": group_admin,
                    "name": group_name,
                    "description": group_desc,
                    "users": [],
                    "websocket_list": []}
            requests.post("http://127.0.0.1:8000/store_gc", data=json.dumps(data))
            # store_user_data = {"username": data['admin'],
            #                    "chat_id": store_group['chat_id']}
            # requests.post("http://127.0.0.1:8000/add_user_to_gc", data=json.dumps(store_user_data))
            self.too_long_desc.destroy()
        else:
            self.too_long_desc.place(anchor='e', relx=0.16, rely=0.33)

    def receive_no_await(self, username: str):
        """
        Function that runs receive function with no await
        :return: None
        """
        asyncio.run(self.receive(username=username))

    def send_message_no_await(self):
        """
        Function that is called on button press so that send_message function doesn't have to be awaited
        :return: None
        """
        written_message = self.send_message_text.get("1.0", 'end-1c')
        asyncio.run(self.send_message(written_message))

    async def receive(self, username: str):
        """
        Function for receiving messages from server
        :return:
        """
        async with websockets.connect(f"ws://localhost:8000/ws/{username}") as self.websocket:
            while True:
                try:
                    message = await self.websocket.recv()
                    self.chat_area_text.config(state='normal')
                    self.chat_area_text.insert('end', f"\n{str(message)}")
                    self.chat_area_text.yview('end')
                    self.chat_area_text.config(state='disabled')
                    self.send_message_text.delete('1.0', 'end')
                except:
                    continue

    async def send_message(self, message: str):
        """
        Requests message to server
        :param message: message that has been sent
        :return: None
        """
        # async with websockets.connect(f"ws://localhost:8000/ws/{username}") as websocket:
        await self.websocket.send(message)
