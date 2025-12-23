import tkinter as tk
from tkinter import ttk, messagebox
import db_helper
import app_state
from theme_helper import AppTheme, ACCENT_COLOR

class InstructorWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.role = app_state.current_user["Role"]
        self.uid = app_state.current_user["UserID"]
        
        # ضبط العنوان حسب الدور
        title_role = "Instructor" if self.role == "Instructor" else "Teacher Assistant"
        self.title(f"{title_role} Dashboard")
        self.geometry("850x600")

        AppTheme.apply_styles(self)
        
        ttk.Label(self, text=f"{title_role} Control Panel", style="Header.TLabel").pack(pady=10)

        tabs = ttk.Notebook(self)
        tabs.pack(fill='both', expand=True, padx=10, pady=5)

        self.tab_att = ttk.Frame(tabs)
        self.tab_grades = ttk.Frame(tabs)

        # 1. تبويب الحضور (متاح للاثنين)
        tabs.add(self.tab_att, text="Manage Attendance")
        
        # 2. تبويب الدرجات (أصبح متاح للاثنين الآن)
        tabs.add(self.tab_grades, text="Manage Grades")

        # تشغيل الدوال
        self.setup_grades()
        self.setup_attendance()

    # --- Grades Logic (Instructor & TA) ---
    def setup_grades(self):
        f = ttk.Frame(self.tab_grades)
        f.pack(fill='x', pady=5)
        ttk.Label(f, text="Select Course:").pack(side='left', padx=5)
        self.cb_g_course = ttk.Combobox(f)
        self.cb_g_course.pack(side='left', padx=5)
        ttk.Button(f, text="Load Students", command=self.load_grades).pack(side='left')

        # تحميل الكورسات حسب الدور (التعديل الجديد)
        if self.role == "Instructor":
            # الدكتور يشوف مواده المربوطة بيه مباشرة
            rows = db_helper.execute_query("SELECT CourseName FROM Course WHERE InstructorID=?", (self.uid,))
        else:
            # المعيد يشوف المواد المتعين فيها في جدول CourseTAs
            rows = db_helper.execute_query("""
                SELECT c.CourseName 
                FROM Course c 
                JOIN CourseTAs t ON c.CourseID = t.CourseID 
                WHERE t.TA_ID = ?
            """, (self.uid,))
            
        self.cb_g_course['values'] = [r['CourseName'] for r in rows]

        # جدول الدرجات
        self.tree_g = ttk.Treeview(self.tab_grades, columns=("EID", "Student", "Grade"), show='headings')
        for c in self.tree_g['columns']: self.tree_g.heading(c, text=c)
        self.tree_g.pack(fill='both', expand=True, pady=10)

        # خانة التعديل
        f2 = ttk.Frame(self.tab_grades)
        f2.pack(pady=5)
        ttk.Label(f2, text="New Grade:").pack(side='left')
        self.ent_grade = ttk.Entry(f2, width=10)
        self.ent_grade.pack(side='left', padx=5)
        ttk.Button(f2, text="Update Grade", command=self.update_grade).pack(side='left')

    def load_grades(self):
        c_name = self.cb_g_course.get()
        if not c_name: return
        sql = """
            SELECT e.EnrollmentID, u.Username, e.Grade 
            FROM Enrollments e 
            JOIN Users u ON e.StudentID = u.UserID
            JOIN Course c ON e.CourseID = c.CourseID
            WHERE c.CourseName = ?
        """
        rows = db_helper.execute_query(sql, (c_name,))
        self.tree_g.delete(*self.tree_g.get_children())
        for r in rows:
            self.tree_g.insert("", "end", values=(r['EnrollmentID'], r['Username'], r['Grade']))

    def update_grade(self):
        sel = self.tree_g.selection()
        if not sel: 
            messagebox.showwarning("Select", "Please select a student first")
            return
            
        eid = self.tree_g.item(sel[0])['values'][0]
        val = self.ent_grade.get()
        
        try:
            db_helper.execute_non_query("UPDATE Enrollments SET Grade=? WHERE EnrollmentID=?", (val, eid))
            self.load_grades() # تحديث القائمة
            messagebox.showinfo("Done", "Grade Updated Successfully")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # --- Attendance Logic (Instructor & TA) ---
    def setup_attendance(self):
        f = ttk.Frame(self.tab_att)
        f.pack(fill='x', pady=5)
        
        ttk.Label(f, text="Select Course:").pack(side='left', padx=5)
        self.cb_a_course = ttk.Combobox(f)
        self.cb_a_course.pack(side='left', padx=5)
        ttk.Button(f, text="Load Class List", command=self.load_att_list).pack(side='left', padx=5)

        # نفس منطق تحميل الكورسات (دكتور vs معيد)
        if self.role == "Instructor":
            rows = db_helper.execute_query("SELECT CourseName FROM Course WHERE InstructorID=?", (self.uid,))
        else:
            rows = db_helper.execute_query("""
                SELECT c.CourseName FROM Course c 
                JOIN CourseTAs t ON c.CourseID = t.CourseID 
                WHERE t.TA_ID = ?
            """, (self.uid,))
        
        self.cb_a_course['values'] = [r['CourseName'] for r in rows]

        # جدول الطلاب
        self.tree_att = ttk.Treeview(self.tab_att, columns=("SID", "Name", "LastStatus"), show='headings')
        self.tree_att.heading("SID", text="Student ID")
        self.tree_att.heading("Name", text="Student Name")
        self.tree_att.heading("LastStatus", text="Info")
        self.tree_att.pack(fill='both', expand=True, pady=10)

        # أزرار الغياب
        btn_f = ttk.Frame(self.tab_att)
        btn_f.pack(pady=10)
        
        ttk.Button(btn_f, text="Mark PRESENT", command=lambda: self.mark_attendance(1)).pack(side='left', padx=10)
        ttk.Button(btn_f, text="Mark ABSENT", style="Danger.TButton", command=lambda: self.mark_attendance(0)).pack(side='left', padx=10)

    def load_att_list(self):
        c_name = self.cb_a_course.get()
        if not c_name: return
        
        sql = """
            SELECT u.UserID, u.Username 
            FROM Enrollments e 
            JOIN Users u ON e.StudentID = u.UserID 
            JOIN Course c ON e.CourseID = c.CourseID
            WHERE c.CourseName = ?
        """
        rows = db_helper.execute_query(sql, (c_name,))
        self.tree_att.delete(*self.tree_att.get_children())
        for r in rows:
            self.tree_att.insert("", "end", values=(r['UserID'], r['Username'], "-"))

    def mark_attendance(self, status_bit):
        sel = self.tree_att.selection()
        if not sel: 
            messagebox.showwarning("Select", "Please select students first")
            return
        
        c_name = self.cb_a_course.get()
        if not c_name: return

        # Get Course ID
        c_row = db_helper.execute_query("SELECT CourseID FROM Course WHERE CourseName=?", (c_name,))
        if not c_row: return
        cid = c_row[0]['CourseID']

        count = 0
        for item in sel:
            sid = self.tree_att.item(item)['values'][0]
            try:
                db_helper.execute_non_query(
                    "INSERT INTO Attendance (StudentID, CourseID, Status, DateRecorded) VALUES (?, ?, ?, GETDATE())",
                    (sid, cid, status_bit)
                )
                count += 1
            except Exception as e:
                print(e)
        
        msg = "Present" if status_bit == 1 else "Absent"
        messagebox.showinfo("Success", f"Marked {count} students as {msg}")