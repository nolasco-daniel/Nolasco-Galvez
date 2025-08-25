import tkinter as tk
from tkinter import ttk
from core import ChatbotCore
from datetime import datetime
from PIL import Image, ImageTk
import os


class ChatDisplay:
    def __init__(self, parent, user_img, bot_img):
        self.user_img = user_img
        self.bot_img = bot_img
        self.typing_label = None
        
        self.canvas = tk.Canvas(parent, bg="#17153B", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.canvas.yview)
        self.msg_frame = tk.Frame(self.canvas, bg="#17153B")

        self.msg_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.msg_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def append_message(self, sender, msg):
        is_user = sender == "🧑 You"
        row = tk.Frame(self.msg_frame, bg="#17153B")
        
        bubble_config = {
            "text": msg, "font": ("Segoe UI", 11), "padx": 12, "pady": 8, 
            "wraplength": 250, "justify": tk.LEFT, "relief": "flat"
        }
        
        time_label = tk.Label(
            row, text=datetime.now().strftime("%I:%M %p"),
            font=("Segoe UI", 8), bg="#17153B", fg="#999999"
        )
        
        if is_user:
            row.pack(fill=tk.X, pady=5, padx=10)
            if self.user_img:
                tk.Label(row, image=self.user_img, bg="#17153B").pack(side=tk.RIGHT, anchor='s')
            bubble = tk.Label(row, **bubble_config, bg="#beb2f0", fg="black")
            bubble.pack(side=tk.RIGHT, padx=10)
            time_label.pack(side=tk.RIGHT, anchor='s')
        else:
            row.pack(fill=tk.X, pady=5, padx=10)
            if self.bot_img:
                tk.Label(row, image=self.bot_img, bg="#17153B").pack(side=tk.LEFT, anchor='s')
            bubble = tk.Label(row, **bubble_config, bg="#725CAD", fg="white")
            bubble.pack(side=tk.LEFT, padx=10)
            time_label.pack(side=tk.LEFT, anchor='s')

        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def show_typing_indicator(self):
        self.hide_typing_indicator()
        
        self.typing_label = tk.Label(
            self.msg_frame, text="🤖 Bot is typing...",
            font=("Segoe UI", 10, "italic"),
            bg="#17153B", fg="#999999"
        )
        self.typing_label.pack(fill=tk.X, pady=5, padx=20, anchor='w')
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def hide_typing_indicator(self):
        if self.typing_label:
            self.typing_label.destroy()
            self.typing_label = None


class ChatInput:
    def __init__(self, parent, send_callback):
        self.frame = tk.Frame(parent, bg="white", height=70)
        self.frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=10)
        
        self.entry = tk.Entry(self.frame, font=("Segoe UI", 11), bg="#9B7EBD", fg="white", relief="flat", insertbackground="white")
        self.entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipady=8, pady=5, padx=10)
        self.entry.bind("<Return>", lambda e: send_callback())

        send_button = tk.Button(
            self.frame, text="➤", font=("Segoe UI", 14, "bold"),
            command=send_callback, bg="#441752", fg="white", relief="flat"
        )
        send_button.pack(side=tk.RIGHT, padx=10, ipadx=5)

    def get_input(self):
        return self.entry.get()

    def clear_input(self):
        self.entry.delete(0, tk.END)


class ChatbotGUI:
    def __init__(self, core: ChatbotCore):
        self.core = core
        self.window = tk.Tk()
        self.window.title("Chatbot")
        self.window.geometry("400x700")
        self.window.configure(bg="#17153B")
        self.window.resizable(True, True)

        self.user_img = self.load_profile_image(os.path.join("Images", "user-profile.jpg"))
        self.bot_img = self.load_profile_image(os.path.join("Images", "bot-profile.jpg"))
        self.header_bot_img = self.load_profile_image(os.path.join("Images", "bot-profile.jpg"), (24, 24))

        self.show_welcome_screen()
        self.window.mainloop()

    def load_gif_frames(self, gif_path):
        frames = []
        try:
            img = Image.open(gif_path)
            while True:
                frames.append(ImageTk.PhotoImage(img.copy()))
                img.seek(len(frames))  
        except EOFError:
            pass  
        except Exception as e:
            print(f"Error loading GIF: {e}")
        return frames if frames else None

    def show_welcome_screen(self):
        self.welcome_frame = tk.Frame(self.window, bg="#fde2fd")
        self.welcome_frame.pack(fill=tk.BOTH, expand=True)
       
        self.animating_gif = True
        
        tk.Label(
            self.welcome_frame, text="Welcome Hooman!", font=("Lucida Console", 24, "bold"), bg="#fde2fd"
        ).pack(pady=(60, 20))

        gif_path = os.path.join("Animations", "chat-bot_animation.gif")
        self.gif_img = self.load_gif_frames(gif_path)
        self.gif_label = tk.Label(self.welcome_frame, bg="#F8D9F8")
        self.gif_label.pack(pady=5)
        if self.gif_img:
            self.animate_gif(0)
        else:
            self.gif_label.config(text="[GIF not found]")

        tk.Label(
            self.welcome_frame,
            text="Chat with me,\nI'll be here whenever you need me!",
            font=("Lucida Console", 12), bg="#fde2fd"
        ).pack(pady=(20, 30), padx=20)

        tk.Button(
            self.welcome_frame, text="Let's Chat!", font=("Lucida Console", 14, "bold"),
            bg="#BCA7F2", fg="#17153B", activebackground="#A48BE0", activeforeground="#fde2fd",
            relief="flat", padx=18, pady=10, command=self.start_chat_interface
        ).pack(pady=10)

    def animate_gif(self, idx):
        if self.gif_img and self.animating_gif:
            frame = self.gif_img[idx]
            self.gif_label.configure(image=frame)
            idx = (idx + 1) % len(self.gif_img)
            self.window.after(60, self.animate_gif, idx)

    def start_chat_interface(self):
        self.animating_gif = False
        self.welcome_frame.destroy()
        self.create_header()
        self.create_chat_display()
        self.create_input_area()
        self.display.append_message("🤖 Bot", "Hi there! How can I help you today?")

    def create_header(self):
        header = tk.Frame(self.window, bg="#17153B", height=60)
        header.pack(fill=tk.X, pady=5)

        center_frame = tk.Frame(header, bg="#17153B")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.menu_button = tk.Button(center_frame, text="⋯", font=("Segoe UI", 16), bg="#17153B", fg="white", relief="flat", command=self.toggle_end_button)
        self.menu_button.pack(side=tk.LEFT, padx=(0, 8))

        self.end_button = tk.Button(center_frame, text="End Conversation", font=("Segoe UI", 10), bg="#BCA7F2", fg="#17153B", relief="flat", command=self.window.destroy)
        self.end_button.pack(side=tk.LEFT, padx=(0, 8))
        self.end_button.pack_forget()

        canvas = tk.Canvas(center_frame, width=10, height=10, bg="#17153B", highlightthickness=0)
        canvas.create_oval(2, 2, 8, 8, fill="#34C759", outline="#34C759")
        canvas.pack(side=tk.LEFT, padx=(0, 8))

        tk.Label(center_frame, text="Chatbot", font=("Segoe UI", 14, "bold"), bg="#17153B", fg="white").pack(side=tk.LEFT)

        if self.header_bot_img:
            tk.Label(center_frame, image=self.header_bot_img, bg="#17153B").pack(side=tk.LEFT, padx=8)

    def toggle_end_button(self):
        if self.end_button.winfo_ismapped():
            self.end_button.pack_forget()
        else:
            self.end_button.pack(side=tk.LEFT, padx=(0, 8))

    def create_chat_display(self):
        chat_container = tk.Frame(self.window, bg=self.window.cget("bg"))
        chat_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        chat_frame = tk.Frame(chat_container, bg="#17153B")
        chat_frame.pack(fill=tk.BOTH, expand=True)
        self.display = ChatDisplay(chat_frame, self.user_img, self.bot_img)

    def create_input_area(self):
        self.input = ChatInput(self.window, self.send_message)

    def load_profile_image(self, path, size=(35, 35)):
        try:
            img = Image.open(path).resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            return None

    def send_message(self):
        user_msg = self.input.get_input()
        if not user_msg:
            return
        
        self.display.append_message("🧑 You", user_msg)
        self.input.clear_input()
        
        self.display.show_typing_indicator()
        self.window.after(1500, self.get_bot_response, user_msg)

    def get_bot_response(self, user_msg):
        self.display.hide_typing_indicator()
        bot_reply = self.core.get_bot_response(user_msg)
        self.display.append_message("🤖 Bot", bot_reply)
        self.core.save_database()