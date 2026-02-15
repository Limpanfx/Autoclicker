import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import threading
import time
from pynput import keyboard, mouse

pyautogui.FAILSAFE = True

class Autoclicker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Limpan's Autoclicker")
        self.root.geometry("450x550")
        self.root.resizable(False, False)
        
        self.clicking = False
        self.recording = False
        self.positions = []
        self.simple_delay = tk.StringVar(value="0.1")
        self.position_delay = tk.StringVar(value="0.1")
        self.simple_keybind = None
        self.position_keybind = None
        self.listening_for_key = None
        self.key_listener = None
        self.mouse_listener = None
        self.current_tab = 0
        
        self.setup_style()
        self.setup_ui()
        self.start_key_listener()

    def setup_style(self):
        self.root.configure(bg='#0f0f0f')
        
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TNotebook', background='#0f0f0f', borderwidth=0, tabmargins=[10, 10, 10, 0])
        style.configure('TNotebook.Tab', background='#1a1a1a', foreground='#888888', 
                       padding=[30, 12], borderwidth=0, font=('Segoe UI', 10))
        style.map('TNotebook.Tab', 
                 background=[('selected', '#0f0f0f')],
                 foreground=[('selected', '#ffffff')])
        
        style.configure('TFrame', background='#0f0f0f')
        style.configure('TLabel', background='#0f0f0f', foreground='#cccccc', 
                       font=('Segoe UI', 10))
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground='#ffffff')
        style.configure('Status.TLabel', foreground='#00ff88', font=('Segoe UI', 11))
        style.configure('Subtitle.TLabel', foreground='#888888', font=('Segoe UI', 9))
        
        style.configure('TEntry', fieldbackground='#1a1a1a', foreground='#ffffff', 
                       borderwidth=1, relief='flat', insertcolor='#ffffff',
                       padding=[10, 8])
        
        style.configure('TButton', background='#1a1a1a', foreground='#ffffff', 
                       borderwidth=0, focuscolor='none', padding=[15, 10],
                       font=('Segoe UI', 10))
        style.map('TButton', background=[('active', '#252525')])
        
        style.configure('Accent.TButton', background='#00ff88', foreground='#000000',
                       font=('Segoe UI', 10, 'bold'))
        style.map('Accent.TButton', background=[('active', '#00dd77')])
        
        style.configure('Danger.TButton', background='#ff4444', foreground='#ffffff',
                       font=('Segoe UI', 10, 'bold'))
        style.map('Danger.TButton', background=[('active', '#dd3333')])

    def setup_ui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=15, pady=15)
        notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
        
        simple_frame = ttk.Frame(notebook)
        position_frame = ttk.Frame(notebook)
        
        notebook.add(simple_frame, text='Simple')
        notebook.add(position_frame, text='Positions')
        
        self.setup_simple_tab(simple_frame)
        self.setup_position_tab(position_frame)
    
    def on_tab_changed(self, event):
        self.current_tab = event.widget.index('current')

    def setup_simple_tab(self, parent):
        ttk.Label(parent, text="Simple Autoclicker", style='Title.TLabel').pack(pady=(30, 10))
        ttk.Label(parent, text="Click repeatedly at current mouse position", 
                 style='Subtitle.TLabel').pack(pady=(0, 40))
        
        keybind_container = ttk.Frame(parent)
        keybind_container.pack(pady=15, fill='x', padx=60)
        ttk.Label(keybind_container, text="Toggle Keybind", 
                 font=('Segoe UI', 9, 'bold')).pack(anchor='w', pady=(0, 8))
        self.simple_key_btn = ttk.Button(keybind_container, text="Not Set", 
                                         command=lambda: self.listen_for_keybind('simple'))
        self.simple_key_btn.pack(fill='x', ipady=5)
        
        delay_container = ttk.Frame(parent)
        delay_container.pack(pady=15, fill='x', padx=60)
        ttk.Label(delay_container, text="Delay Between Clicks (seconds)", 
                 font=('Segoe UI', 9, 'bold')).pack(anchor='w', pady=(0, 8))
        delay_entry = ttk.Entry(delay_container, textvariable=self.simple_delay)
        delay_entry.pack(fill='x', ipady=5)
        
        button_container = ttk.Frame(parent)
        button_container.pack(pady=30, fill='x', padx=60)
        self.simple_start_btn = ttk.Button(button_container, text="Start Clicking", 
                                           style='Accent.TButton', 
                                           command=self.start_simple_click)
        self.simple_start_btn.pack(fill='x', ipady=8, pady=(0, 10))
        self.simple_stop_btn = ttk.Button(button_container, text="Stop", 
                                          style='Danger.TButton', 
                                          command=self.stop_click, state='disabled')
        self.simple_stop_btn.pack(fill='x', ipady=8)
        
        status_container = ttk.Frame(parent)
        status_container.pack(pady=20)
        self.simple_status = ttk.Label(status_container, text="● Idle", style='Status.TLabel')
        self.simple_status.pack()

    def setup_position_tab(self, parent):
        ttk.Label(parent, text="Position-based Clicking", style='Title.TLabel').pack(pady=(30, 10))
        ttk.Label(parent, text="Click through multiple saved screen positions", 
                 style='Subtitle.TLabel').pack(pady=(0, 40))
        
        keybind_container = ttk.Frame(parent)
        keybind_container.pack(pady=15, fill='x', padx=60)
        ttk.Label(keybind_container, text="Toggle Keybind", 
                 font=('Segoe UI', 9, 'bold')).pack(anchor='w', pady=(0, 8))
        self.position_key_btn = ttk.Button(keybind_container, text="Not Set", 
                                           command=lambda: self.listen_for_keybind('position'))
        self.position_key_btn.pack(fill='x', ipady=5)
        
        delay_container = ttk.Frame(parent)
        delay_container.pack(pady=15, fill='x', padx=60)
        ttk.Label(delay_container, text="Delay Between Clicks (seconds)", 
                 font=('Segoe UI', 9, 'bold')).pack(anchor='w', pady=(0, 8))
        delay_entry = ttk.Entry(delay_container, textvariable=self.position_delay)
        delay_entry.pack(fill='x', ipady=5)
        
        position_container = ttk.Frame(parent)
        position_container.pack(pady=15, fill='x', padx=60)
        ttk.Label(position_container, text="Click Positions", 
                 font=('Segoe UI', 9, 'bold')).pack(anchor='w', pady=(0, 8))
        
        pos_info_frame = ttk.Frame(position_container)
        pos_info_frame.pack(fill='x', pady=(0, 8))
        self.pos_label = ttk.Label(pos_info_frame, text="0 positions saved", foreground='#00ff88')
        self.pos_label.pack(side='left')
        
        pos_btn_frame = ttk.Frame(position_container)
        pos_btn_frame.pack(fill='x')
        ttk.Button(pos_btn_frame, text="Add Position", command=self.add_position).pack(side='left', expand=True, fill='x', padx=(0, 5))
        ttk.Button(pos_btn_frame, text="Clear All", command=self.clear_positions).pack(side='left', expand=True, fill='x', padx=(5, 0))
        
        button_container = ttk.Frame(parent)
        button_container.pack(pady=30, fill='x', padx=60)
        self.position_start_btn = ttk.Button(button_container, text="Start Clicking", 
                                             style='Accent.TButton', 
                                             command=self.start_position_click)
        self.position_start_btn.pack(fill='x', ipady=8, pady=(0, 10))
        self.position_stop_btn = ttk.Button(button_container, text="Stop", 
                                            style='Danger.TButton', 
                                            command=self.stop_click, state='disabled')
        self.position_stop_btn.pack(fill='x', ipady=8)
        
        status_container = ttk.Frame(parent)
        status_container.pack(pady=20)
        self.position_status = ttk.Label(status_container, text="● Idle", style='Status.TLabel')
        self.position_status.pack()

    def start_key_listener(self):
        def on_press(key):
            if self.listening_for_key:
                try:
                    key_char = key.char if hasattr(key, 'char') else key.name
                    if self.listening_for_key == 'simple':
                        self.simple_keybind = key_char
                        self.simple_key_btn.config(text=key_char.upper())
                        self.animate_button(self.simple_key_btn)
                    else:
                        self.position_keybind = key_char
                        self.position_key_btn.config(text=key_char.upper())
                        self.animate_button(self.position_key_btn)
                    self.listening_for_key = None
                except:
                    pass
            else:
                try:
                    key_char = key.char if hasattr(key, 'char') else key.name
                    if key_char == self.simple_keybind and self.current_tab == 0:
                        if self.clicking:
                            self.stop_click()
                        else:
                            self.start_simple_click()
                    elif key_char == self.position_keybind and self.current_tab == 1:
                        if self.clicking:
                            self.stop_click()
                        else:
                            self.start_position_click()
                except:
                    pass
        
        self.key_listener = keyboard.Listener(on_press=on_press)
        self.key_listener.daemon = True
        self.key_listener.start()

    def animate_button(self, button, color='#00ff88'):
        original_bg = button.cget('style')
        button.configure(style='Accent.TButton')
        self.root.after(150, lambda: button.configure(style=original_bg if original_bg else 'TButton'))
    
    def listen_for_keybind(self, mode):
        self.listening_for_key = mode
        if mode == 'simple':
            self.simple_key_btn.config(text="Listening...")
        else:
            self.position_key_btn.config(text="Listening...")

    def add_position(self):
        self.recording = True
        self.root.attributes('-alpha', 0.5)
        
        def on_click(x, y, button, pressed):
            if pressed and button == mouse.Button.left and self.recording:
                self.positions.append((x, y))
                self.pos_label.config(text=f"{len(self.positions)} position{'s' if len(self.positions) != 1 else ''} saved")
                self.recording = False
                self.root.attributes('-alpha', 1.0)
                if self.mouse_listener:
                    self.mouse_listener.stop()
                return False
        
        self.mouse_listener = mouse.Listener(on_click=on_click)
        self.mouse_listener.daemon = True
        self.mouse_listener.start()

    def clear_positions(self):
        self.positions = []
        self.pos_label.config(text="0 positions saved")

    def start_simple_click(self):
        if self.clicking:
            return
        self.clicking = True
        self.simple_status.config(text="● Active")
        self.simple_start_btn.config(state='disabled')
        self.simple_stop_btn.config(state='normal')
        self.animate_status(self.simple_status)
        threading.Thread(target=self.simple_click_loop, daemon=True).start()

    def start_position_click(self):
        if self.clicking:
            return
        if not self.positions:
            messagebox.showerror("Error", "No positions saved. Add at least one position first.")
            return
        self.clicking = True
        self.position_status.config(text="● Active")
        self.position_start_btn.config(state='disabled')
        self.position_stop_btn.config(state='normal')
        self.animate_status(self.position_status)
        threading.Thread(target=self.position_click_loop, daemon=True).start()

    def stop_click(self):
        self.clicking = False
        self.simple_status.config(text="● Idle")
        self.position_status.config(text="● Idle")
        self.simple_start_btn.config(state='normal')
        self.simple_stop_btn.config(state='disabled')
        self.position_start_btn.config(state='normal')
        self.position_stop_btn.config(state='disabled')
    
    def animate_status(self, label):
        if self.clicking:
            current = label.cget('text')
            if current == "● Active":
                label.config(text="◐ Active")
            elif current == "◐ Active":
                label.config(text="◑ Active")
            elif current == "◑ Active":
                label.config(text="◒ Active")
            else:
                label.config(text="● Active")
            self.root.after(200, lambda: self.animate_status(label))

    def simple_click_loop(self):
        while self.clicking:
            try:
                pyautogui.click()
                time.sleep(float(self.simple_delay.get()))
            except:
                break

    def position_click_loop(self):
        idx = 0
        while self.clicking:
            try:
                pos = self.positions[idx % len(self.positions)]
                pyautogui.click(*pos)
                time.sleep(float(self.position_delay.get()))
                idx += 1
            except:
                break

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        self.root.mainloop()

    def quit_app(self):
        self.clicking = False
        self.recording = False
        if self.key_listener:
            self.key_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()
        self.root.quit()

if __name__ == "__main__":
    app = Autoclicker()
    app.run()