import json
import tkinter.scrolledtext
from functools import partial

import requests
import tkinter
import threading
import websockets
import asyncio
from tkinter import *


class GroupChat(tkinter.Tk):

    def __init__(self, chat_id: str, chat_name: str, chat_admin: str, chat_desc: str, participants: list):
        super().__init__()
        self.id_label = Label(self, text="Id: " + chat_id)
        self.name_label = Label(self, text="Chat name: " + chat_name)
        self.host_label = Label(self, text="Host: " + chat_admin)
        self.desc_label = Label(self, text="About chat: " + chat_desc)
        self.chat_label = Label(self, text="Chat")
        self.scrolled_text = tkinter.scrolledtext.ScrolledText(self)
        self.text_field = Text(self, height=10)
        self.send_button = Button(self, text="Send", command=self.send_message_no_await)
        self.participant_text = Text(self, height=1, width=10)
        self.add_button = Button(self, text="+", command=partial(self.add_participant, chat_id))
        for participant in participants:
            Label(self, text=participant).pack(padx=1, pady=2, side=TOP, anchor=NE)

        threading.Thread(target=partial(self.receive_no_await, group_id=chat_id, username="TEST")).start()
        threading.Thread(target=self.create_group_window()).start()

    def create_group_window(self):
        self.resizable(False, False)
        self.id_label.pack(padx=1, pady=2, side=TOP, anchor=NW)
        self.name_label.pack(padx=1, pady=2, side=TOP, anchor=NW)
        self.host_label.pack(padx=1, pady=2, side=TOP, anchor=NW)
        self.desc_label.pack(padx=1, pady=2, side=TOP, anchor=NW)
        self.chat_label.pack(padx=1, pady=2, side=TOP, anchor=N)
        self.scrolled_text.pack(padx=1, pady=2, side=TOP, anchor=N)
        self.scrolled_text.config(state="disabled")
        self.text_field.pack()
        self.send_button.pack(padx=1, pady=2, side=LEFT, anchor=S)
        self.participant_text.pack(padx=1, pady=2, side=RIGHT, anchor=SE)
        self.add_button.pack(padx=1, pady=2, side=RIGHT, anchor=SE)
        self.mainloop()

    def receive_no_await(self, group_id: str, username: str):
        """
        Function that runs receive function with no await
        :return: None
        """
        asyncio.run(self.receive(group_id, username))

    async def receive(self, group_id: str, username: str):
        """
        Function for receiving messages from server
        :return:
        """
        async with websockets.connect(f"ws://localhost:8000/ws/{group_id}/{username}") as self.websocket:
            while True:
                try:
                    message = await self.websocket.recv()
                    self.scrolled_text.config(state='normal')
                    self.scrolled_text.insert('end', f"\n{str(message)}")
                    self.scrolled_text.yview('end')
                    self.scrolled_text.config(state='disabled')
                    self.scrolled_text.delete('1.0', 'end')
                except:
                    continue

    def send_message_no_await(self):
        """
        Function that is called on button press so that send_message function doesn't have to be awaited
        :return: None
        """
        written_message = self.text_field.get("1.0", 'end-1c')
        asyncio.run(self.send_message(written_message))

    async def send_message(self, message):
        """
        Requests message to server
        :param message: message that has been sent
        :return: None
        """
        # async with websockets.connect(f"ws://localhost:8000/ws/{username}") as websocket:
        await self.websocket.send(message)

    def add_participant(self, chat_id: str):
        username = self.participant_text.get("1.0", "end-1c")
        user_info = {"chat_id": chat_id,
                     "username": username}
        requests.post("http://127.0.0.1:8000/add_user_to_gc", data=json.dumps(user_info))
