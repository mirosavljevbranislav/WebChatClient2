import asyncio
from functools import partial

import websockets
import threading
import requests

import tkinter
import tkinter.scrolledtext
from tkinter import *


class PrivateChat(tkinter.Tk):

    def __init__(self, chat_id: str, username: str):
        super().__init__()
        self.scrolled_text = tkinter.scrolledtext.ScrolledText(self)
        self.text_field = Text(self, height=10)
        self.send_button = Button(self, text="Send", command=self.send_message_no_await)
        group_messages = requests.get("http://127.0.0.1:8000/get_private_messages", params={"chat_id": chat_id}).json()
        for message in group_messages:
            self.scrolled_text.config(state='normal')
            self.scrolled_text.insert('end', f"\n{message}")
            self.scrolled_text.yview('end')
            self.scrolled_text.config(state='disabled')
        threading.Thread(target=partial(self.receive_no_await, group_id=chat_id, username=username)).start()
        self.create_group_window()

    def create_group_window(self):
        self.resizable(False, False)
        self.scrolled_text.pack(padx=1, pady=2, side=TOP, anchor=N)
        self.scrolled_text.config(state="disabled")
        self.text_field.pack()
        self.send_button.pack(padx=1, pady=2, anchor=S)

        self.mainloop()

    def receive_no_await(self, group_id: str, username: str):
        """
        Function that runs receive function with no await
        :return: None
        """
        asyncio.run(self.receive(group_id, username))

    async def receive(self, chat_id: str, username: str):
        """
        Function for receiving messages from server
        :return:
        """
        async with websockets.connect(f"ws://localhost:8000/ws/private_chat/{chat_id}/{username}") as self.websocket:
            while True:
                try:
                    message = await self.websocket.recv()
                    self.scrolled_text.config(state='normal')
                    self.scrolled_text.insert('end', f"\n{str(message)}")
                    self.scrolled_text.yview('end')
                    self.scrolled_text.config(state='disabled')
                    self.text_field.delete('1.0', 'end')
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
        await self.websocket.send(message)
