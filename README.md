# 📊 Smart Attendance Analytics Dashboard

A full-stack web application for managing and analysing college attendance. Admins can manage students, faculty, departments and subjects, record daily attendance, and view analytics and downloadable reports.

## ✨ Features
- 🔐 **Login-protected** admin access
- 👩‍🎓 **Manage records**: add, edit and delete students, faculty, departments and subjects
- 🗓️ **Attendance tracking**: mark Present / Absent per student, subject and date
- 📈 **Dashboard**: total students, faculty and subjects, overall attendance %, present vs. absent counts
- 👤 **Student profiles** with subject-wise attendance percentage
- 🏷️ **Attendance categories**: each student is classified as Excellent (≥85%), Good (≥75%), Average (≥65%) or Low Attendance
- 📄 **Reports**: export student lists to **PDF** and **Excel**

## 🛠️ Tech Stack
| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database | MySQL (PyMySQL) |
| Frontend | HTML, CSS (Jinja templates) |
| Reports | ReportLab (PDF), openpyxl (Excel) |

## 🚀 How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a MySQL database named `attendance_system` with the tables `users`, `students`, `faculty`, `departments`, `subjects` and `attendance`.
3. Set your MySQL connection details (host, user, password, database). Keep the password in an environment variable rather than in the code, for example:
   ```bash
   export DB_PASSWORD="your-password"
   ```
4. Start the app:
   ```bash
   python app.py
   ```
5. Open `http://127.0.0.1:5000` in your browser and log in.

## 📁 Project Structure
| File | Purpose |
|---|---|
| `app.py` | Flask routes for login, CRUD, dashboard, prediction and exports |
| `config.py`, `db.py` | Database configuration and connection |
| `*.html`, `dashboard.css` | Page templates and styling |
| `Smart Attendance Analytics System.pdf` | Project report |
| `Student_Report.pdf / .xlsx` | Sample exported reports |

## 🔮 Future Scope
- Role-based logins for faculty and students
- Attendance trend charts per subject and month
- Automatic alerts for students below the attendance threshold

## 👩‍💻 Author
**Nandini Madugula** — B.Tech Electrical & Computer Engineering, Amrita Vishwa Vidyapeetham, Coimbatore
[LinkedIn](https://www.linkedin.com/in/madugula-nandini)
