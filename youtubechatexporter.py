import tkinter as tk
from tkinter import ttk, font
import pytchat
import threading
import queue
import requests
import sv_ttk
import re
import os
import sys

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

class YouTubeChatViewer:
    def __init__(self, master):
        self.master = master
        master.title("YouTube Chat Viewer")

        self.video_id_label = ttk.Label(master, text="Enter YouTube Video ID:")
        self.video_id_label.pack(pady=(10, 0))

        self.video_id_entry = ttk.Entry(master, width=30)
        self.video_id_entry.pack(pady=(0, 6))

        self.start_button = ttk.Button(master, text="Start Viewing", command=self.start_viewing)
        self.start_button.pack()
    
        self.font_size_label = ttk.Label(master, text="Font Size:")
        self.font_size_label.pack()

        self.font_size_var = tk.IntVar(value=11)
        self.font_size_slider = ttk.Scale(master, from_=4, to=24, variable=self.font_size_var, orient=tk.HORIZONTAL, command=self.update_font_size)
        self.font_size_slider.pack()

        self.filter_var = tk.BooleanVar(value=False)
        self.filter_checkbox = ttk.Checkbutton(master, text="Filter Profanity", variable=self.filter_var)
        self.filter_checkbox.pack()

        self.hide_emojis_var = tk.BooleanVar(value=False)
        self.hide_emojis_checkbox = ttk.Checkbutton(master, text="Hide Emojis", variable=self.hide_emojis_var)
        self.hide_emojis_checkbox.pack()

        self.text_widget = tk.Text(master, wrap=tk.WORD, width=80, height=20, state=tk.DISABLED, borderwidth=0, highlightthickness=0)
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(master, command=self.text_widget.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_widget.config(yscrollcommand=self.scrollbar.set)

        self.user_name_font = font.Font(family='Inter SemiBold', size=self.font_size_var.get())
        self.message_font = font.Font(family='Inter Regular', size=self.font_size_var.get())

        self.text_widget.tag_configure('message_tag', font=self.message_font, foreground='black')
        self.text_widget.tag_configure('white_text', font=self.message_font, foreground='white')

        self.chat = None
        self.update_queue = queue.Queue()
        self.update_thread = None
        self.scroll_thread = None
        self.stop_update_thread = threading.Event()

        self.author_colors = {}
        self.predefined_colors = [
            "#FF0000", "#B22222", "#FF4500", "#FF7F50", "#F8FF3C", "#DAA820", "#00FF7F", "#008000", "#1E90FF", "#00FFEC", "#7C7CE1", "#8A2BE2", "#D66BFC", "#FF00B5"
        ]

        master.bind("<Configure>", self.adjust_message_box_size)

    def start_viewing(self):
        video_id = self.video_id_entry.get()
        if video_id:
            self.chat = pytchat.create(video_id=video_id)
            self.stop_update_thread.clear()
            self.update_thread = threading.Thread(target=self.update_chat_messages)
            self.scroll_thread = threading.Thread(target=self.continuous_scroll)
            self.update_thread.start()
            self.scroll_thread.start()

    def update_chat_messages(self):
        while not self.stop_update_thread.is_set():
            if self.chat and self.chat.is_alive():
                for c in self.chat.get().sync_items():
                    author_name = c.author.name.rstrip()
                    message_text = c.message

                    if self.filter_var.get():
                        message_text = self.filter_profanity(message_text)

                    if self.hide_emojis_var.get():
                        message_text = self.remove_emojis(message_text)

                    if message_text != "":
                        color = self.get_author_color(author_name)

                        tag_name = f'{author_name.replace(" ", "_")}_tag'
                        self.text_widget.tag_configure(tag_name, font=self.user_name_font, foreground=color)
                        self.text_widget.config(state=tk.NORMAL)
                        self.text_widget.insert(tk.END, f"{author_name} ", (tag_name,))
                        self.text_widget.insert(tk.END, f" {message_text}\n", ('message_tag', 'white_text'))
                        self.text_widget.config(state=tk.DISABLED)

                        num_lines = int(self.text_widget.index('end-1c').split('.')[0])
                        max_lines = int(self.text_widget.cget('height'))
                        if num_lines > max_lines:
                            first_visible_line = num_lines - max_lines
                            self.text_widget.config(state=tk.NORMAL)
                            self.text_widget.delete(1.0, f"{first_visible_line}.0")
                            self.text_widget.config(state=tk.DISABLED)

                self.text_widget.yview(tk.END)
                self.master.after(10, self.process_update_queue)
                self.text_widget.yview(tk.END)
            else:
                self.stop_update_thread.set()

    def continuous_scroll(self):
            while not self.stop_update_thread.is_set():
                try: 
                    self.text_widget.yview(tk.END)
                    self.text_widget.see(tk.END)
                    self.master.update_idletasks()
                    self.master.update()
                    self.master.after(25) # slight delay to prevent cpu overconsumption
                except RuntimeError:
                    pass # program most likely closed

    def filter_profanity(self, message):
        profanity_list_url = "https://raw.githubusercontent.com/dsojevic/profanity-list/main/en.txt" # oh god
        response = requests.get(profanity_list_url)
        profanity_list = response.text.splitlines()

        for word in profanity_list:
            if word.lower() in message.lower():
                message = message.replace(word, '*' * len(word)) # option to change symbol should be added later

        return message

    def remove_emojis(self, message):
        return re.sub(r':[a-zA-Z0-9_\'-]+:', '', message)

    def process_update_queue(self):
        while not self.update_queue.empty():
            message = self.update_queue.get()
            self.text_widget.insert(tk.END, message)

        self.text_widget.update_idletasks()

    def stop_update_thread(self):
        if self.update_thread and self.update_thread.is_alive():
            self.stop_update_thread.set()
            self.update_thread.join()

    def get_author_color(self, author_name):
        if author_name not in self.author_colors:
            hash_value = hash(author_name)
            index = abs(hash_value) % len(self.predefined_colors)
            color = self.predefined_colors[index]

            self.author_colors[author_name] = color

        return self.author_colors[author_name]

    def adjust_message_box_size(self, event):
        new_width = max(self.master.winfo_width() // 10, 80)
        new_height = max(self.master.winfo_height() // 30, 20)

        self.text_widget.config(width=new_width, height=new_height)

    def update_font_size(self, value):
        size = round(float(value))
        self.user_name_font.configure(size=size)
        self.message_font.configure(size=size)

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeChatViewer(root)
    sv_ttk.set_theme("dark")
    root.iconbitmap(application_path + "\\icon.ico")
    root.mainloop()
