import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from tkinter import ttk
from translator import JejemonTranslator
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os

class JejemonGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Jejemon Translator")
        self.translator = JejemonTranslator()
        self.mode = None
        self.bg_color = "#393E46"
        self.root.geometry("500x700")
        self._build_main_menu()

    def _clear_window(self):
        if hasattr(self, 'bg_canvas') and hasattr(self, 'bg_gif_id'):
            try:
                self.root.after_cancel(self._gif_after_id)
            except Exception:
                pass
        for widget in self.root.winfo_children():
            widget.destroy()

    def _build_main_menu(self):
        self._clear_window()
        self.mode = None
        self.output_var = tk.StringVar()
        self.input_var = tk.StringVar()
        self.bg_color = "#f8f6f2"
        self.root.geometry("1200x700")
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Arial', 12, 'bold'), padding=8, borderwidth=2, relief='flat', background='#393E46', foreground='#fff', focuscolor='', bordercolor='#38b6ff')
        style.map('TButton', background=[], relief=[], foreground=[], bordercolor=[])
        style.configure('Hover.TButton', background='#b6e388', foreground='#222')
        bg_path = os.path.join("multimedia", "Background1.png")
        target_w, target_h = 1200, 700
        try:
            bg_img = Image.open(bg_path)
            orig_w, orig_h = bg_img.size
            scale = max(target_w / orig_w, target_h / orig_h)
            new_w = int(orig_w * scale)
            new_h = int(orig_h * scale)
            bg_img = bg_img.resize((new_w, new_h), Image.LANCZOS)
            left = (new_w - target_w) // 2
            top = (new_h - target_h) // 2
            right = left + target_w
            bottom = top + target_h
            bg_img = bg_img.crop((left, top, right, bottom))
            self.bg_img_tk = ImageTk.PhotoImage(bg_img)
        except Exception as e:
            self.bg_img_tk = None
        self.bg_canvas = tk.Canvas(self.root, width=1200, height=700, highlightthickness=0, bd=0)
        self.bg_canvas.place(x=0, y=0)
        if self.bg_img_tk:
            self.bg_canvas.create_image(0, 0, anchor='nw', image=self.bg_img_tk)
        else:
            self.bg_canvas.create_rectangle(0, 0, 1200, 700, fill=self.bg_color, outline="")
        btn_frame = tk.Frame(self.root, bg='#393E46')
        btn_frame.pack(expand=True)

        style.configure('TButton', font=('Arial', 12, 'bold'), padding=8, borderwidth=2, relief='flat', background='#393E46', foreground='#fff', focuscolor='', bordercolor='#38b6ff')
        style.map('TButton', background=[], relief=[], foreground=[], bordercolor=[])
        style.configure('Hover.TButton', background='#b6e388', foreground='#222')

        style.configure('TButton', font=('Arial', 12, 'bold'), padding=8, borderwidth=0, relief='flat', background='#0f0f0f', foreground='#fff', focuscolor='')
        style.map('TButton', background=[], relief=[], foreground=[])

        def bordered_button(parent, **kwargs):
            border = tk.Frame(parent, bg='#38b6ff', padx=2, pady=2)
            btn = ttk.Button(border, style='TButton', **kwargs)
            btn.pack()
            return border, btn

        self.btn_to_jejemon_frame, self.btn_to_jejemon = bordered_button(btn_frame, text="Normalize to Jejemon", width=22, command=self._set_to_jejemon)
        self.btn_to_jejemon_frame.grid(row=0, column=0, padx=4)

        self.btn_to_normal_frame, self.btn_to_normal = bordered_button(btn_frame, text="Jejemon to Normalize", width=22, command=self._set_to_normal)
        self.btn_to_normal_frame.grid(row=0, column=1, padx=4)

        self.btn_exit_frame, self.btn_exit = bordered_button(btn_frame, text="Exit Program", width=16, command=self.root.quit)
        self.btn_exit_frame.grid(row=0, column=2, padx=4)

        for btn in [self.btn_to_jejemon, self.btn_to_normal, self.btn_exit]:
            pass

    def _set_to_jejemon(self):
        self.mode = 'to_jejemon'
        self._build_translate_view()

    def _set_to_normal(self):
        self.mode = 'to_normal'
        self._build_translate_view()

    def _get_font_and_wrapped_lines(self, text, max_img_size=500, min_font_size=6, max_font_size=120, canvas_height=500, line_height_multiplier=1.0):
        from PIL import ImageFont
        import textwrap
        font_name_candidates = ["arialn.ttf", "arial.ttf"]
        font_path = None
        for font_name in font_name_candidates:
            try:
                _ = ImageFont.truetype(font_name, 40)
                font_path = font_name
                break
            except:
                continue
        def wrap_lines(lines, font, max_width):
            wrapped = []
            for line in lines:
                while True:
                    line_width = font.getbbox(line)[2] - font.getbbox(line)[0]
                    if line_width <= max_width:
                        wrapped.append(line)
                        break
                    avg_char_width = font.getbbox('A')[2] - font.getbbox('A')[0]
                    if avg_char_width == 0:
                        avg_char_width = 10
                    chars_per_line = max(1, max_width // avg_char_width)
                    wrapped.extend(textwrap.wrap(line, width=chars_per_line, break_long_words=True, replace_whitespace=False))
                    break
            return wrapped
        font_size = max_font_size
        lines = text.split('\n')
        margin = 30
        max_width = max_img_size - 2 * margin
        max_height = canvas_height - 2 * margin
        while font_size >= min_font_size:
            try:
                if font_path:
                    font = ImageFont.truetype(font_path, font_size)
                else:
                    font = ImageFont.load_default()
                wrapped_lines = wrap_lines(lines, font, max_width)
                line_height = font.getbbox('A')[3] - font.getbbox('A')[1] + int(font_size * 0.3)
                adj_line_height = int(line_height * line_height_multiplier)
                total_text_height = adj_line_height * len(wrapped_lines)
                all_fit = True
                for line in wrapped_lines:
                    if font.getbbox(line)[2] - font.getbbox(line)[0] > max_width:
                        all_fit = False
                        break
                if all_fit and total_text_height <= max_height:
                    break
                font_size -= 2
            except Exception:
                font_size -= 2
        if font_path:
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()
        wrapped_lines = wrap_lines(lines, font, max_width)
        line_height = font.getbbox('A')[3] - font.getbbox('A')[1] + int(font_size * 0.3)
        adj_line_height = int(line_height * line_height_multiplier)
        total_text_height = adj_line_height * len(wrapped_lines)
        max_text_width = max([font.getbbox(line)[2] - font.getbbox(line)[0] for line in wrapped_lines]) if wrapped_lines else 0
        return font, wrapped_lines, font_size, line_height, adj_line_height, total_text_height, max_text_width, margin

    def _build_translate_view(self):
        self._clear_window()
        self.bg_color = "#0f0f0f"
        self.root.geometry("1366x768")
        self.root.configure(bg="#0f0f0f")
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Green.TButton', font=('Arial', 12, 'bold'), padding=8, borderwidth=0, relief='flat', background='#b6e388', foreground='#222', focuscolor='')
        style.map('Green.TButton',
            background=[('active', '#a0c97c'), ('pressed', '#8fc46c')],
            foreground=[('active', '#222'), ('pressed', '#222')]
        )
        style.configure('White.TButton', font=('Arial', 12, 'bold'), padding=8, borderwidth=0, relief='flat', background='#fff', foreground='#222', focuscolor='')
        style.map('White.TButton',
            background=[('active', '#e0e0e0'), ('pressed', '#cccccc')],
            foreground=[('active', '#222'), ('pressed', '#222')]
        )
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True)
        output_frame = tk.Frame(main_frame, bg=self.bg_color, bd=0, highlightthickness=0)
        output_frame.pack(pady=(20, 5), padx=100, fill=tk.X)
        self.output_canvas = tk.Canvas(
            output_frame,
            width=1000,
            height=470,
            bg="#F2F2F2",
            highlightthickness=0,
            relief="flat"
        )
        self.output_canvas.pack()
        self._draw_output_canvas(self.output_var.get())
        self.output_frame = output_frame
        color_selector_frame = tk.Frame(main_frame, bg=self.bg_color)
        color_selector_frame.pack(pady=(0, 8))
        label_bg_frame = tk.Frame(color_selector_frame, bg="#393E46")
        label_bg_frame.pack(side=tk.LEFT)
        tk.Label(label_bg_frame, text="Background color:", bg="#393E46", fg="#fff").pack()
        for color in ["#b6e388", "#ffffff", "#f8f6f2"]:
            border = tk.Frame(color_selector_frame, bg="black", padx=1, pady=1)
            border.pack(side=tk.LEFT, padx=2)
            tk.Button(border, bg=color, width=2, height=1, command=lambda c=color: self._change_bg_color(c), relief='flat', bd=0).pack()
        self.color_frame = color_selector_frame
        self.input_entry = tk.Entry(main_frame, textvariable=self.input_var, font=("Arial", 14), width=80, relief="solid", bd=2)
        self.input_entry.pack(pady=8)
        btn_frame = tk.Frame(main_frame, bg=self.bg_color)
        btn_frame.pack(pady=10)
        # Button frame for translate view
        def bordered_button(parent, **kwargs):
            border = tk.Frame(parent, bg='#38b6ff', padx=2, pady=2)
            btn = ttk.Button(border, style='TButton', **kwargs)
            btn.pack()
            return border, btn

        # Update TButton style for translate view buttons
        style.configure('TButton', font=('Arial', 12, 'bold'), padding=8, borderwidth=0, relief='flat', background='#0f0f0f', foreground='#fff', focuscolor='')
        style.map('TButton', background=[], relief=[], foreground=[])

        # Replace translate, save, and back buttons with bordered buttons
        self.btn_translate_frame, self.btn_translate = bordered_button(btn_frame, text="Translate", width=18, command=self._translate)
        self.btn_translate_frame.grid(row=0, column=0, padx=10)

        self.btn_save_frame, self.btn_save = bordered_button(btn_frame, text="Save", width=12, command=self._save_text)
        self.btn_save_frame.grid(row=0, column=1, padx=10)

        self.btn_back_frame, self.btn_back = bordered_button(btn_frame, text="Back to Main Menu", width=22, command=self._build_main_menu)
        self.btn_back_frame.grid(row=0, column=2, padx=10)

    def _draw_output_canvas(self, text):
        if hasattr(self, 'output_canvas'):
            self.output_canvas.delete("all")
            if not text:
                return
            import textwrap
            import tkinter.font as tkFont
            canvas_width = int(self.output_canvas['width'])
            canvas_height = int(self.output_canvas['height'])
            margin = 30
            min_font_size = 8
            max_font_size = 32
            font_family = "Arial"
            for font_size in range(max_font_size, min_font_size - 1, -1):
                font = tkFont.Font(family=font_family, size=font_size, weight="bold")
                usable_width = canvas_width - 2 * margin
                avg_char_width = font.measure('A') if font.measure('A') > 0 else font_size * 0.6
                max_chars_per_line = max(1, int(usable_width // avg_char_width))
                lines = []
                for paragraph in text.split('\n'):
                    lines.extend(textwrap.wrap(paragraph, width=max_chars_per_line))
                    if paragraph != text.split('\n')[-1]:
                        lines.append("")
                fits_width = all(font.measure(line) <= usable_width for line in lines)
                line_height = font.metrics("linespace") + 4
                total_text_height = len(lines) * line_height
                fits_height = total_text_height <= (canvas_height - 2 * 10)
                if fits_width and fits_height:
                    break
            y = (canvas_height - total_text_height) // 2
            for line in lines:
                self.output_canvas.create_text(
                    canvas_width // 2, y, text=line, font=(font_family, font_size, "bold"), fill="#222", anchor="n"
                )
                y += line_height

    def _update_output_text(self, text):
        self._draw_output_canvas(text)

    def _clear_placeholder(self):
        if self.input_text.get("1.0", "end-1c") == "Type or paste your text here...":
            self.input_text.delete("1.0", "end")

    def _change_bg_color(self, color):
        self.bg_color = color
        if hasattr(self, 'output_canvas'):
            self.output_canvas.config(bg=color)
        if hasattr(self, 'output_frame'):
            self.output_frame.config(bg=color)
        if hasattr(self, 'color_frame'):
            self.color_frame.config(bg=color)

    def _translate(self):
        input_text = self.input_var.get()
        if not input_text.strip():
            messagebox.showwarning("Input Required", "Please enter text to translate.")
            return
        if self.mode == 'to_jejemon':
            result = self.translator.jejemonize(input_text)
        else:
            result = self.translator.normalize(input_text)
        self.output_var.set(result)
        self._update_output_text(result)

    def _save_text(self):
        text = self.output_var.get()
        if not text.strip():
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")])
        if file_path:
            try:
                self._save_text_as_image(text, file_path)
            except Exception as e:
                print(f"Failed to save image: {e}")

    def _save_text_as_image(self, text, file_path):
        from PIL import Image, ImageDraw, ImageFont
        import textwrap
        img_width = 1080
        img_height = 1080
        bg_color = self.output_canvas['bg'] if 'bg' in self.output_canvas.keys() else self.bg_color
        margin = 40
        min_font_size = 10
        max_font_size = 180
        font_family = "arial.ttf"
        for font_size in range(max_font_size, min_font_size - 1, -2):
            try:
                font = ImageFont.truetype(font_family, font_size)
            except Exception:
                font = ImageFont.load_default()
            usable_width = img_width - 2 * margin
            avg_char_width = font.getbbox('A')[2] - font.getbbox('A')[0]
            if avg_char_width == 0:
                avg_char_width = font_size * 0.6
            max_chars_per_line = max(1, int(usable_width // avg_char_width))
            lines = []
            for paragraph in text.split('\n'):
                lines.extend(textwrap.wrap(paragraph, width=max_chars_per_line))
                if paragraph != text.split('\n')[-1]:
                    lines.append("")
            line_widths = []
            line_height = int((font.getbbox('A')[3] - font.getbbox('A')[1] + 4) * 1.35)
            total_text_height = len(lines) * line_height
            fits_height = total_text_height <= (img_height - 2 * margin)
            fits_width = True
            for line in lines:
                bbox = font.getbbox(line)
                w = bbox[2] - bbox[0]
                line_widths.append(w)
                if w > usable_width:
                    fits_width = False
                    break
            if fits_height and fits_width:
                break
        img = Image.new('RGB', (img_width, img_height), color=bg_color)
        draw = ImageDraw.Draw(img)
        y = (img_height - total_text_height) // 2
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            w = bbox[2] - bbox[0]
            x = (img_width - w) // 2
            draw.text((x, y), line, font=font, fill="#222")
            y += line_height
        img.save(file_path)

if __name__ == "__main__":
    root = tk.Tk()
    gui = JejemonGUI(root)
    root.mainloop() 