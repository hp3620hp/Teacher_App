import streamlit as st
import sqlite3
import jdatetime

# --- تنظیمات ظاهری ---
st.set_page_config(page_title="دفتر کلاس معلم", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: Tahoma, sans-serif !important; }
    .stApp { background-color: #f4f7f6; }
    .stButton>button {
        background-color: #4CAF50; color: white; border-radius: 8px;
        padding: 8px 20px; font-weight: bold; border: none; width: 100%;
    }
    .stButton>button:hover { background-color: #45a049; }
    /* استایل منوی کناری */
    [data-testid="stSidebar"] { background-color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

# --- اتصال به دیتابیس ---
conn = sqlite3.connect('school.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, class_name TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS attendance (id INTEGER PRIMARY KEY AUTOINCREMENT, student_name TEXT, status TEXT, day TEXT, time TEXT, date TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS grades (id INTEGER PRIMARY KEY AUTOINCREMENT, student_name TEXT, subject TEXT, score INTEGER, date TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS discipline (id INTEGER PRIMARY KEY AUTOINCREMENT, student_name TEXT, type TEXT, note TEXT, date TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS schedule (id INTEGER PRIMARY KEY AUTOINCREMENT, day TEXT, time TEXT, subject TEXT)''')
conn.commit()

today_date = jdatetime.date.today().strftime("%Y/%m/%d")

# --- منوی کناری (Sidebar) ---
with st.sidebar:
    st.title("🎓 منوی اصلی")
    st.write("لطفاً یک بخش را انتخاب کنید:")
    menu = st.radio(
        "انتخاب بخش:",
        ["ثبت دانش‌آموز", "حضور و غیاب", "ثبت نمرات", "انضباط", "برنامه هفتگی", "دفتر کلاس"]
    )
    st.divider()
    st.caption("ساخته شده برای معلمان عزیز ❤️")

# --- عنوان اصلی ---
st.title("سامانه جامع مدیریت کلاس")
st.write("مدیریت هوشمند دانش‌آموزان، حضور و غیاب، نمرات و برنامه هفتگی")

# گرفتن لیست دانش‌آموزان
c.execute("SELECT name FROM students")
all_students = [row[0] for row in c.fetchall()]

# ==================== بخش‌ها ====================

if menu == "ثبت دانش‌آموز":
    st.header("ثبت دانش‌آموز جدید")
    col1, col2 = st.columns(2)
    with col1:
        student_name = st.text_input("نام و نام خانوادگی:", key="input_student_name")
    with col2:
        class_name = st.selectbox("انتخاب کلاس:", ["هفتم الف", "هفتم ب", "هشتم الف", "نهم الف"], key="select_class")
    
    if st.button("ذخیره دانش‌آموز", key="btn_save_student"):
        if student_name:
            c.execute("INSERT INTO students (name, class_name) VALUES (?, ?)", (student_name, class_name))
            conn.commit()
            st.success(f"دانش‌آموز '{student_name}' اضافه شد.")
            st.rerun()
        else:
            st.warning("لطفاً نام دانش‌آموز را وارد کنید.")
            
    st.divider()
    st.subheader("لیست دانش‌آموزان")
    c.execute("SELECT name, class_name FROM students")
    for s in c.fetchall():
        st.info(f"{s[0]} - {s[1]}")

elif menu == "حضور و غیاب":
    st.header("ثبت حضور و غیاب")
    if not all_students:
        st.warning("ابتدا از بخش «ثبت دانش‌آموز» دانش‌آموز اضافه کنید.")
    else:
        col_day, col_time = st.columns(2)
        with col_day:
            day = st.selectbox("روز هفته:", ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"], key="att_day")
        with col_time:
            time = st.selectbox("ساعت کلاس:", ["08:00 - 09:00", "09:00 - 10:00", "10:00 - 11:00", "11:00 - 12:00", "13:00 - 14:00"], key="att_time")
            
        st.write(f"تاریخ ثبت: {today_date}")
        st.divider()
        
        for student in all_students:
            col1, col2 = st.columns([3, 1])
            with col1:
                status = st.radio(f"وضعیت {student}:", ["حاضر", "غایب", "لان"], key=f"att_radio_{student}", horizontal=True)
            with col2:
                if st.button(f"ثبت", key=f"btn_att_{student}"):
                    c.execute("SELECT * FROM attendance WHERE student_name=? AND date=? AND time=?", (student, today_date, time))
                    if c.fetchone():
                        c.execute("UPDATE attendance SET status=? WHERE student_name=? AND date=? AND time=?", (status, student, today_date, time))
                    else:
                        c.execute("INSERT INTO attendance (student_name, status, day, time, date) VALUES (?, ?, ?, ?, ?)", (student, status, day, time, today_date))
                    conn.commit()
                    st.success(f"ثبت شد: {student} -> {status}")

elif menu == "ثبت نمرات":
    st.header("ثبت نمرات")
    if not all_students:
        st.warning("ابتدا دانش‌آموز اضافه کنید.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            grade_student = st.selectbox("دانش‌آموز:", all_students, key="grade_student_select")
        with col2:
            subject = st.text_input("نام درس:", key="input_grade_subject")
        with col3:
            score = st.number_input("نمره (0 تا 20):", min_value=0, max_value=20, value=20, key="input_grade_score")
            
        if st.button("ثبت نمره", key="btn_save_grade"):
            if subject:
                c.execute("INSERT INTO grades (student_name, subject, score, date) VALUES (?, ?, ?, ?)", (grade_student, subject, score, today_date))
                conn.commit()
                st.success(f"نمره {score} برای {grade_student} ثبت شد.")
            else:
                st.warning("نام درس را وارد کنید.")

elif menu == "انضباط":
    st.header("ثبت موارد انضباطی")
    if not all_students:
        st.warning("ابتدا دانش‌آموز اضافه کنید.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            disc_student = st.selectbox("دانش‌آموز:", all_students, key="disc_student_select")
            disc_type = st.selectbox("نوع مورد:", ["تشویق", "تذکر", "غیبت غیرموجه"], key="disc_type_select")
        with col2:
            disc_note = st.text_area("توضیحات:", key="input_disc_note")
            
        if st.button("ثبت مورد انضباطی", key="btn_save_disc"):
            c.execute("INSERT INTO discipline (student_name, type, note, date) VALUES (?, ?, ?, ?)", (disc_student, disc_type, disc_note, today_date))
            conn.commit()
            st.success(f"مورد ثبت شد: {disc_type} برای {disc_student}")

elif menu == "برنامه هفتگی":
    st.header("برنامه هفتگی کلاس")
    with st.expander("افزودن برنامه جدید"):
        col1, col2, col3 = st.columns(3)
        with col1:
            sch_day = st.selectbox("روز:", ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه"], key="sch_day_select")
        with col2:
            sch_time = st.selectbox("ساعت:", ["08:00 - 09:00", "09:00 - 10:00", "10:00 - 11:00", "11:00 - 12:00"], key="sch_time_select")
        with col3:
            sch_subject = st.text_input("نام درس:", key="sch_subject_input")
            
        if st.button("افزودن به برنامه", key="btn_add_sch"):
            if sch_subject:
                c.execute("INSERT INTO schedule (day, time, subject) VALUES (?, ?, ?)", (sch_day, sch_time, sch_subject))
                conn.commit()
                st.success("برنامه جدید اضافه شد.")
                st.rerun()
            else:
                st.warning("نام درس را وارد کنید.")
                
    st.divider()
    st.subheader("مشاهده برنامه")
    c.execute("SELECT day, time, subject FROM schedule ORDER BY day, time")
    schedules = c.fetchall()
    if schedules:
        for s in schedules:
            st.write(f"**{s[0]}** | {s[1]} | {s[2]}")
    else:
        st.info("برنامه‌ای ثبت نشده است.")

elif menu == "دفتر کلاس":
    st.header("دفتر کلاس (سوابق)")
    report_type = st.selectbox("نمایش سوابق:", ["حضور و غیاب", "نمرات", "انضباط"], key="report_type_select")
    
    if report_type == "حضور و غیاب":
        c.execute("SELECT student_name, status, day, time, date FROM attendance ORDER BY date DESC")
        for r in c.fetchall():
            st.write(f"**{r[0]}** | وضعیت: {r[1]} | روز: {r[2]} | ساعت: {r[3]} | تاریخ: {r[4]}")
    elif report_type == "نمرات":
        c.execute("SELECT student_name, subject, score, date FROM grades ORDER BY date DESC")
        for r in c.fetchall():
            st.write(f"**{r[0]}** | درس: {r[1]} | نمره: {r[2]} | تاریخ: {r[3]}")
    elif report_type == "انضباط":
        c.execute("SELECT student_name, type, note, date FROM discipline ORDER BY date DESC")
        for r in c.fetchall():
            st.write(f"**{r[0]}** | نوع: {r[1]} | توضیحات: {r[2]} | تاریخ: {r[3]}")