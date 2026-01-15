import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import timedelta
import altair as alt

# ================= إعدادات الصفحة =================
st.set_page_config(
    page_title="لوحة المعلومات | PMO",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= Session State =================
defaults = {
    "role": "viewer",
    "page": "home",
    "show_overdue": False,
    "show_risk": False,
    "top_nav": "الافتراضي"
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

DATA_DIR = Path("data")
ASSETS_DIR = Path("assets")
DATA_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

LOGO_PATH = ASSETS_DIR / "logo.png"

DATA_FILES = {
    "مشاريع الباب الثالث": "bab3.xlsx",
    "مشاريع الباب الرابع": "bab4.xlsx",
    "مشاريع بهجة": "bahja.xlsx",
    "تطبيق دليل PMD": "pmd.xlsx",
    "المشاريع المنجزة": "done.xlsx",
    "مشاريع المحفظة": "portfolio.xlsx",
    "الدراسات وقوائم التحقق": "studies.xlsx",
    "دورة المشتريات": "procurement.xlsx",
    "مواقع المشاريع": "sites.xlsx",
    "مشاريع الإسكان": "housing.xlsx",
    "الافتراضي": "data.xlsx"
}

# ================= CSS =================
st.markdown("""
<style>
html, body {direction: rtl; font-family: 'Segoe UI';}

section[data-testid="stSidebar"] {
    background: #1e5055;
}
section[data-testid="stSidebar"] * {
    color: white !important;
}

.topbar-btn button {
    background:#1e5055 !important;
    color:white !important;
    border:1px solid rgba(255,255,255,.3) !important;
    min-width:160px;
    height:44px;
    border-radius:14px;
}

.topbar-btn button:hover {
    background:#24666c !important;
}

.card {
    background:#fff;
    padding:18px;
    border-radius:18px;
    box-shadow:0 10px 28px rgba(0,0,0,.08);
    text-align:center;
    min-height:140px;
}

.card h2 {
    font-size:22px;
    white-space:nowrap;
}

.card.blue {border-top:4px solid #2c7be5;}
.card.green {border-top:4px solid #00a389;}
.card.orange {border-top:4px solid #f4a261;}
.card.gray {border-top:4px solid #6c757d;}
</style>
""", unsafe_allow_html=True)

# ================= أدوات =================
def load_data():
    file = DATA_FILES.get(st.session_state.top_nav, "data.xlsx")
    path = DATA_DIR / file
    if not path.exists():
        return None

    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()

    df.rename(columns={
        "إسم المشـــروع": "اسم المشروع",
        "قيمة المستخلصات المعتمده": "قيمة المستخلصات",
        "نسبة الانجاز": "نسبة الإنجاز"
    }, inplace=True)

    for c in df.columns:
        if "تاريخ" in c:
            df[c] = pd.to_datetime(df[c], errors="coerce")

    return df

def build_status_df(df):
    s = df["حالة المشروع"].fillna("غير محدد")
    out = s.value_counts().reset_index()
    out.columns = ["الحالة","عدد"]
    return out

# ================= Sidebar =================
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(LOGO_PATH, width=120)

    if st.button("الصفحة الرئيسية"):
        st.session_state.page = "home"

    if st.session_state.role == "viewer":
        if st.button("تسجيل الدخول"):
            st.session_state.page = "login"

    if st.session_state.role == "admin":
        if st.button("رفع البيانات"):
            st.session_state.page = "upload"
        if st.button("تسجيل خروج"):
            st.session_state.role = "viewer"
            st.session_state.page = "home"
            st.rerun()

# ================= Login =================
if st.session_state.page == "login":
    st.title("تسجيل الدخول")
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if u == ADMIN_USER and p == ADMIN_PASS:
            st.session_state.role = "admin"
            st.session_state.page = "home"
            st.rerun()
        else:
            st.error("بيانات غير صحيحة")
    st.stop()

# ================= Upload =================
if st.session_state.page == "upload":
    st.title("رفع الملفات")
    for name, file in DATA_FILES.items():
        if name == "الافتراضي": continue
        with st.expander(name):
            up = st.file_uploader(name, type=["xlsx"], key=file)
            if up:
                (DATA_DIR / file).write_bytes(up.getbuffer())
                st.success("تم الرفع")
    st.stop()

# ================= Home =================
st.title("لوحة المعلومات")

# ===== Top Buttons =====
items = list(DATA_FILES.keys())
items.remove("الافتراضي")

for row in [items[:5], items[5:]]:
    cols = st.columns(5)
    for c, name in zip(cols, row):
        with c:
            if st.button(name):
                st.session_state.top_nav = name
                st.rerun()

st.caption(f"📊 التحليل الحالي: {st.session_state.top_nav}")

df = load_data()
if df is None:
    st.warning("لا يوجد ملف")
    st.stop()

# ================= تحليل مشاريع بهجة =================
if st.session_state.top_nav == "مشاريع بهجة":

    st.subheader("تحليل مشاريع بهجة")

    filtered = df.copy()

    f1,f2,f3,f4 = st.columns(4)

    with f1:
        mun = st.selectbox("البلدية", ["الكل"] + sorted(filtered["البلدية"].dropna().unique()))
        if mun != "الكل":
            filtered = filtered[filtered["البلدية"] == mun]

    with f2:
        proj = st.selectbox("اسم المشروع", ["الكل"] + sorted(filtered["اسم المشروع"].dropna().unique()))
        if proj != "الكل":
            filtered = filtered[filtered["اسم المشروع"] == proj]

    with f3:
        typ = st.selectbox("نوع المشروع", ["الكل"] + sorted(filtered["نوع المشروع"].dropna().unique()))
        if typ != "الكل":
            filtered = filtered[filtered["نوع المشروع"] == typ]

    with f4:
        appr = st.selectbox("حالة الاعتماد", ["الكل"] + sorted(filtered["حالة الاعتماد"].dropna().unique()))
        if appr != "الكل":
            filtered = filtered[filtered["حالة الاعتماد"] == appr]

    c1,c2,c3 = st.columns(3)
    c1.markdown(f"<div class='card blue'><h2>{len(filtered)}</h2>عدد المشاريع</div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='card green'><h2>{filtered['التكلفة'].sum():,.0f}</h2>إجمالي التكلفة</div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='card orange'><h2>{filtered['نسبة الإنجاز'].mean():.1f}%</h2>نسبة الإنجاز</div>", unsafe_allow_html=True)

    st.subheader("مواقع المشاريع")
    if {"خط العرض","خط الطول"}.issubset(filtered.columns):
        st.map(filtered.rename(columns={"خط العرض":"lat","خط الطول":"lon"})[["lat","lon"]].dropna())

    ch1,ch2 = st.columns(2)

    with ch1:
        st.subheader("حالة المشروع")
        st.bar_chart(filtered["حالة المشروع"].value_counts())

    with ch2:
        st.subheader("المستهدف مقابل الإنجاز")
        if {"اسم المشروع","نسبة الإنجاز","المستهدف"}.issubset(filtered.columns):
            st.bar_chart(
                filtered.set_index("اسم المشروع")[["نسبة الإنجاز","المستهدف"]]
            )
        else:
            st.info("أعمدة المستهدف غير مكتملة")

    st.dataframe(filtered, use_container_width=True)
    st.stop()

# ================= الداشبورد العام (باقي الأقسام) =================
st.info("اختر قسم من الأعلى لعرض التحليل")
