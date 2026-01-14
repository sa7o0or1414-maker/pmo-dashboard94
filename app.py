import streamlit as st
import pandas as pd
from pathlib import Path

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
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
EXCEL_PATH = DATA_DIR / "data.xlsx"

# ================= CSS (سنترة + هوية) =================
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
.card {
    background: white;
    padding: 22px;
    border-radius: 20px;
    box-shadow: 0 8px 25px rgba(0,0,0,.08);
}
</style>
""", unsafe_allow_html=True)

# ================= ربط ذكي للأعمدة =================
COLUMN_MAP = {
    "اسم المشروع": "إسم المشـــروع",
    "تاريخ الانتهاء": "تاريخ الانتهاء من المشروع",
    "نسبة الإنجاز": "نسبة الإنجاز",
    "قيمة العقد": "قيمة العقد",
    "قيمة المستخلصات": "قيمة المستخلصات المعتمده",
    "نسبة الصرف": "نسبة الصرف",
    "حالة المشروع": "حالة المشروع",
    "الجهة": "الجهة",
    "البلدية": "البلدية",
    "نوع العقد": "نوع العقد"
}

# ================= قراءة Excel =================
def load_data():
    if not EXCEL_PATH.exists():
        return None
    df = pd.read_excel(EXCEL_PATH, engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]

    # إعادة تسمية الأعمدة المهمة
    for std, real in COLUMN_MAP.items():
        if real in df.columns:
            df.rename(columns={real: std}, inplace=True)

    # تحويل التواريخ
    if "تاريخ الانتهاء" in df.columns:
        df["تاريخ الانتهاء"] = pd.to_datetime(df["تاريخ الانتهاء"], errors="coerce")

    return df

# ================= Sidebar =================
with st.sidebar:
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
        st.success("تم رفع الملف بنجاح")
        st.session_state.page = "home"
        st.rerun()

# ================= الصفحة الرئيسية (تحليل Power BI) =================
if st.session_state.page == "home":
    st.title("لوحة التحكم")

    df = load_data()
    if df is None:
        st.warning("ارفع ملف Excel لعرض لوحة التحكم")
    else:
        # ---------- الفلاتر ----------
        f1, f2, f3 = st.columns(3)
        with f1:
            ent = st.selectbox("الجهة", ["الكل"] + sorted(df["الجهة"].dropna().unique()))
        with f2:
            mun = st.selectbox("البلدية", ["الكل"] + sorted(df["البلدية"].dropna().unique()))
        with f3:
            status = st.selectbox("حالة المشروع", ["الكل"] + sorted(df["حالة المشروع"].dropna().unique()))

        filtered = df.copy()
        if ent != "الكل": filtered = filtered[filtered["الجهة"] == ent]
        if mun != "الكل": filtered = filtered[filtered["البلدية"] == mun]
        if status != "الكل": filtered = filtered[filtered["حالة المشروع"] == status]

        # ---------- KPI ----------
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"<div class='card'>عدد المشاريع<br><h2>{len(filtered)}</h2></div>", unsafe_allow_html=True)
        with c2:
            total = pd.to_numeric(filtered["قيمة العقد"], errors="coerce").sum()
            st.markdown(f"<div class='card'>إجمالي قيمة العقود<br><h2>{total:,.0f}</h2></div>", unsafe_allow_html=True)
        with c3:
            avg = pd.to_numeric(filtered["نسبة الإنجاز"], errors="coerce").mean()
            st.markdown(f"<div class='card'>متوسط نسبة الإنجاز<br><h2>{avg:.1f}%</h2></div>", unsafe_allow_html=True)

        st.divider()

        # ---------- المشاريع المتأخرة ----------
        today = pd.Timestamp.today()
        overdue = filtered[
            (filtered["تاريخ الانتهاء"] < today) &
            (~filtered["حالة المشروع"].isin(["مكتمل", "منجز"]))
        ]

        st.subheader("المشاريع المتأخرة")
        st.dataframe(
            overdue[["اسم المشروع", "الجهة", "البلدية", "تاريخ الانتهاء", "حالة المشروع"]],
            use_container_width=True
        )
