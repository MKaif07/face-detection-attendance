#!/usr/bin/env python3
import os
import sys
from attendance_system.app import AttendanceSystem
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceSystem(root)
    root.mainloop() 