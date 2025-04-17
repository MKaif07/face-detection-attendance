import sqlite3
import os
import numpy as np
import pickle

class DatabaseManager:
    def __init__(self, db_path='attendance.db'):
        self.db_path = db_path
        self.create_database()
    
    def create_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Read schema.sql file
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r') as f:
            schema = f.read()
        
        # Execute schema
        cursor.executescript(schema)
        conn.commit()
        conn.close()
    
    def add_user(self, username, password, role):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, password, role)
            )
            conn.commit()
            user_id = cursor.lastrowid
            return user_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def verify_user(self, username, password):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, role FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        result = cursor.fetchone()
        conn.close()
        return result if result else None
    
    def add_student(self, user_id, name, roll_number, department, face_image=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Convert face image to binary data
            encoded_data = pickle.dumps(face_image) if face_image is not None else None
            
            cursor.execute(
                "INSERT INTO students (user_id, name, roll_number, department, face_encoding) VALUES (?, ?, ?, ?, ?)",
                (user_id, name, roll_number, department, encoded_data)
            )
            conn.commit()
            student_id = cursor.lastrowid
            return student_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def update_student_face(self, student_id, face_image):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Convert face image to binary data
            encoded_data = pickle.dumps(face_image)
            
            cursor.execute(
                "UPDATE students SET face_encoding = ? WHERE student_id = ?",
                (encoded_data, student_id)
            )
            conn.commit()
            return True
        except:
            return False
        finally:
            conn.close()
    
    def get_student_by_roll(self, roll_number):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM students WHERE roll_number = ?",
            (roll_number,)
        )
        result = cursor.fetchone()
        conn.close()
        return result
    
    def get_student_by_id(self, student_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM students WHERE student_id = ?",
            (student_id,)
        )
        result = cursor.fetchone()
        conn.close()
        return result
    
    def get_all_students(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, name, roll_number, department FROM students")
        students = cursor.fetchall()
        conn.close()
        return students
    
    def get_all_face_encodings(self):
        """Get all face encodings from the database for face recognition"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, face_encoding FROM students WHERE face_encoding IS NOT NULL")
        results = cursor.fetchall()
        conn.close()
        return results  # Return raw data for processing by face detector
    
    def mark_attendance(self, student_id, date, time, status="present"):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Check if attendance already marked
            cursor.execute(
                "SELECT * FROM attendance WHERE student_id = ? AND date = ?",
                (student_id, date)
            )
            if cursor.fetchone():
                # Update existing attendance
                cursor.execute(
                    "UPDATE attendance SET time = ?, status = ? WHERE student_id = ? AND date = ?",
                    (time, status, student_id, date)
                )
            else:
                # Add new attendance
                cursor.execute(
                    "INSERT INTO attendance (student_id, date, time, status) VALUES (?, ?, ?, ?)",
                    (student_id, date, time, status)
                )
            conn.commit()
            return True
        except:
            return False
        finally:
            conn.close()
    
    def get_attendance_report(self, from_date=None, to_date=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
        SELECT s.name, s.roll_number, s.department, a.date, a.time, a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.student_id
        """
        
        params = []
        if from_date and to_date:
            query += " WHERE a.date BETWEEN ? AND ?"
            params = [from_date, to_date]
        
        query += " ORDER BY a.date DESC, s.name"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return results 