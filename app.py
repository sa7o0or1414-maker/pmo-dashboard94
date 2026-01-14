import streamlit as st
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# ================= إعدادات الصفحة =================
st.set_page_config(page_title="منصة PMO", layout="wide")

# ================= الحالة =================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "role" not in st.session_state:
    st.session_state.role = "viewer"
if "show_overdue" not in st.session_state:
    st.session_state.show_overdue = False
if "show_risk" not in st.session_state:
    st.session_state.show_risk = False

# ================= بيانات المسؤول =================
ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# ================= المسارات =================
BASE_DIR = Path(".")
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

EXCEL_PATH = DATA_DIR / "data.xlsx"
LOGO_PATH = ASSETS_DIR / "logo.png"

# ================= CSS (Power BI Style + سنترة) =================
st.markdown("""
<style>
html, body, [class*="css"] {
    direction: rtl;
    text-align: center !important;
    font-family: 'Segoe UI', sans-serif;
}
section[data-testid="stSidebar"] {
    background-color: #0f2d33;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.stButton button {
    width: 230px;
    height: 56px;
    background: #153e46;
    color: white;
    border-radius: 16px;
    border: none;
    font-size: 16px;
    margin-bottom: 14px;
}
.block-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    min-height: 90vh;
}
.card {
    background: white;
    padding: 22px;
    border-radius: 20px;
    box-shadow: 0 8px 25px rgba(0,0,0,.08);
    width: 100%;
}
h1, h2, h3, p, label {
    text-align: center !important;
}
</style>
""", unsafe_allow_html=True)

# ================= قراءة Excel =================
def load_data():
    if not EXCEL_PATH.exists():
        return None
    df = pd.read_excel(EXCEL_PATH, engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]
    df["تاريخ الانتهاء"] = pd.to_datetime(df["تاريخ الانتهاء"], errors="coerce")
    return df

# ================= Sidebar =================
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=120)
    else:
        st.markdown("<b style='color:white'>PMO</b>", unsafe_allow_html=True)

    if st.button("الصفحة الرئيسية"):
        st.session_state.page = "home"

    if st.session_state.role == "admin":
        if st.button("رفع البيانات"):
            st.session_state.page = "upload"

    if st.session_state.role != "admin":
        if st.button("تسجيل دخول"):
            st.session_state.page = "login"
    else:
        if st.button("تسجيل خروج"):
            st.session_state.role = "viewer"
            st.session_state.page = "home"
            st.rerun()

# ================= تسجيل الدخول =================
if st.session_state.page == "login":
    st.title("تسجيل دخول المسؤول")
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if u == ADMIN_USER and p == ADMIN_PASS:
            st.session_state.role = "admin"
            st.session_state.page = "home"
            st.rerun()
        else:
            st.error("بيانات غير صحيحة")

# ================= رفع البيانات =================
if st.session_state.page == "upload":
    st.title("رفع البيانات")
    excel = st.file_uploader("رفع ملف Excel", type=["xlsx"])
    if excel:
        with open(EXCEL_PATH, "wb") as f:
            f.write(excel.getbuffer())
        st.success("تم رفع الملف")
        st.session_state.page = "home"
        st.rerun()

# ================= الصفحة الرئيسية (Dashboard كامل) =================
if st.session_state.page == "home":
    st.title("لوحة التحكم")

    df = load_data()
    if df is None:
        st.warning("ارفع ملف Excel لعرض لوحة التحكم")
    else:
        # ---------- الفلاتر ----------
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            cat = st.selectbox("التصنيف", ["الكل"] + sorted(df["التصنيف"].dropna().unique()))
        with c2:
            ent = st.selectbox("الجهة", ["الكل"] + sorted(df["الجهة"].dropna().unique()))
        with c3:
            mun = st.selectbox("البلدية", ["الكل"] + sorted(df["البلدية"].dropna().unique()))
        with c4:
            status = st.selectbox("حالة المشروع", ["الكل"] + sorted(df["حالة المشروع"].dropna().unique()))
        with c5:
            ctype = st.selectbox("نوع العقد", ["الكل"] + sorted(df["نوع العقد"].dropna().unique()))

        filtered = df.copy()
        if cat != "الكل": filtered = filtered[filtered["التصنيف"] == cat]
        if ent != "الكل": filtered = filtered[filtered["الجهة"] == ent]
        if mun != "الكل": filtered = filtered[filtered["البلدية"] == mun]
        if status != "الكل": filtered = filtered[filtered["حالة المشروع"] == status]
        if ctype != "الكل": filtered = filtered[filtered["نوع العقد"] == ctype]

        # ---------- KPI ----------
        k1, k2, k3 = st.columns(3)
        with k1:
            st.markdown(f"<div class='card'>عدد المشاريع<br><h2>{len(filtered)}</h2></div>", unsafe_allow_html=True)
        with k2:
            total = pd.to_numeric(filtered["قيمة العقد"], errors="coerce").sum()
            st.markdown(f"<div class='card'>إجمالي قيمة العقود<br><h2>{total:,.0f}</h2></div>", unsafe_allow_html=True)
        with k3:
            avg = pd.to_numeric(filtered["نسبة الصرف"], errors="coerce").mean()
            st.markdown(f"<div class='card'>متوسط نسبة الصرف<br><h2>{avg:.1f}%</h2></div>", unsafe_allow_html=True)

        st.divider()

        # ---------- الرسومات ----------
        colA, colB = st.columns(2)

        with colA:
            st.subheader("عدد المشاريع حسب الحالة")
            fig, ax = plt.subplots()
            filtered["حالة المشروع"].value_counts().plot(kind="bar", ax=ax)
            st.pyplot(fig)

        with colB:
            st.subheader("قيمة العقود حسب الجهة")
            fig, ax = plt.subplots()
            filtered.groupby("الجهة")["قيمة العقد"].sum().plot(kind="bar", ax=ax)
            st.pyplot(fig)

        st.divider()

        # ---------- المشاريع المتأخرة ----------
        today = pd.Timestamp.today()
        overdue = filtered[
            (filtered["تاريخ الانتهاء"] < today) &
            (~filtered["حالة المشروع"].isin(["مكتمل", "منجز"]))
        ]

        if st.button("عرض المشاريع المتأخرة"):
            st.dataframe(
                overdue[
                    ["اسم المشروع", "الجهة", "البلدية", "تاريخ الانتهاء", "حالة المشروع"]
                ],
                use_container_width=True
            )
