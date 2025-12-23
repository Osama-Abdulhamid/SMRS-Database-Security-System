import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
import db_helper
import app_state
from theme_helper import AppTheme, ACCENT_COLOR

class AdminWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Admin Panel - System Management")
        self.geometry("1150x750")  # كبرنا الشاشة شوية

        AppTheme.apply_styles(self)

        ttk.Label(self, text="Administrator Control Panel", style="Header.TLabel").pack(pady=10)

        tabs = ttk.Notebook(self)
        tabs.pack(fill='both', expand=True, padx=10, pady=5)

        self.tab_users = ttk.Frame(tabs)
        self.tab_courses = ttk.Frame(tabs)
        self.tab_requests = ttk.Frame(tabs)

        tabs.add(self.tab_users, text="Manage Users")
        tabs.add(self.tab_courses, text="Manage Courses, Enrollments & TAs")
        tabs.add(self.tab_requests, text="Role Requests")

        self.setup_users_tab()
        self.setup_courses_tab()
        self.setup_requests_tab()

    # ---------------------------------------------------------
    # 1. Manage Users
    # ---------------------------------------------------------
    def setup_users_tab(self):
        # ... (نفس كود المستخدمين السابق) ...
        f = ttk.LabelFrame(self.tab_users, text=" Add New User ", padding=10)
        f.pack(fill='x', padx=10, pady=5)

        grid_frame = ttk.Frame(f)
        grid_frame.pack(fill='x')

        ttk.Label(grid_frame, text="Username:").grid(row=0, column=0, padx=5)
        self.ent_u = ttk.Entry(grid_frame)
        self.ent_u.grid(row=0, column=1, padx=5)

        ttk.Label(grid_frame, text="Password:").grid(row=0, column=2, padx=5)
        self.ent_p = ttk.Entry(grid_frame)
        self.ent_p.grid(row=0, column=3, padx=5)

        ttk.Label(grid_frame, text="Role:").grid(row=0, column=4, padx=5)
        self.cb_r = ttk.Combobox(grid_frame, values=["Student", "Instructor", "TA", "Admin", "Guest"], width=10)
        self.cb_r.grid(row=0, column=5, padx=5)
        self.cb_r.current(0)

        ttk.Button(f, text="Add User", command=self.add_user).pack(pady=10)

        self.tree_users = ttk.Treeview(self.tab_users, columns=("ID", "User", "Role", "Clearance"), show='headings')
        for c in self.tree_users['columns']: self.tree_users.heading(c, text=c)
        self.tree_users.pack(fill='both', expand=True, padx=10, pady=5)
        
        btn_frame = ttk.Frame(self.tab_users)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Delete User", style="Danger.TButton", command=self.delete_user).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Reset Password", command=self.reset_user_password).pack(side='left', padx=5)

        self.load_users()

    # ---------------------------------------------------------
    # 2. Manage Courses & Enrollments & TAs (Layout Fixed)
    # ---------------------------------------------------------
    def setup_courses_tab(self):
        # تقسيم الشاشة
        paned = tk.PanedWindow(self.tab_courses, orient=tk.HORIZONTAL)
        paned.pack(fill='both', expand=True, padx=5, pady=5)

        left_frame = ttk.Frame(paned)
        right_frame = ttk.Frame(paned)
        paned.add(left_frame, minsize=400)
        paned.add(right_frame, minsize=450)

        # --- اليسار: إنشاء المواد ---
        ttk.Label(left_frame, text="1. Create Course", style="Welcome.TLabel").pack(anchor='w')
        f_create = ttk.LabelFrame(left_frame, text=" Course Details ")
        f_create.pack(fill='x', pady=5)
        
        ttk.Label(f_create, text="Name:").grid(row=0, column=0, padx=5)
        self.ent_c_name = ttk.Entry(f_create, width=15)
        self.ent_c_name.grid(row=0, column=1)
        
        ttk.Label(f_create, text="Inst:").grid(row=0, column=2, padx=5)
        self.cb_c_inst = ttk.Combobox(f_create, width=15)
        self.cb_c_inst.grid(row=0, column=3)

        ttk.Label(f_create, text="Info:").grid(row=1, column=0, padx=5)
        self.ent_c_desc = ttk.Entry(f_create, width=35)
        self.ent_c_desc.grid(row=1, column=1, columnspan=3, pady=5)

        ttk.Button(f_create, text="Create", command=self.add_course).grid(row=2, column=1, pady=10)

        self.tree_courses = ttk.Treeview(left_frame, columns=("ID", "Name", "Inst"), show='headings')
        self.tree_courses.heading("ID", text="ID")
        self.tree_courses.heading("Name", text="Course")
        self.tree_courses.heading("Inst", text="Instructor")
        self.tree_courses.column("ID", width=30)
        self.tree_courses.pack(fill='both', expand=True)


        # --- اليمين: (2. تسجيل الطلاب) و (3. تعيين المعيدين) ---
        
        # حاوية للأجزاء العلوية عشان نضمن ظهورها
        top_right = ttk.Frame(right_frame)
        top_right.pack(side='top', fill='x')

        # جزء 2: تسجيل الطلاب
        ttk.Label(top_right, text="2. Enroll Student", style="Welcome.TLabel").pack(anchor='w')
        f_enroll = ttk.LabelFrame(top_right, text=" Assign Student to Course ")
        f_enroll.pack(fill='x', pady=5)

        self.cb_enroll_student = ttk.Combobox(f_enroll, width=18)
        self.cb_enroll_student.pack(side='left', padx=5, pady=5)
        self.cb_enroll_course = ttk.Combobox(f_enroll, width=18)
        self.cb_enroll_course.pack(side='left', padx=5, pady=5)
        ttk.Button(f_enroll, text="Enroll", command=self.enroll_student).pack(side='left', padx=5)

        # جزء 3: تعيين المعيدين (المشكلة كانت هنا وصلحناها)
        ttk.Label(top_right, text="3. Assign TA (Assistant)", style="Welcome.TLabel").pack(anchor='w', pady=(15, 0))
        f_ta = ttk.LabelFrame(top_right, text=" Assign TA to Course ")
        f_ta.pack(fill='x', pady=5)

        self.cb_assign_ta = ttk.Combobox(f_ta, width=18)
        self.cb_assign_ta.pack(side='left', padx=5, pady=5)
        
        self.cb_assign_course_ta = ttk.Combobox(f_ta, width=18)
        self.cb_assign_course_ta.pack(side='left', padx=5, pady=5)
        
        ttk.Button(f_ta, text="Assign TA", command=self.assign_ta).pack(side='left', padx=5)

        # جدول العرض في المساحة المتبقية
        ttk.Label(right_frame, text="Enrollment & Assignment Log").pack(anchor='w', pady=(10,0))
        self.tree_enroll = ttk.Treeview(right_frame, columns=("ID", "User", "Course"), show='headings')
        self.tree_enroll.heading("ID", text="ID")
        self.tree_enroll.heading("User", text="Student/TA Name")
        self.tree_enroll.heading("Course", text="Course")
        self.tree_enroll.column("ID", width=30)
        self.tree_enroll.pack(fill='both', expand=True)

        self.load_all_data()

    # ---------------------------------------------------------
    # 3. Role Requests
    # ---------------------------------------------------------
    def setup_requests_tab(self):
        self.tree_req = ttk.Treeview(self.tab_requests, columns=("ID", "User", "Requested", "Status"), show='headings')
        for c in self.tree_req['columns']: self.tree_req.heading(c, text=c)
        self.tree_req.pack(fill='both', expand=True, padx=10, pady=10)
        
        btn_f = ttk.Frame(self.tab_requests)
        btn_f.pack(pady=5)
        ttk.Button(btn_f, text="Approve", command=lambda: self.process_req("Approve")).pack(side='left', padx=5)
        ttk.Button(btn_f, text="Deny", style="Danger.TButton", command=lambda: self.process_req("Deny")).pack(side='left')
        
        self.load_requests()

    # --- Logic ---
    def load_all_data(self):
        self.load_courses()
        self.load_instructors_combo()
        self.load_students_combo()
        self.load_tas_combo() # تحميل المعيدين
        self.load_enrollments_list()

    def add_user(self):
        u, p, r = self.ent_u.get(), self.ent_p.get(), self.cb_r.get()
        cl = 1
        if r == "Admin": cl = 4
        elif r == "Instructor": cl = 3
        elif r in ["TA", "Student"]: cl = 2
        try:
            db_helper.execute_non_query("EXEC usp_AddUser ?, ?, ?, ?", (u, p, r, cl))
            self.load_users()
            self.load_all_data() # تحديث كل القوائم
            messagebox.showinfo("Success", "User Added")
        except Exception as e: messagebox.showerror("Error", str(e))

    def delete_user(self):
        # ... (نفس دالة الحذف القوية السابقة) ...
        sel = self.tree_users.selection()
        if not sel: return
        uid = self.tree_users.item(sel[0])['values'][0]
        if not messagebox.askyesno("Confirm", "Delete User & All Data?"): return
        try:
            db_helper.execute_non_query("DELETE FROM RoleRequests WHERE UserID=?", (uid,))
            db_helper.execute_non_query("DELETE FROM Attendance WHERE StudentID=?", (uid,))
            db_helper.execute_non_query("DELETE FROM Enrollments WHERE StudentID=?", (uid,))
            db_helper.execute_non_query("DELETE FROM CourseTAs WHERE TA_ID=?", (uid,))
            db_helper.execute_non_query("UPDATE Course SET InstructorID=NULL WHERE InstructorID=?", (uid,))
            db_helper.execute_non_query("DELETE FROM Student WHERE UserID=?", (uid,))
            db_helper.execute_non_query("DELETE FROM Instructor WHERE UserID=?", (uid,))
            db_helper.execute_non_query("DELETE FROM Users WHERE UserID=?", (uid,))
            self.load_users()
            self.load_all_data()
            messagebox.showinfo("Done", "User Deleted")
        except Exception as e: messagebox.showerror("Error", str(e))

    def reset_user_password(self):
        sel = self.tree_users.selection()
        if not sel: return
        uid, uname = self.tree_users.item(sel[0])['values'][0], self.tree_users.item(sel[0])['values'][1]
        
        pop = Toplevel(self)
        pop.title("Reset Password")
        AppTheme.apply_styles(pop)
        ttk.Label(pop, text=f"New Pass for {uname}:").pack(pady=10)
        e = ttk.Entry(pop, show="*")
        e.pack()
        def sv():
            if not e.get(): return
            db_helper.execute_non_query("EXEC usp_ChangePassword ?, ?", (uid, e.get()))
            pop.destroy()
            messagebox.showinfo("Done", "Password Changed")
        ttk.Button(pop, text="Save", command=sv).pack(pady=10)

    def load_users(self):
        self.tree_users.delete(*self.tree_users.get_children())
        rows = db_helper.execute_query("EXEC sp_GetAllUsers")
        for r in rows: self.tree_users.insert("", "end", values=(r['UserID'], r['Username'], r['UserRole'], r['ClearanceLevel']))

    def load_instructors_combo(self):
        rows = db_helper.execute_query("SELECT Username FROM Users WHERE UserRole='Instructor'")
        self.cb_c_inst['values'] = [r['Username'] for r in rows]

    def load_students_combo(self):
        rows = db_helper.execute_query("SELECT Username FROM Users WHERE UserRole='Student'")
        self.cb_enroll_student['values'] = [r['Username'] for r in rows]

    def load_tas_combo(self):
        # الدالة دي بتملأ قائمة الـ TA
        rows = db_helper.execute_query("SELECT Username FROM Users WHERE UserRole='TA'")
        # تنويه: لو القائمة دي فضلت فاضية، ده معناه إنك لسه مأضفتش يوزر نوعه TA
        self.cb_assign_ta['values'] = [r['Username'] for r in rows]

    def add_course(self):
        try:
            inst_id = None
            if self.cb_c_inst.get():
                r = db_helper.execute_query("SELECT UserID FROM Users WHERE Username=?", (self.cb_c_inst.get(),))
                if r: inst_id = r[0]['UserID']
            db_helper.execute_non_query("INSERT INTO Course (CourseName, Description, PublicInfo, InstructorID) VALUES (?, ?, ?, ?)", 
                                        (self.ent_c_name.get(), "Secret", self.ent_c_desc.get(), inst_id))
            self.load_courses()
            messagebox.showinfo("Done", "Course Created")
        except Exception as e: messagebox.showerror("Error", str(e))

    def enroll_student(self):
        try:
            sid = db_helper.execute_query("SELECT UserID FROM Users WHERE Username=?", (self.cb_enroll_student.get(),))[0]['UserID']
            cid = db_helper.execute_query("SELECT CourseID FROM Course WHERE CourseName=?", (self.cb_enroll_course.get(),))[0]['CourseID']
            db_helper.execute_non_query("INSERT INTO Enrollments (StudentID, CourseID, Grade) VALUES (?, ?, 'Pending')", (sid, cid))
            self.load_enrollments_list()
            messagebox.showinfo("Done", "Student Enrolled")
        except Exception as e: messagebox.showerror("Error", str(e))

    def assign_ta(self):
        # دالة ربط المعيد
        try:
            ta_name = self.cb_assign_ta.get()
            c_name = self.cb_assign_course_ta.get()
            if not ta_name or not c_name: return

            ta_id = db_helper.execute_query("SELECT UserID FROM Users WHERE Username=?", (ta_name,))[0]['UserID']
            cid = db_helper.execute_query("SELECT CourseID FROM Course WHERE CourseName=?", (c_name,))[0]['CourseID']
            
            db_helper.execute_non_query("INSERT INTO CourseTAs (TA_ID, CourseID) VALUES (?, ?)", (ta_id, cid))
            messagebox.showinfo("Done", f"Assigned {ta_name} to {c_name}")
        except Exception as e: messagebox.showerror("Error", str(e))

    def load_courses(self):
        self.tree_courses.delete(*self.tree_courses.get_children())
        rows = db_helper.execute_query("SELECT c.CourseID, c.CourseName, u.Username FROM Course c LEFT JOIN Users u ON c.InstructorID=u.UserID")
        c_names = []
        for r in rows:
            self.tree_courses.insert("", "end", values=(r['CourseID'], r['CourseName'], r['Username'] or "-"))
            c_names.append(r['CourseName'])
        self.cb_enroll_course['values'] = c_names
        self.cb_assign_course_ta['values'] = c_names

    def load_enrollments_list(self):
        # عرض التسجيلات فقط للتسهيل
        self.tree_enroll.delete(*self.tree_enroll.get_children())
        rows = db_helper.execute_query("SELECT e.EnrollmentID, u.Username, c.CourseName FROM Enrollments e JOIN Users u ON e.StudentID=u.UserID JOIN Course c ON e.CourseID=c.CourseID")
        for r in rows: self.tree_enroll.insert("", "end", values=(r['EnrollmentID'], r['Username'], r['CourseName']))

    def load_requests(self):
        self.tree_req.delete(*self.tree_req.get_children())
        rows = db_helper.execute_query("SELECT r.RequestID, u.Username, r.RequestedRole, r.RequestStatus FROM RoleRequests r JOIN Users u ON r.UserID=u.UserID WHERE r.RequestStatus='Pending'")
        for r in rows: self.tree_req.insert("", "end", values=(r['RequestID'], r['Username'], r['RequestedRole'], r['RequestStatus']))

    def process_req(self, act):
        sel = self.tree_req.selection()
        if not sel: return
        rid = self.tree_req.item(sel[0])['values'][0]
        try:
            db_helper.execute_non_query("EXEC usp_ProcessRoleRequest ?, ?, ?, 'GUI'", (rid, app_state.current_user["UserID"], act))
            self.load_requests()
            self.load_users()
            self.load_all_data()
            messagebox.showinfo("Done", f"Request {act}ed")
        except Exception as e: messagebox.showerror("Error", str(e))