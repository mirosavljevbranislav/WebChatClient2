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
from .private_chat import PrivateChat


class GlobalPage(tkinter.Tk):

    def __init__(self, username, first_name, last_name):
        super().__init__()

        # Info

        self.username_label = Label(self, text=f"Username: {username}")
        self.name_label = Label(self, text=f"Name: {first_name}")
        self.last_name_label = Label(self, text=f"Last name: {last_name}")

        # Groups

        self.new_group_label = Label(self, text="New group: ")
        self.description_label = Label(self, text="Description: ")
        self.add_group_button = Button(self)
        self.new_group_name_text = Text(self, height=1, width=30)
        self.new_group_desc_text = Text(self, height=5, width=20)
        self.too_long_desc = Label(self, text="Description too long...")

        # Chat

        self.chat_area_text = tkinter.scrolledtext.ScrolledText(self)
        self.send_message_text = Text(self, height=5)
        self.send_button = Button(self, text="Send", command=self.send_message_no_await)

        # Friends
        self.add_friend_button = Button(self)
        self.add_friend_label = Label(self, text="Add friend", pady=0.1)
        self.add_friend_text = Text(self, width=10, height=1, padx=0.5)

        global_messages = requests.get("http://127.0.0.1:8000/get_global_messages").json()
        for message in global_messages:
            self.chat_area_text.config(state='normal')
            self.chat_area_text.insert('end', f"\n{message}")
            self.chat_area_text.yview('end')
            self.chat_area_text.config(state='disabled')

        threading.Thread(target=partial(self.receive_no_await, username)).start()
        threading.Thread(target=self.gui_creation(username=username)).start()

    def gui_creation(self, username):

        # Chat part

        self.geometry("1200x800")
        self.title("Global chat")
        self.resizable(False, False)

        self.username_label.pack(padx=1, pady=2, side=TOP, anchor=NW)
        self.name_label.pack(padx=1, pady=2, side=TOP, anchor=NW)
        self.last_name_label.pack(padx=1, pady=2, side=TOP, anchor=NW)

        # Groups part

        self.new_group_label.pack(padx=1, pady=2, side=TOP, anchor=NW)
        self.new_group_name_text.pack(padx=1, pady=2, side=TOP, anchor=NW)

        self.description_label.pack(padx=1, pady=2, side=TOP, anchor=NW)
        self.new_group_desc_text.pack(padx=1, pady=2, side=TOP, anchor=NW)

        self.add_group_button.config(text="+", command=partial(self.create_group_frame, username))
        self.add_group_button.pack(padx=1, pady=2, side=TOP, anchor=NW)

        self.chat_area_text.place(anchor='n', relx=0.5, rely=0.001)
        self.chat_area_text.config(state="disabled")

        self.send_button.pack(padx=1, pady=2, side=BOTTOM, anchor=S)
        self.send_message_text.pack(padx=1, pady=2, side=BOTTOM, anchor=S)

        groups = requests.get("http://127.0.0.1:8000/get_all_gc", params={"username": username})
        group_list = list(groups.json())

        if len(list(group_list)) >= 0:
            for i in range(len(group_list)):
                self.parent_frame = LabelFrame(self)
                self.parent_frame.config(text=str(group_list[i]['name']) + "-" + group_list[i]['admin'],
                                         cursor="hand2")
                self.parent_frame.bind("<Button-1>", lambda e: GroupChat(group_id=group_list[i]["_id"],
                                                                         chat_name=group_list[i]['name'],
                                                                         chat_admin=group_list[i]['admin'],
                                                                         chat_desc=group_list[i]['description'],
                                                                         participants=group_list[i]['users'],
                                                                         username=username))
                self.parent_frame.pack(padx=1, pady=2, side=TOP, anchor=NW)
                Label(self.parent_frame, text=group_list[i]['description'], wraplength=250).pack()

        # Friends part

        self.add_friend_label.place(anchor='e', relx=0.98, rely=0.02)
        self.add_friend_button.config(text="+", command=partial(self.add_friend, username))
        self.add_friend_button.place(anchor='e', relx=0.9, rely=0.06)
        self.user_exists_label = Label(self, text="User is already in your friends,\n or it does not exists.")
        self.add_friend_text.place(anchor='e', relx=0.98, rely=0.06)

        user = requests.get("http://127.0.0.1:8000/get_user", params={"username": username}).json()
        user_friends = user['friends']

        all_chats = requests.get("http://127.0.0.1:8000/get_private_chat", params={"username": username,
                                                                                   "friend": user_friends[0]})
        all_chats_list = all_chats.json()

        if len(user_friends) >= 0:
            for j in range(len(user_friends)):
                self.friend_frame = LabelFrame(self)
                self.friend_frame.config(text=user_friends[j],
                                         cursor="hand2")

                self.friend_frame.pack(padx=1,
                                       pady=2,
                                       side=TOP,
                                       anchor=NE)

                self.friend_frame.bind("<Button-1>",
                                       lambda e: PrivateChat(chat_id=all_chats_list[0]['_id'],
                                                             username=username))
                friend = requests.get("http://127.0.0.1:8000/get_user",
                                      params={"username": user_friends[j]}).json()

                Button(self.friend_frame, text="Unfriend", command=partial(self.remove_friend,
                                                                           friend_to_remove=self.friend_frame.cget("text"),
                                                                           username=username)).pack()
                Label(self.friend_frame, text="Name: " + friend['full_name']
                                              + "\n" +
                                              "Last name: " + friend['last_name']).pack()
        self.mainloop()

    def add_friend(self, username: str):
        """
        Function that sends request to add friend to database, and creates LabelFrame with friend's info
        :return: None
        """
        friend_username = self.add_friend_text.get('1.0', 'end-1c')

        user_already_friend = requests.get("http://127.0.0.1:8000/check_user", params={"username": username,
                                                                                       "friend": friend_username})
        if not user_already_friend.json():
            add_user = requests.post("http://127.0.0.1:8000/add_friend",
                                     params={"username": friend_username,
                                             "current_user": username})
            user_info = add_user.json()
            private_chat_info = {"participants": [username, friend_username],
                                 "messages": []}
            requests.post("http://127.0.0.1:8000/store_private_chat",
                          data=json.dumps(private_chat_info))

            self.friend_frame = LabelFrame(self, text=user_info['username'],
                                           cursor="hand2")
            self.friend_frame.pack(padx=1,
                                   pady=2,
                                   side=TOP,
                                   anchor=NE)

            Label(self.friend_frame, text="Name: " + user_info['full_name']
                                          + "\n" +
                                          "Last name: " + user_info['last_name']).pack()
            self.add_friend_text.delete("1.0", "end")
            self.hide_user_exists_label()
        elif user_already_friend.json():
            self.add_friend_text.delete("1.0", "end")
            self.user_exists_label.place(anchor='e', relx=0.97, rely=0.12)

    def hide_user_exists_label(self):
        self.user_exists_label.place_forget()

    def remove_friend(self, friend_to_remove: str, username: str):
        requests.delete("http://127.0.0.1:8000/remove_friend", params={"friend_to_remove": friend_to_remove,
                                                                       "username": username})

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
            Label(self.parent_frame, text=group_desc).pack()

            data = {"admin": group_admin,
                    "name": group_name,
                    "description": group_desc,
                    "users": [],
                    "messages": []}
            requests.post("http://127.0.0.1:8000/store_gc",
                          data=json.dumps(data))

            self.too_long_desc.place_forget()
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
        await self.websocket.send(message)
