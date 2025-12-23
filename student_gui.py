import tkinter as tk
from tkinter import ttk, messagebox
import db_helper
import app_state
from theme_helper import AppTheme, ACCENT_COLOR

class StudentWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Student Portal")
        self.geometry("700x550")
        self.uid = app_state.current_user["UserID"]
        self.username = app_state.current_user["Username"]

        AppTheme.apply_styles(self)

        ttk.Label(self, text=f"Welcome, {self.username}", style="Header.TLabel").pack(pady=10)

        # زرار طلب الترقية
        action_frame = ttk.LabelFrame(self, text=" Actions ", padding=10)
        action_frame.pack(fill='x', padx=10, pady=5)
        ttk.Button(action_frame, text="Request Role Upgrade", command=self.open_request_popup).pack(anchor='w')

        # نظام التبويبات (Grades + Attendance)
        tabs = ttk.Notebook(self)
        tabs.pack(fill='both', expand=True, padx=10, pady=10)

        self.tab_grades = ttk.Frame(tabs)
        self.tab_attendance = ttk.Frame(tabs) # التبويب الجديد

        tabs.add(self.tab_grades, text="My Grades")
        tabs.add(self.tab_attendance, text="My Attendance")

        self.setup_grades_tab()
        self.setup_attendance_tab()

    def setup_grades_tab(self):
        tree = ttk.Treeview(self.tab_grades, columns=("Course", "Grade"), show='headings')
        tree.heading("Course", text="Course Name")
        tree.heading("Grade", text="Grade")
        tree.pack(fill='both', expand=True, pady=10)

        rows = db_helper.execute_query("""
            SELECT c.CourseName, e.Grade 
            FROM Enrollments e 
            JOIN Course c ON e.CourseID = c.CourseID
            WHERE e.StudentID = ?
        """, (self.uid,))
        
        for r in rows:
            tree.insert("", "end", values=(r['CourseName'], r['Grade']))

    def setup_attendance_tab(self):
        # جدول الحضور
        tree = ttk.Treeview(self.tab_attendance, columns=("Course", "Status", "Date"), show='headings')
        tree.heading("Course", text="Course")
        tree.heading("Status", text="Status")
        tree.heading("Date", text="Date Recorded")
        tree.pack(fill='both', expand=True, pady=10)

        # استدعاء Procedure الحضور اللي عملناه في SQL
        # لو مكنش عندك Procedure جاهز، هنستخدم Select عادية
        sql = """
            SELECT c.CourseName, 
                   CASE a.Status WHEN 1 THEN 'Present' ELSE 'Absent' END as St,
                   a.DateRecorded
            FROM Attendance a
            JOIN Course c ON a.CourseID = c.CourseID
            WHERE a.StudentID = ?
            ORDER BY a.DateRecorded DESC
        """
        rows = db_helper.execute_query(sql, (self.uid,))
        
        for r in rows:
            tree.insert("", "end", values=(r['CourseName'], r['St'], r['DateRecorded']))

    def open_request_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Request Upgrade")
        popup.geometry("300x200")
        AppTheme.apply_styles(popup)

        ttk.Label(popup, text="Select Desired Role:").pack(pady=10)
        cb_roles = ttk.Combobox(popup, values=["Instructor", "TA", "Admin"], state="readonly")
        cb_roles.pack(pady=5)
        cb_roles.current(0)

        def submit():
            wanted_role = cb_roles.get()
            try:
                db_helper.execute_non_query(
                    "EXEC usp_SubmitRoleRequest ?, ?, 'Automated Request'", 
                    (self.uid, wanted_role)
                )
                messagebox.showinfo("Success", "Request Sent!")
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {e}")

        ttk.Button(popup, text="Submit Request", command=submit).pack(pady=20)