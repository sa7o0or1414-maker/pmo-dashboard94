import streamlit as st
import pandas as pd
from pathlib import Path

# ---------------- إعدادات الصفحة ----------------
st.set_page_config(page_title="منصة PMO", layout="wide")

# ---------------- الحالة ----------------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "role" not in st.session_state:
    st.session_state.role = "viewer"  # مشاهد افتراضي

# ---------------- بيانات المسؤول ----------------
ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# ---------------- المسارات ----------------
DATA_DIR = Path("data")
ASSETS_DIR = Path("assets")
DATA_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

EXCEL_PATH = DATA_DIR / "data.xlsx"
LOGO_PATH = ASSETS_DIR / "logo.png"

# ---------------- CSS (سنترة + تنسيق جميل) ----------------
st.markdown("""
<style>
:root{
--main:#153e46;--light:#1f5661;--dark:#0f2d33;
}

/* سنترة شاملة */
html, body, [class*="css"] {
    direction: rtl;
    text-align: center !important;
    font-family: 'Segoe UI', sans-serif;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: var(--dark);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

/* أزرار */
.stButton button {
    width: 230px;
    height: 56px;
    background: var(--main);
    color: white;
    border: none;
    border-radius: 16px;
    font-size: 16px;
    margin-bottom: 14px;
    text-align: center;
    transition: 0.3s;
}
.stButton button:hover {
    background: var(--light);
}

/* محتوى الصفحة */
.block-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 90vh;
}

/* العناوين */
h1, h2, h3 {
    color: var(--main);
    text-align: center !important;
}

/* النصوص */
p, label, span, div {
    text-align: center !important;
}

/* حقول الإدخال */
input {
    text-align: center !important;
}

/* KPI Cards */
.kpi {
    background: white;
    padding: 28px;
    border-radius: 20px;
    width: 100%;
    box-shadow: 0 8px 25px rgba(0,0,0,0.08);
}

/* اللوقو */
img {
    display: block;
    margin: 0 auto 14px auto;
}
</style>
""", unsafe_allow_html=True)

# ---------------- تحميل البيانات ----------------
def load_data():
    if EXCEL_PATH.exists():
        return pd.read_excel(EXCEL_PATH, sheet_name="Data")
    return None

df = load_data()

# ---------------- Sidebar ----------------
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=120)
    else:
        st.markdown("<b style='color:white'>منصة PMO</b>", unsafe_allow_html=True)

    if st.button("الصفحة الرئيسية"):
        st.session_state.page = "home"

    if st.session_state.role == "admin":
        if st.button("رفع البيانات"):
            st.session_state.page = "upload"

    if st.session_state.role != "admin":
        if st.button("تسجيل دخول المسؤول"):
            st.session_state.page = "login"
    else:
        if st.button("تسجيل خروج"):
            st.session_state.role = "viewer"
            st.session_state.page = "home"

# ---------------- تسجيل الدخول ----------------
if st.session_state.page == "login":
    st.title("تسجيل دخول المسؤول")

    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")

    if st.button("دخول"):
        if u == ADMIN_USER and p == ADMIN_PASS:
            st.session_state.role = "admin"
            st.success("تم تسجيل الدخول بنجاح")
            st.session_state.page = "home"
        else:
            st.error("بيانات الدخول غير صحيحة")

# ---------------- الصفحة الرئيسية (Dashboard) ----------------
if st.session_state.page == "home":
    st.title("لوحة التحكم")

    if df is None:
        st.warning("لا توجد بيانات بعد")
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                f"<div class='kpi'>عدد المشاريع<br><h2>{len(df)}</h2></div>",
                unsafe_allow_html=True)

        with col2:
            st.markdown(
                f"<div class='kpi'>إجمالي الميزانية<br><h2>{df['budget'].sum():,.0f}</h2></div>",
                unsafe_allow_html=True)

        with col3:
            st.markdown(
                f"<div class='kpi'>متوسط الإنجاز<br><h2>{df['progress'].mean():.1f}%</h2></div>",
                unsafe_allow_html=True)

        st.divider()
        st.subheader("تفاصيل المشاريع")
        st.dataframe(df, use_container_width=True)

# ---------------- رفع البيانات (Admin فقط) ----------------
if st.session_state.page == "upload":
    if st.session_state.role != "admin":
        st.warning("غير مصرح لك بالوصول")
    else:
        st.title("رفع البيانات")

        excel = st.file_uploader("رفع ملف Excel", type=["xlsx"])
        if excel:
            with open(EXCEL_PATH, "wb") as f:
                f.write(excel.getbuffer())
            st.success("تم حفظ ملف البيانات")

        st.divider()

        logo = st.file_uploader("رفع شعار الجهة", type=["png","jpg","jpeg"])
        if logo:
            with open(LOGO_PATH, "wb") as f:
                f.write(logo.getbuffer())
            st.success("تم حفظ الشعار")
