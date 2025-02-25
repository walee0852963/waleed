import tkinter as tk
from tkinter import ttk
import sqlite3
import random

# ✅ إنشاء قاعدة بيانات للحجوزات
conn = sqlite3.connect("bookings.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT,
        service TEXT,
        date TEXT,
        time TEXT
    )
""")
conn.commit()

# ✅ قاعدة بيانات الردود الجاهزة
responses = {
    "مرحبا": ["أهلاً وسهلاً! كيف يمكنني مساعدتك اليوم؟ 😊", "مرحبًا بك! كيف أساعدك؟"],
    "كيف حالك": ["أنا مجرد برنامج، لكني بخير! 😃", "أعمل بكفاءة، شكرًا لسؤالك!"],
    "عرض الخدمات": ["🔹 لدينا: حجوزات الفنادق، تذاكر الطيران، حجوزات السيارات، المطاعم، والمنتجعات."],
    "كيف احجز": ["سهل جدًا! فقط أخبرني باسمك، ثم نوع الخدمة التي تريدها، وسأتولى الباقي. 😃"],
    "من انت": ["أنا بوت الحجز الخاص بك! 🤖 مهمتي مساعدتك في إدارة الحجوزات بسهولة."],
    "شكرا": ["على الرحب والسعة! 😊", "أي وقت! إذا كنت بحاجة لأي شيء آخر، أخبرني."],
    "بحث عن حجز": ["من فضلك أدخل اسم الشخص أو نوع الخدمة التي تريد البحث عنها."],
    
}

# ✅ نظام تتبع الحجز
booking_step = None
booking_data = {}

# ✅ وظيفة الرد التلقائي
def get_bot_response(user_input):
    for key in responses:
        if key in user_input.lower():
            return random.choice(responses[key])
    return "🤔 لم أفهم ذلك تمامًا. هل يمكنك توضيح طلبك؟"

# ✅ إنشاء واجهة المستخدم
root = tk.Tk()
root.title("🔹 إدارة الحجوزات")
root.geometry("600x500")
root.configure(bg="#1e1e1e")

style = ttk.Style()
style.configure("TButton", font=("Arial", 10), padding=4)
style.configure("TLabel", font=("Arial", 10), background="#1e1e1e", foreground="white")
style
# ✅ إضافة منطقة الشات
chat_frame = tk.Frame(root, bg="#1e1e1e")
chat_frame.pack(fill=tk.BOTH, expand=False, pady=2)

chat_box = tk.Text(chat_frame, bg="#292929", fg="white", font=("Arial", 19), height=8, state=tk.DISABLED, wrap="word")
chat_box.pack(fill=tk.BOTH, expand=False, padx=5, pady=2)

# ✅ إدخال المستخدم
user_input_var = tk.StringVar()
input_frame = tk.Frame(root, bg="#1e1e1e")
input_frame.pack(fill=tk.X, padx=5, pady=2)

input_entry = ttk.Entry(input_frame, textvariable=user_input_var, font=("Arial", 12), width=40)
input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

send_button = ttk.Button(input_frame, text="إرسال", command=lambda: send_message())
send_button.pack(side=tk.RIGHT, padx=2)

# ✅ وظيفة إدراج الرسالة في الدردشة
def insert_message(msg, sender="bot"):
    chat_box.config(state=tk.NORMAL)
    chat_box.insert(tk.END, f"{'🤖 ' if sender == 'bot' else '👤 '}{msg}\n", sender)
    chat_box.config(state=tk.DISABLED)
    chat_box.yview(tk.END)

# ✅ إرسال الرسالة والتفاعل مع البوت
def send_message():
    user_input = user_input_var.get().strip()
    if user_input:
        insert_message(user_input, "user")
        user_input_var.set("")
        process_user_input(user_input)

# ✅ البحث عن الحجوزات
def search_bookings(query):
    cursor.execute("SELECT user_name, service, date, time FROM bookings WHERE user_name LIKE ? OR service LIKE ?", (f"%{query}%", f"%{query}%"))
    results = cursor.fetchall()
    if results:
        response = "🔍 النتائج:\n" + "\n".join([f"👤 {r[0]} | 🔹 {r[1]} | 📅 {r[2]} | ⏰ {r[3]}" for r in results])
    else:
        response = "❌ لم يتم العثور على حجوزات متطابقة."
    return response

# ✅ تحليل إدخال المستخدم ومعالجة الحجز
def process_user_input(user_input):
    global booking_step, booking_data

    if booking_step is not None:  # إذا كان هناك حجز جاري
        if booking_step == 0:
            booking_data["user_name"] = user_input
            insert_message("🔹 ما هي الخدمة التي تريد حجزها؟ (مثال: فندق، طيران, عيادات)", "bot")
            booking_step = 1
        elif booking_step == 1:
            booking_data["service"] = user_input
            insert_message("📅 أدخل تاريخ الحجز (مثال: 2025-03-15)", "bot")
            booking_step = 2

        elif booking_step == 2:
            booking_data["date"] = user_input
            insert_message("⏰ أدخل وقت الحجز (مثال: 14:30)", "bot")
            booking_step = 3

        elif booking_step == 3:
            booking_data["time"] = user_input
            save_booking()
            insert_message("✅ تم تأكيد الحجز بنجاح! 🎉", "bot")
            booking_step = None  # إعادة تعيين المتغير

        return  # إيقاف المعالجة العادية للرسائل أثناء الحجز

    # ✅ بدء الحجز عند الطلب
    if "حجز" in user_input:
        insert_message("🎟 أدخل اسمك للبدء بالحجز.", "bot")
        booking_step = 0
        booking_data = {}  # إعادة تعيين البيانات
        return

    # ✅ البحث عن الحجوزات من النافذة المستقلة
    elif "بحث عن" in user_input or "حجزي" in user_input:
        response = search_bookings(user_input.split("عن")[-1].strip())
        insert_message(response, "bot")
        return

    # ✅ الردود الجاهزة
    response = get_bot_response(user_input)
    insert_message(response, "bot")

# ✅ حفظ الحجز في قاعدة البيانات
def save_booking():
    cursor.execute("INSERT INTO bookings (user_name, service, date, time) VALUES (?, ?, ?, ?)",
                   (booking_data["user_name"], booking_data["service"], booking_data["date"], booking_data["time"]))
    conn.commit()

# ✅ إنشاء نافذة البحث عن الحجوزات
def open_search_window():
    search_window = tk.Toplevel(root)
    search_window.title("🔍 البحث عن الحجوزات")
    search_window.geometry("400x300")
    
    ttk.Label(search_window, text="🔎 أدخل الاسم أو نوع الخدمة:", font=("Arial", 12)).pack(pady=10)
    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_window, textvariable=search_var, font=("Arial", 12))
    search_entry.pack(pady=5, padx=10, fill=tk.X)

    result_box = tk.Text(search_window, font=("Arial", 10), height=8, state=tk.DISABLED)
    result_box.pack(padx=10, pady=5, fill=tk.BOTH)

    def search():
        result_box.config(state=tk.NORMAL)
        result_box.delete("1.0", tk.END)
        result_box.insert(tk.END, search_bookings(search_var.get()))
        result_box.config(state=tk.DISABLED)

    ttk.Button(search_window, text="🔍 بحث", command=search).pack(pady=5)

# ✅ زر فتح نافذة البحث
search_button = ttk.Button(root, text="🔍 استعلام عن الحجز", command=open_search_window)
search_button.pack(pady=5)

insert_message("🤖 مرحبًا بك! كيف يمكنني مساعدتك اليوم؟", "bot")

root.mainloop()
