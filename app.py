import streamlit as st
import pandas as pd
from pathlib import Path

# ---------------- إعدادات الصفحة ----------------
st.set_page_config(page_title="منصة PMO", layout="wide")

# ---------------- الحالة ----------------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None

# ---------------- المستخدمين ----------------
USERS = {
    "admin": {"password": "1234", "role": "admin"},
    "viewer": {"password": "1234", "role": "viewer"},
}

# ---------------- المسارات ----------------
DATA_DIR = Path("data")
ASSETS_DIR = Path("assets")
DATA_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

EXCEL_PATH = DATA_DIR / "data.xlsx"
LOGO_PATH = ASSETS_DIR / "logo.png"

# ---------------- CSS ----------------
st.markdown("""
<style>
:root{
--main:#153e46;--light:#1f5661;--dark:#0f2d33;
}
html,body,[class*="css"]{
direction:rtl;text-align:center;font-family:'Segoe UI';
}
section[data-testid="stSidebar"]{
background:var(--dark);
display:flex;justify-content:center;align-items:center;
}
.stButton button{
width:220px;height:55px;border-radius:14px;
background:var(--main);color:white;border:none;
font-size:16px;margin-bottom:14px;
}
.stButton button:hover{background:var(--light);}
.block-container{
display:flex;flex-direction:column;
justify-content:center;align-items:center;
min-height:90vh;
}
.kpi{
background:white;padding:25px;border-radius:18px;
width:100%;box-shadow:0 6px 20px rgba(0,0,0,.08);
}
</style>
""", unsafe_allow_html=True)

# ---------------- Sidebar ----------------
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=120)
    else:
        st.markdown("منصة PMO")

    if st.button("الصفحة الرئيسية"):
        st.session_state.page = "home"

    if st.button("رفع البيانات"):
        st.session_state.page = "upload"

    if not st.session_state.logged_in:
        if st.button("تسجيل الدخول"):
            st.session_state.page = "login"
    else:
        if st.button("تسجيل خروج"):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.session_state.page = "home"

# ---------------- تسجيل الدخول ----------------
if st.session_state.page == "login":
    st.title("تسجيل الدخول")
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")

    if st.button("دخول"):
        if u in USERS and USERS[u]["password"] == p:
            st.session_state.logged_in = True
            st.session_state.role = USERS[u]["role"]
            st.success("تم تسجيل الدخول")
            st.session_state.page = "home"
        else:
            st.error("بيانات غير صحيحة")

# ---------------- تحميل البيانات ----------------
def load_data():
    if EXCEL_PATH.exists():
        return pd.read_excel(EXCEL_PATH, sheet_name="Data")
    return None

df = load_data()

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

# ---------------- رفع البيانات ----------------
if st.session_state.page == "upload":
    if not st.session_state.logged_in or st.session_state.role != "admin":
        st.warning("هذه الصفحة متاحة للمسؤول فقط")
    else:
        st.title("رفع البيانات")

        excel = st.file_uploader("رفع ملف Excel", type=["xlsx"])
        if excel:
            with open(EXCEL_PATH, "wb") as f:
                f.write(excel.getbuffer())
            st.success("تم حفظ البيانات")

        st.divider()

        logo = st.file_uploader("رفع شعار الجهة", type=["png","jpg","jpeg"])
        if logo:
            with open(LOGO_PATH, "wb") as f:
                f.write(logo.getbuffer())
            st.success("تم حفظ الشعار")
