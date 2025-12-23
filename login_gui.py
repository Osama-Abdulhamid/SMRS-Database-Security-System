import tkinter as tk
from tkinter import ttk, messagebox
import db_helper
import app_state
from dashboard_gui import DashboardWindow
# استوردنا ACCENT_COLOR عشان نلون الزرار بالأزرق النيون
from theme_helper import AppTheme, ACCENT_COLOR 

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SRMS Secure Login")
        self.geometry("400x400")
        
        # تطبيق الثيم العام (الغامق) من ملف theme_helper
        AppTheme.apply_styles(self)

        # الإطار الرئيسي
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(expand=True, fill='both')

        # العنوان
        ttk.Label(main_frame, text="أهلا بيك في الجامعة العالمية للفهلوة المتقدمة", style="Header.TLabel").pack(pady=(20, 30))

        # إطار المدخلات
        input_frame = ttk.LabelFrame(main_frame, text=" User Login ", padding=20)
        input_frame.pack(fill='x', pady=10)

        # اسم المستخدم
        ttk.Label(input_frame, text="Username:").pack(anchor='w')
        self.ent_user = ttk.Entry(input_frame, width=30)
        self.ent_user.pack(fill='x', pady=5)

        # كلمة المرور
        ttk.Label(input_frame, text="Password:").pack(anchor='w', pady=(10, 0))
        self.ent_pass = ttk.Entry(input_frame, show="*", width=30)
        self.ent_pass.pack(fill='x', pady=5)

        # --- منطقة الأزرار ---
        
        # 1. زرار الدخول
        # خليناه أزرق (ACCENT_COLOR) عشان يبان في الدارك مود
        self.btn_login = tk.Button(
            main_frame, 
            text="SECURE LOGIN", 
            command=self.login,
            bg=ACCENT_COLOR,     # الخلفية زرقاء
            fg="white",          # الكتابة أبيض
            font=("Helvetica", 11, "bold"),
            relief="flat",       # بدون برواز
            pady=8,
            cursor="hand2",
            activebackground="#2980b9", # لون أغمق عند الضغط
            activeforeground="white"
        )
        self.btn_login.pack(fill='x', pady=(20, 10))

        # 2. زرار الزائر
        ttk.Button(main_frame, text="Continue as Guest", command=self.guest_login).pack(fill='x')

        # تأثير الماوس (Hover Effect)
        self.btn_login.bind("<Enter>", self.on_enter)
        self.btn_login.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        # لما الماوس يقف عليه نخليه أزرق أغمق شوية
        self.btn_login['background'] = "#2980b9" 
    
    def on_leave(self, e):
        # يرجع للون الأزرق الأصلي لما الماوس يمشي
        self.btn_login['background'] = ACCENT_COLOR 

    def login(self):
        user = self.ent_user.get()
        pwd = self.ent_pass.get()
        try:
            conn = db_helper.get_connection()
            cursor = conn.cursor()
            cursor.execute("EXEC sp_Login ?, ?", user, pwd)
            row = cursor.fetchone()
            conn.close()

            if not row or row[0] == -1:
                messagebox.showerror("Error", "Invalid Username or Password")
                return

            app_state.current_user["UserID"] = row[0]
            app_state.current_user["Role"] = row[1]
            app_state.current_user["Clearance"] = row[2]
            app_state.current_user["Username"] = user

            self.withdraw()
            DashboardWindow(self)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def guest_login(self):
        app_state.current_user["Role"] = "Guest"
        app_state.current_user["Clearance"] = 1
        app_state.current_user["UserID"] = 0
        app_state.current_user["Username"] = "Guest"
        self.withdraw()
        DashboardWindow(self)

if __name__ == "__main__":
    LoginWindow().mainloop()