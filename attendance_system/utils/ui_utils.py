import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
from PIL import Image, ImageTk
import datetime
import time
import os
import threading

def center_window(window, width, height):
    """Center a tkinter window on the screen"""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    
    window.geometry(f"{width}x{height}+{x}+{y}")

def create_styled_button(parent, text, command, width=15):
    """Create a styled button"""
    style = ttk.Style()
    style.configure("TButton", font=("Arial", 10))
    
    button = ttk.Button(parent, text=text, command=command, width=width)
    return button

def create_styled_label(parent, text, font_size=12, bold=False):
    """Create a styled label"""
    font_weight = "bold" if bold else "normal"
    label = tk.Label(parent, text=text, font=("Arial", font_size, font_weight))
    return label

def create_styled_entry(parent, width=20):
    """Create a styled entry"""
    style = ttk.Style()
    style.configure("TEntry", font=("Arial", 10))
    
    entry = ttk.Entry(parent, width=width)
    return entry

def create_form_field(parent, label_text, row, column=0, entry_width=20):
    """Create a form field with label and entry"""
    label = create_styled_label(parent, label_text)
    label.grid(row=row, column=column, padx=5, pady=5, sticky="e")
    
    entry = create_styled_entry(parent, width=entry_width)
    entry.grid(row=row, column=column+1, padx=5, pady=5, sticky="w")
    
    return entry

def show_message(title, message, message_type="info"):
    """Show a message box"""
    if message_type == "info":
        messagebox.showinfo(title, message)
    elif message_type == "warning":
        messagebox.showwarning(title, message)
    elif message_type == "error":
        messagebox.showerror(title, message)

def create_video_frame(parent, width=640, height=480):
    """Create a frame for video display"""
    frame = tk.Frame(parent, width=width, height=height)
    frame.pack_propagate(False)  # Prevent the frame from shrinking
    
    video_label = tk.Label(frame)
    video_label.pack(fill=tk.BOTH, expand=True)
    
    return frame, video_label

class VideoCapture:
    def __init__(self, video_source=0):
        self.video_source = video_source
        self.cap = None
        self.is_running = False
        self.thread = None
        
    def start(self):
        """Start video capture"""
        self.cap = cv2.VideoCapture(self.video_source)
        if not self.cap.isOpened():
            raise ValueError("Unable to open video source", self.video_source)
        
        # Get video properties
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.is_running = True
        
    def stop(self):
        """Stop video capture"""
        self.is_running = False
        if self.thread:
            self.thread.join()
        if self.cap and self.cap.isOpened():
            self.cap.release()
        
    def get_frame(self):
        """Get a frame from the video source"""
        if self.cap is None or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        return frame
    
    def start_update_thread(self, callback, process_frame=None, delay=15):
        """Start a thread to update frames"""
        self.is_running = True
        self.thread = threading.Thread(target=self._update, args=(callback, process_frame, delay))
        self.thread.daemon = True
        self.thread.start()
    
    def _update(self, callback, process_frame=None, delay=15):
        """Update frames in a loop"""
        while self.is_running:
            frame = self.get_frame()
            if frame is not None:
                if process_frame:
                    frame = process_frame(frame)
                callback(frame)
            time.sleep(delay / 1000)  # delay in milliseconds

def convert_cv_to_tkinter(cv_img, target_width=None, target_height=None):
    """Convert an OpenCV image to a tkinter-compatible photo image"""
    if target_width and target_height:
        cv_img = cv2.resize(cv_img, (target_width, target_height))
    
    # Convert to RGB (from BGR)
    rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb_img)
    tk_img = ImageTk.PhotoImage(image=pil_img)
    return tk_img

def get_current_datetime():
    """Get current date and time as strings"""
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    return date_str, time_str 