import tkinter as tk
from tkinter import ttk

# --- لوحة الألوان (Dark Mode Palette) ---
BG_MAIN = "#2b2b2b"         # رمادي غامق (الخلفية الأساسية)
BG_SEC = "#1e1e1e"          # أسود فاتح (للعناوين)
ACCENT_COLOR = "#3498db"    # أزرق نيون
TEXT_MAIN = "#ffffff"       # أبيض
TEXT_SEC = "#b0b0b0"        # رمادي فاتح
ENTRY_BG = "#3a3a3a"        # خلفية مربعات الكتابة

# --- حل المشكلة هنا ---
# ضفنا المتغير ده عشان الملفات القديمة متضربش إيرور
BG_DARK = BG_SEC            

HEADER_FONT = ("Helvetica", 16, "bold")
NORMAL_FONT = ("Helvetica", 11)

class AppTheme:
    @staticmethod
    def apply_styles(root):
        # 1. إعداد خلفية النافذة
        root.configure(bg=BG_MAIN)
        
        # 2. إعداد الستايل العام
        style = ttk.Style(root)
        style.theme_use('clam') 

        # --- تنسيق النصوص (Labels) ---
        style.configure("TLabel", background=BG_MAIN, foreground=TEXT_MAIN, font=NORMAL_FONT)
        style.configure("Header.TLabel", font=HEADER_FONT, foreground=ACCENT_COLOR, background=BG_MAIN)
        style.configure("Welcome.TLabel", font=("Helvetica", 13), foreground=TEXT_SEC, background=BG_MAIN)

        # --- تنسيق الأزرار (Buttons) ---
        style.configure("TButton", 
                        font=("Helvetica", 10, "bold"), 
                        background=BG_SEC, 
                        foreground=TEXT_MAIN,
                        borderwidth=0,
                        focuscolor=ACCENT_COLOR)
        
        style.map("TButton",
            background=[('active', ACCENT_COLOR), ('pressed', ACCENT_COLOR)],
            foreground=[('active', 'white'), ('pressed', 'white')]
        )

        style.configure("Danger.TButton", background="#c0392b", foreground="white")
        style.map("Danger.TButton", background=[('active', "#e74c3c")])

        # --- تنسيق الإطارات (Frames) ---
        style.configure("TFrame", background=BG_MAIN)
        style.configure("TLabelframe", background=BG_MAIN, bordercolor=TEXT_SEC)
        style.configure("TLabelframe.Label", font=("Helvetica", 11, "bold"), foreground=ACCENT_COLOR, background=BG_MAIN)

        # --- تنسيق مربعات الإدخال (Entries) ---
        style.configure("TEntry", 
                        fieldbackground=ENTRY_BG, 
                        foreground=TEXT_MAIN,     
                        insertcolor=TEXT_MAIN,    
                        bordercolor=BG_SEC,
                        lightcolor=ACCENT_COLOR,
                        darkcolor=ACCENT_COLOR)

        style.configure("TCombobox", 
                        fieldbackground=ENTRY_BG, 
                        background=BG_SEC,
                        foreground=TEXT_MAIN,
                        arrowcolor=TEXT_MAIN)
        
        # --- تنسيق الجداول (Treeview) ---
        style.configure("Treeview", 
                        background="#333333",       
                        fieldbackground="#333333",  
                        foreground=TEXT_MAIN,       
                        rowheight=25)
        
        style.configure("Treeview.Heading", 
                        background=BG_SEC, 
                        foreground=TEXT_MAIN, 
                        font=("Helvetica", 10, "bold"),
                        relief="flat")
        
        style.map("Treeview", background=[('selected', ACCENT_COLOR)], foreground=[('selected', 'white')])

        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])