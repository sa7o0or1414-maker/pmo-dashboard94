import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

# ================= إعدادات الصفحة =================
st.set_page_config(page_title="منصة PMO", layout="wide")

# ================= الحالة =================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "role" not in st.session_state:
    st.session_state.role = "viewer"

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

# ================= CSS (سنترة كاملة + هوية) =================
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
    justify-content: center;
    align-items: center;
}
.stButton button {
    width: 230px;
    height: 56px;
    background: #153e46;
    color: white;
    border: none;
    border-radius: 16px;
    font-size: 16px;
    margin-bottom: 14px;
}
.block-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 90vh;
}
.card {
    background: white;
    padding: 22px;
    border-radius: 18px;
    box-shadow: 0 8px 25px rgba(0,0,0,.08);
    width: 100%;
}
h1, h2, h3, p, label, div {
    text-align: center !important;
}
input {
    text-align: center !important;
}
</style>
""", unsafe_allow_html=True)

# ================= قراءة Excel (نسخة قوية) =================
def load_data():
    if not EXCEL_PATH.exists():
        return None
    try:
        df = pd.read_excel(EXCEL_PATH, engine="openpyxl")
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error("تعذر قراءة ملف Excel")
        st.code(str(e))
        return None

# ================= Sidebar =================
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=120)
    else:
        st.markdown("<b style='color:white'>منصة PMO</b>", unsafe_allow_html=True)

    if st.button("الصفحة الرئيسية"):
        st.session_state.page = "home"

    if st.button("صفحة التحليل"):
        st.session_state.page = "analysis"

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
            st.success("تم تسجيل الدخول بنجاح")
            st.rerun()
        else:
            st.error("بيانات الدخول غير صحيحة")

# ================= رفع البيانات =================
if st.session_state.page == "upload":
    if st.session_state.role != "admin":
        st.warning("غير مصرح لك بالوصول")
    else:
        st.title("رفع البيانات")

        excel = st.file_uploader("رفع ملف Excel", type=["xlsx"])
        if excel:
            with open(EXCEL_PATH, "wb") as f:
                f.write(excel.getbuffer())
            st.success("تم رفع الملف بنجاح")
            st.session_state.page = "home"
            st.rerun()

        st.divider()

        logo = st.file_uploader("رفع شعار الجهة", type=["png","jpg","jpeg"])
        if logo:
            with open(LOGO_PATH, "wb") as f:
                f.write(logo.getbuffer())
            st.success("تم حفظ الشعار")
            st.rerun()

# ================= الصفحة الرئيسية =================
if st.session_state.page == "home":
    st.title("لوحة التحكم")

    df = load_data()
    if df is None:
        st.warning("لا توجد بيانات بعد. ارفع ملف Excel من صفحة رفع البيانات.")
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"<div class='card'>عدد المشاريع<br><h2>{len(df)}</h2></div>", unsafe_allow_html=True)

        with col2:
            total = pd.to_numeric(df.get("قيمة العقد", 0), errors="coerce").sum()
            st.markdown(f"<div class='card'>إجمالي قيمة العقود<br><h2>{total:,.0f}</h2></div>", unsafe_allow_html=True)

        with col3:
            avg = pd.to_numeric(df.get("نسبة الصرف", 0), errors="coerce").mean()
            st.markdown(f"<div class='card'>متوسط نسبة الصرف<br><h2>{avg:.1f}%</h2></div>", unsafe_allow_html=True)

# ================= صفحة التحليل =================
if st.session_state.page == "analysis":
    st.title("تحليل المشاريع")

    df = load_data()
    if df is None:
        st.warning("لا توجد بيانات لتحليلها")
    else:
        df["تاريخ الانتهاء"] = pd.to_datetime(df["تاريخ الانتهاء"], errors="coerce")

        # ---------- الفلاتر ----------
        st.subheader("الفلاتر")

        c1, c2, c3 = st.columns(3)
        with c1:
            cat = st.selectbox("التصنيف", ["الكل"] + sorted(df["التصنيف"].dropna().unique().tolist()))
        with c2:
            ent = st.selectbox("الجهة", ["الكل"] + sorted(df["الجهة"].dropna().unique().tolist()))
        with c3:
            mun = st.selectbox("البلدية", ["الكل"] + sorted(df["البلدية"].dropna().unique().tolist()))

        c4, c5 = st.columns(2)
        with c4:
            status = st.selectbox("حالة المشروع", ["الكل"] + sorted(df["حالة المشروع"].dropna().unique().tolist()))
        with c5:
            ctype = st.selectbox("نوع العقد", ["الكل"] + sorted(df["نوع العقد"].dropna().unique().tolist()))

        filtered = df.copy()
        if cat != "الكل": filtered = filtered[filtered["التصنيف"] == cat]
        if ent != "الكل": filtered = filtered[filtered["الجهة"] == ent]
        if mun != "الكل": filtered = filtered[filtered["البلدية"] == mun]
        if status != "الكل": filtered = filtered[filtered["حالة المشروع"] == status]
        if ctype != "الكل": filtered = filtered[filtered["نوع العقد"] == ctype]

        # ---------- التحليل ----------
        today = pd.Timestamp.today()
        overdue = filtered[
            (filtered["تاريخ الانتهاء"] < today) &
            (~filtered["حالة المشروع"].isin(["مكتمل", "منجز"]))
        ]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='card'>عدد المشاريع<br><h2>{len(filtered)}</h2></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='card'>المشاريع المتأخرة<br><h2>{len(overdue)}</h2></div>", unsafe_allow_html=True)

        st.divider()
        st.subheader("تفاصيل المشاريع")

        st.dataframe(
            filtered[
                [
                    "اسم المشروع",
                    "المقاول",
                    "الجهة",
                    "البلدية",
                    "تاريخ الانتهاء",
                    "حالة المشروع",
                    "قيمة العقد",
                    "نسبة الصرف"
                ]
            ],
            use_container_width=True
        )
