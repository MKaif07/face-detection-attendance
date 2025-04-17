import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import threading
import cv2
import datetime

# Add the parent directory to the path to import database and utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from attendance_system.database.db_manager import DatabaseManager
from attendance_system.utils.face_utils_simple import FaceDetector
from attendance_system.utils.ui_utils import (
    center_window, create_styled_button, create_styled_label, create_styled_entry,
    create_form_field, show_message, create_video_frame, VideoCapture, 
    convert_cv_to_tkinter, get_current_datetime
)

class AttendanceSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Detection Attendance System")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        center_window(self.root, 800, 600)
        
        # Initialize database and face detector
        self.db = DatabaseManager()
        self.face_detector = FaceDetector()
        
        # Current user data
        self.current_user = None
        self.current_user_role = None
        
        # Show login screen
        self.show_login_screen()
    
    def show_login_screen(self):
        """Show the login screen"""
        # Clear current frame if any
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create login frame
        login_frame = ttk.Frame(self.root, padding=20)
        login_frame.pack(expand=True)
        
        # Title
        title = create_styled_label(login_frame, "Face Detection Attendance System", 16, True)
        title.grid(row=0, column=0, columnspan=2, pady=20)
        
        # Username
        username_label = create_styled_label(login_frame, "Username:")
        username_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.username_entry = create_styled_entry(login_frame)
        self.username_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Password
        password_label = create_styled_label(login_frame, "Password:")
        password_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.password_entry = create_styled_entry(login_frame)
        self.password_entry.config(show="*")
        self.password_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # Login button
        login_button = create_styled_button(login_frame, "Login", self.login)
        login_button.grid(row=3, column=0, columnspan=2, pady=20)
    
    def login(self):
        """Handle login process"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            show_message("Login Error", "Username and password are required", "error")
            return
        
        # Check credentials
        result = self.db.verify_user(username, password)
        if result:
            user_id, role = result
            self.current_user = user_id
            self.current_user_role = role
            self.show_main_screen()
        else:
            show_message("Login Error", "Invalid username or password", "error")
    
    def show_main_screen(self):
        """Show the main application screen based on user role"""
        # Clear current frame
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create main notebook with tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add appropriate tabs based on user role
        if self.current_user_role == "admin":
            # Admin tabs
            self.create_student_management_tab(notebook)
            self.create_take_attendance_tab(notebook)
            self.create_attendance_reports_tab(notebook)
        else:
            # Student tabs
            self.create_take_attendance_tab(notebook)
            self.create_my_attendance_tab(notebook)
        
        # Logout button at the bottom
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=10, pady=5)
        
        logout_button = create_styled_button(bottom_frame, "Logout", self.logout)
        logout_button.pack(side=tk.RIGHT, padx=5)
    
    def create_student_management_tab(self, notebook):
        """Create the student management tab (admin only)"""
        tab = ttk.Frame(notebook, padding=10)
        notebook.add(tab, text="Student Management")
        
        # Split into two frames
        left_frame = ttk.Frame(tab, padding=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_frame = ttk.Frame(tab, padding=5)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Student list (left side)
        list_frame = ttk.LabelFrame(left_frame, text="Student List")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create Treeview
        columns = ("ID", "Name", "Roll Number", "Department")
        self.student_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Configure headings
        for col in columns:
            self.student_tree.heading(col, text=col)
            self.student_tree.column(col, width=80)
        
        self.student_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.student_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.student_tree.configure(yscrollcommand=scrollbar.set)
        
        # Load student data
        self.load_student_list()
        
        # Add/Edit student form (right side)
        form_frame = ttk.LabelFrame(right_frame, text="Add/Edit Student")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Form fields
        self.student_name_entry = create_form_field(form_frame, "Name:", 0)
        self.student_roll_entry = create_form_field(form_frame, "Roll Number:", 1)
        self.student_dept_entry = create_form_field(form_frame, "Department:", 2)
        self.student_username_entry = create_form_field(form_frame, "Username:", 3)
        self.student_password_entry = create_form_field(form_frame, "Password:", 4)
        self.student_password_entry.config(show="*")
        
        # Face capture section
        face_frame = ttk.LabelFrame(right_frame, text="Face Capture")
        face_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Buttons for face capture
        button_frame = ttk.Frame(face_frame)
        button_frame.pack(pady=10)
        
        capture_button = create_styled_button(button_frame, "Capture Face", self.capture_student_face)
        capture_button.pack(side=tk.LEFT, padx=5)
        
        save_button = create_styled_button(button_frame, "Save Student", self.save_student)
        save_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = create_styled_button(button_frame, "Clear Form", self.clear_student_form)
        clear_button.pack(side=tk.LEFT, padx=5)
    
    def create_take_attendance_tab(self, notebook):
        """Create the take attendance tab"""
        tab = ttk.Frame(notebook, padding=10)
        notebook.add(tab, text="Take Attendance")
        
        # Split into two frames
        left_frame = ttk.Frame(tab, padding=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_frame = ttk.Frame(tab, padding=5)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Video display (left side)
        video_frame = ttk.LabelFrame(left_frame, text="Camera Feed")
        video_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.camera_frame, self.camera_label = create_video_frame(video_frame, 400, 300)
        self.camera_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Control buttons
        control_frame = ttk.Frame(left_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.start_camera_button = create_styled_button(control_frame, "Start Camera", self.start_camera)
        self.start_camera_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_camera_button = create_styled_button(control_frame, "Stop Camera", self.stop_camera)
        self.stop_camera_button.pack(side=tk.LEFT, padx=5)
        self.stop_camera_button.configure(state=tk.DISABLED)
        
        # Recent detections (right side)
        detection_frame = ttk.LabelFrame(right_frame, text="Recent Detections")
        detection_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create Treeview for recent detections
        columns = ("Time", "Name", "Roll Number", "Status")
        self.detection_tree = ttk.Treeview(detection_frame, columns=columns, show="headings")
        
        # Configure headings
        for col in columns:
            self.detection_tree.heading(col, text=col)
            self.detection_tree.column(col, width=80)
        
        self.detection_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(detection_frame, orient="vertical", command=self.detection_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.detection_tree.configure(yscrollcommand=scrollbar.set)
        
        # Initialize video capture
        self.video_capture = None
        self.detection_lock = threading.Lock()
        self.last_detection_time = {}  # To prevent multiple detections in a short time
        
    def create_attendance_reports_tab(self, notebook):
        """Create the attendance reports tab (admin only)"""
        tab = ttk.Frame(notebook, padding=10)
        notebook.add(tab, text="Attendance Reports")
        
        # Controls
        control_frame = ttk.LabelFrame(tab, text="Report Controls")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Date range
        date_frame = ttk.Frame(control_frame)
        date_frame.pack(fill=tk.X, padx=5, pady=5)
        
        from_label = create_styled_label(date_frame, "From Date:")
        from_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.from_date_entry = create_styled_entry(date_frame)
        self.from_date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.from_date_entry.insert(0, get_current_datetime()[0])
        
        to_label = create_styled_label(date_frame, "To Date:")
        to_label.grid(row=0, column=2, padx=5, pady=5)
        
        self.to_date_entry = create_styled_entry(date_frame)
        self.to_date_entry.grid(row=0, column=3, padx=5, pady=5)
        self.to_date_entry.insert(0, get_current_datetime()[0])
        
        generate_button = create_styled_button(date_frame, "Generate Report", self.generate_attendance_report)
        generate_button.grid(row=0, column=4, padx=20, pady=5)
        
        # Report display
        report_frame = ttk.LabelFrame(tab, text="Attendance Report")
        report_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create Treeview
        columns = ("Name", "Roll Number", "Department", "Date", "Time", "Status")
        self.report_tree = ttk.Treeview(report_frame, columns=columns, show="headings")
        
        # Configure headings
        for col in columns:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=80)
        
        self.report_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(report_frame, orient="vertical", command=self.report_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.report_tree.configure(yscrollcommand=scrollbar.set)
    
    def create_my_attendance_tab(self, notebook):
        """Create the my attendance tab (student only)"""
        tab = ttk.Frame(notebook, padding=10)
        notebook.add(tab, text="My Attendance")
        
        # Student info
        info_frame = ttk.LabelFrame(tab, text="Student Information")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Get student info
        student_info = self.get_student_info(self.current_user)
        if student_info:
            student_id, user_id, name, roll_num, department, _ = student_info
            
            # Display student info
            info_text = f"Name: {name}\nRoll Number: {roll_num}\nDepartment: {department}"
            info_label = create_styled_label(info_frame, info_text)
            info_label.pack(padx=10, pady=10)
            
            # Attendance history
            history_frame = ttk.LabelFrame(tab, text="Attendance History")
            history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Create Treeview
            columns = ("Date", "Time", "Status")
            self.my_attendance_tree = ttk.Treeview(history_frame, columns=columns, show="headings")
            
            # Configure headings
            for col in columns:
                self.my_attendance_tree.heading(col, text=col)
                self.my_attendance_tree.column(col, width=120)
            
            self.my_attendance_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.my_attendance_tree.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.my_attendance_tree.configure(yscrollcommand=scrollbar.set)
            
            # Load student's attendance
            self.load_student_attendance(student_id)
        else:
            error_label = create_styled_label(info_frame, "Student information not found")
            error_label.pack(padx=10, pady=10)
    
    def get_student_info(self, user_id):
        """Get student information from user ID"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def load_student_attendance(self, student_id):
        """Load attendance history for a student"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT date, time, status FROM attendance WHERE student_id = ? ORDER BY date DESC, time DESC",
            (student_id,)
        )
        results = cursor.fetchall()
        conn.close()
        
        # Clear current items
        for item in self.my_attendance_tree.get_children():
            self.my_attendance_tree.delete(item)
        
        # Insert new items
        for date, time, status in results:
            self.my_attendance_tree.insert("", "end", values=(date, time, status))
    
    def load_student_list(self):
        """Load student list into the treeview"""
        # Clear current items
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        
        # Get all students
        students = self.db.get_all_students()
        for student_id, name, roll_number, department in students:
            self.student_tree.insert("", "end", values=(student_id, name, roll_number, department))
    
    def clear_student_form(self):
        """Clear the student form"""
        self.student_name_entry.delete(0, tk.END)
        self.student_roll_entry.delete(0, tk.END)
        self.student_dept_entry.delete(0, tk.END)
        self.student_username_entry.delete(0, tk.END)
        self.student_password_entry.delete(0, tk.END)
    
    def capture_student_face(self):
        """Open camera to capture student's face"""
        # Create a new window for face capture
        capture_window = tk.Toplevel(self.root)
        capture_window.title("Capture Face")
        center_window(capture_window, 500, 400)
        
        # Create video frame
        frame, video_label = create_video_frame(capture_window, 400, 300)
        frame.pack(padx=10, pady=10)
        
        # Control buttons
        button_frame = ttk.Frame(capture_window)
        button_frame.pack(pady=10)
        
        self.face_encoding = None
        
        # Capture button
        def on_capture():
            # Get the current frame
            current_frame = video_capture.get_frame()
            if current_frame is not None:
                # Detect faces
                faces = self.face_detector.detect_faces(current_frame)
                
                if len(faces) > 0:
                    # Extract the largest face
                    largest_face = None
                    max_area = 0
                    for (x, y, w, h) in faces:
                        if w * h > max_area:
                            max_area = w * h
                            largest_face = (x, y, w, h)
                    
                    # Process face for storage
                    face_img = current_frame[largest_face[1]:largest_face[1]+largest_face[3], 
                                            largest_face[0]:largest_face[0]+largest_face[2]]
                    self.face_encoding = face_img  # Store the face image
                    
                    show_message("Success", "Face captured successfully!", "info")
                    capture_window.destroy()
                else:
                    show_message("Error", "No face detected in the image", "error")
        
        capture_button = create_styled_button(button_frame, "Capture", on_capture)
        capture_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = create_styled_button(button_frame, "Cancel", capture_window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Initialize video capture
        video_capture = VideoCapture()
        video_capture.start()
        
        # Function to update video frame
        last_frame = None
        def update_frame(frame):
            nonlocal last_frame
            last_frame = frame
            faces = self.face_detector.detect_faces(frame)
            frame = self.face_detector.draw_faces(frame.copy(), faces)
            
            # Convert to tkinter format
            tk_img = convert_cv_to_tkinter(frame)
            video_label.configure(image=tk_img)
            video_label.image = tk_img
        
        # Start video capture thread
        video_capture.start_update_thread(update_frame)
        
        # Make sure resources are released when window is closed
        def on_closing():
            video_capture.stop()
            capture_window.destroy()
        
        capture_window.protocol("WM_DELETE_WINDOW", on_closing)
    
    def save_student(self):
        """Save student information to database"""
        name = self.student_name_entry.get().strip()
        roll_number = self.student_roll_entry.get().strip()
        department = self.student_dept_entry.get().strip()
        username = self.student_username_entry.get().strip()
        password = self.student_password_entry.get().strip()
        
        # Validate inputs
        if not name or not roll_number or not department or not username or not password:
            show_message("Error", "All fields are required", "error")
            return
        
        # Create student account
        user_id = self.db.add_user(username, password, "student")
        if not user_id:
            show_message("Error", "Username already exists", "error")
            return
        
        # Add student profile
        student_id = self.db.add_student(user_id, name, roll_number, department, self.face_encoding)
        if not student_id:
            show_message("Error", "Roll number already exists", "error")
            return
        
        show_message("Success", f"Student {name} added successfully!", "info")
        self.clear_student_form()
        self.load_student_list()
    
    def start_camera(self):
        """Start the camera for attendance detection"""
        if self.video_capture is None:
            self.video_capture = VideoCapture()
            self.video_capture.start()
            
            # Get the face data from database and train the recognizer
            face_data = self.db.get_all_face_encodings()
            faces, labels = self.face_detector.prepare_faces_for_training(face_data)
            
            if faces and labels:
                self.face_detector.train_recognizer(faces, labels)
            
            # Function to process frames and detect faces
            def process_frame(frame):
                # Resize frame for faster processing
                small_frame = self.face_detector.resize_frame(frame, width=320)
                
                # Get face locations and processed faces
                face_locations, face_samples = self.face_detector.get_face_encodings(small_frame)
                
                # Draw rectangles on faces
                for (x, y, w, h) in face_locations:
                    # Scale back to original size
                    scale = frame.shape[1] / small_frame.shape[1]
                    x = int(x * scale)
                    y = int(y * scale)
                    w = int(w * scale)
                    h = int(h * scale)
                    
                    # Draw rectangle
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Process each detected face for attendance
                for i, face_encoding in enumerate(face_samples):
                    match_found, student_id = self.face_detector.compare_faces(None, face_encoding)
                    
                    if match_found:
                        self.mark_attendance(student_id)
                
                return frame
            
            # Function to update the video display
            def update_video_display(frame):
                tk_img = convert_cv_to_tkinter(frame, 400, 300)
                self.camera_label.configure(image=tk_img)
                self.camera_label.image = tk_img
            
            # Start video capture thread
            self.video_capture.start_update_thread(update_video_display, process_frame)
            
            # Update buttons
            self.start_camera_button.configure(state=tk.DISABLED)
            self.stop_camera_button.configure(state=tk.NORMAL)
    
    def stop_camera(self):
        """Stop the camera"""
        if self.video_capture:
            self.video_capture.stop()
            self.video_capture = None
            
            # Update buttons
            self.start_camera_button.configure(state=tk.NORMAL)
            self.stop_camera_button.configure(state=tk.DISABLED)
            
            # Clear camera display
            self.camera_label.configure(image='')
    
    def mark_attendance(self, student_id):
        """Mark attendance for a student"""
        with self.detection_lock:
            # Get current time
            date_str, time_str = get_current_datetime()
            
            # Avoid duplicate detections within 5 seconds
            if student_id in self.last_detection_time:
                last_time = self.last_detection_time[student_id]
                if (datetime.datetime.now() - last_time).total_seconds() < 5:
                    return
            
            # Update last detection time
            self.last_detection_time[student_id] = datetime.datetime.now()
            
            # Get student info
            student = self.db.get_student_by_id(student_id)
            if student:
                student_id, user_id, name, roll_number, department, _ = student
                
                # Mark attendance in database
                self.db.mark_attendance(student_id, date_str, time_str)
                
                # Add to detection tree
                self.detection_tree.insert("", 0, values=(time_str, name, roll_number, "Present"))
    
    def generate_attendance_report(self):
        """Generate attendance report for the selected date range"""
        from_date = self.from_date_entry.get().strip()
        to_date = self.to_date_entry.get().strip()
        
        if not from_date or not to_date:
            show_message("Error", "Please enter date range", "error")
            return
        
        # Get report data
        report_data = self.db.get_attendance_report(from_date, to_date)
        
        # Clear current items
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)
        
        # Insert new items
        for name, roll_number, department, date, time, status in report_data:
            self.report_tree.insert("", "end", values=(name, roll_number, department, date, time, status))
    
    def logout(self):
        """Logout and show login screen"""
        if self.video_capture:
            self.stop_camera()
        
        self.current_user = None
        self.current_user_role = None
        self.show_login_screen()
    
    def on_closing(self):
        """Handle closing event"""
        if self.video_capture:
            self.stop_camera()
        self.root.destroy()

if __name__ == "__main__":
    import sqlite3  # Import here to avoid circular import
    
    root = tk.Tk()
    app = AttendanceSystem(root)
    root.mainloop() 