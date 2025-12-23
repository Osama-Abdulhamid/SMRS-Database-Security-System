import pyodbc

PORT = "1433" 
SERVER_NAME = "127.0.0.1" 

DRIVER = "{ODBC Driver 17 for SQL Server}"
# DRIVER = "{SQL Server}"

CONN_STR = (
    f"Driver={DRIVER};"
    f"Server={SERVER_NAME},{PORT};"  
    "Database=SRMS_DB;"
    "Trusted_Connection=yes;"
)

def get_connection():
    try:
        conn = pyodbc.connect(CONN_STR, timeout=10)
        cursor = conn.cursor()
        # محاولة فتح مفاتيح التشفير (مهم جداً عشان Part A)
        try:
            cursor.execute("EXEC sp_OpenKeys")
        except:
            pass # لو المفتاح مفتوح أصلاً أو فيه مشكلة بسيطة هيكمل
        return conn
    except pyodbc.Error as e:
        print("--- خطأ في الاتصال ---")
        print(e)
        raise e

# ---------------------------------------------------------
# الدوال الإضافية الضرورية لتشغيل باقي البرنامج
# ---------------------------------------------------------

def execute_query(sql, params=None):
    """تستخدم لجمل SELECT وترجع بيانات"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params or [])
        # التأكد إن فيه بيانات راجعة عشان ميعملش Crash
        if cursor.description:
            columns = [c[0] for c in cursor.description]
            rows = [dict(zip(columns, r)) for r in cursor.fetchall()]
        else:
            rows = []
        return rows
    finally:
        conn.close()

def execute_non_query(sql, params=None):
    """تستخدم لجمل INSERT, UPDATE, DELETE"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params or [])
        conn.commit() # حفظ التغييرات
    finally:
        conn.close()