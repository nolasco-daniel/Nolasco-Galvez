from jejemon import JejemonZ
import sys

try:
    from gui import JejemonGUI
    import tkinter as tk
    
    if __name__ == "__main__":
        root = tk.Tk()
        gui = JejemonGUI(root)
        root.mainloop()
except Exception as e:
    print("Failed to launch GUI. Running CLI mode instead.")
    print(f"Error: {e}")
    def main():
        bot = JejemonZ()
        bot.run()
    if __name__ == "__main__":
        main()
