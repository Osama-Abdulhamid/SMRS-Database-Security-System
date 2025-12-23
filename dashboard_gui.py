import tkinter as tk
from tkinter import ttk
import app_state
# استيراد الثيم
from theme_helper import AppTheme, BG_DARK

try:
    from admin_gui import AdminWindow
    from instructor_gui import InstructorWindow
    from student_gui import StudentWindow
    from guest_gui import GuestWindow
except ImportError:
    pass 

class DashboardWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.role = app_state.current_user["Role"]
        self.username = app_state.current_user["Username"] # اسم المستخدم
        
        self.title(f"Dashboard - {self.role}")
        self.geometry("500x450") # تكبير النافذة
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.parent = parent

        # --- تطبيق الثيم ---
        AppTheme.apply_styles(self)
        
        # إطار علوي للترحيب (بلون غامق)
        header_frame = tk.Frame(self, bg=BG_DARK, height=80)
        header_frame.pack(fill='x')
        
        # جمل ترحيبية
        tk.Label(header_frame, text=f"Welcome back, {self.username}!", 
                 font=("Helvetica", 14, "bold"), bg=BG_DARK, fg="white").pack(pady=(15, 5))
        
        tk.Label(header_frame, text=f"Role: {self.role} Account", 
                 font=("Helvetica", 10), bg=BG_DARK, fg="#bdc3c7").pack(pady=(0, 15))


        # إطار للأزرار
        buttons_frame = ttk.Frame(self, padding=30)
        buttons_frame.pack(fill='both', expand=True)

        ttk.Label(buttons_frame, text="Quick Actions", style="Welcome.TLabel").pack(anchor='w', pady=(0, 20))

        # توجيه حسب الدور (نفس المنطق القديم بس بتنسيق جديد)
        if self.role == "Admin":
            self.create_nav_button(buttons_frame, "Admin Control Panel", lambda: AdminWindow(self))
        
        elif self.role in ["Instructor", "TA"]:
            btn_text = "Instructor Dashboard" if self.role == "Instructor" else "TA Dashboard"
            self.create_nav_button(buttons_frame, btn_text, lambda: InstructorWindow(self))
            
        elif self.role == "Student":
            self.create_nav_button(buttons_frame, "My Student Portal", lambda: StudentWindow(self))
            
        elif self.role == "Guest":
            self.create_nav_button(buttons_frame, "View Public Courses Directory", lambda: GuestWindow(self))

        # زرار الخروج بستايل مختلف (Danger Style)
        ttk.Button(buttons_frame, text="Secure Logout", style="Danger.TButton", command=self.logout).pack(side='bottom', pady=20, fill='x')

    def create_nav_button(self, parent, text, command):
        # دالة مساعدة لإنشاء أزرار كبيرة
        btn = ttk.Button(parent, text=text, command=command)
        btn.pack(fill='x', pady=8, ipady=5) # ipady بيزود ارتفاع الزرار من جوه

    def logout(self):
        self.destroy()
        self.parent.deiconify() 
        app_state.current_user = {"UserID": None, "Role": None, "Clearance": 0, "Username": ""}

    def on_close(self):
        self.parent.destroy()