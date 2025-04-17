# Face Detection Attendance System

A facial recognition-based attendance system built with OpenCV and Tkinter.

## Features

- Face detection and recognition for attendance
- Two user roles: admin and student
- Admin can add new students with facial recognition
- Students can mark their attendance using face recognition
- View attendance reports and history
- SQLite database for storing user data and attendance records

## Requirements

- Python 3.6 or higher
- OpenCV
- face_recognition library (requires dlib)
- Tkinter
- Pillow
- NumPy

## Installation

1. Clone the repository:
```
git clone https://github.com/MKaif07/face-detection-attendance.git
cd face-detection-attendance
```

2. Install the dependencies:
```
pip install -r requirements.txt
```

Note: The face_recognition library requires dlib which may need additional setup. Please refer to the [dlib installation guide](https://github.com/davisking/dlib) for more details.

## Usage

1. Run the main script:
```
python main.py
```

2. Login with the default admin credentials:
   - Username: admin
   - Password: admin123

3. As an admin, you can:
   - Add new students
   - Capture face data for students
   - Take attendance
   - View attendance reports

4. Students can log in with their credentials to:
   - Mark attendance using facial recognition
   - View their attendance history

## System Components

- **Database**: SQLite database storing user accounts, student information, and attendance records
- **Face Detection**: Uses OpenCV and face_recognition for detecting and recognizing faces
- **GUI**: Tkinter-based user interface with separate views for admin and student roles

## Project Structure

```
attendance_system/
├── database/
│   ├── schema.sql
│   └── db_manager.py
├── models/
├── utils/
│   ├── face_utils.py
│   └── ui_utils.py
├── app.py
├── main.py
└── requirements.txt
```

## Notes

- When adding a student, make sure the face is clearly visible to the camera
- For best recognition results, ensure good lighting conditions
- The system uses a tolerance level of 0.6 for face matching (configurable in the code)

## License

This project is licensed under the MIT License - see the LICENSE file for details. 