import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import timedelta
import base64
import altair as alt

# ================= إعدادات الصفحة =================
st.set_page_config(
    page_title="لوحة المعلومات  | PMO",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= Session State =================
defaults = {
    "role": "viewer",
    "page": "home",
    "logo_align": "center",
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

# ================= ربط الأزرار بالملفات =================
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
html, body, [class*="css"] {
    direction: rtl;
    font-family: 'Segoe UI', sans-serif;
}
h1 { text-align:center; }

/* ===== Sidebar ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f2d33, #153e46);
    padding-top: 24px;
}
section[data-testid="stSidebar"] * {
    color: white !important;
    text-align: center;
}
section[data-testid="stSidebar"] .stButton {
    display: flex;
    justify-content: center;
}
section[data-testid="stSidebar"] .stButton > button {
    padding: 10px 26px;
    margin: 10px 0;
    background: rgba(255,255,255,0.18);
    border-radius: 20px;
    border: none;
    font-size: 14px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.25);
}

/* ===== Cards ===== */
.card {
    background:#fff;
    padding:18px;
    border-radius:18px;
    box-shadow:0 10px 28px rgba(0,0,0,0.08);
    text-align:center;
}
.card.blue { border-top:4px solid #2c7be5; }
.card.green { border-top:4px solid #00a389; }
.card.orange { border-top:4px solid #f4a261; }
.card.gray { border-top:4px solid #6c757d; }
</style>
""", unsafe_allow_html=True)

# ================= أدوات =================
def load_data():
    filename = DATA_FILES.get(st.session_state.top_nav, "data.xlsx")
    path = DATA_DIR / filename
    if not path.exists():
        return None

    df = pd.read_excel(path)
    df.columns = [str(c).strip() for c in df.columns]

    df.rename(columns={
        "إسم المشـــروع": "اسم المشروع",
        "تاريخ الانتهاء من المشروع": "تاريخ الانتهاء",
        "قيمة المستخلصات المعتمده": "قيمة المستخلصات",
    }, inplace=True)

    for c in ["قيمة العقد","قيمة المستخلصات","نسبة الإنجاز"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    if "تاريخ الانتهاء" in df.columns:
        df["تاريخ الانتهاء"] = pd.to_datetime(df["تاريخ الانتهاء"], errors="coerce")

    return df

def build_status_df(df):
    s = df["حالة المشروع"].fillna("غير محدد").astype(str)
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
    st.title("رفع البيانات حسب نوع المشاريع")
    for name, file in DATA_FILES.items():
        if name == "الافتراضي":
            continue
        with st.expander(name):
            up = st.file_uploader(name, type=["xlsx"], key=file)
            if up:
                (DATA_DIR / file).write_bytes(up.getbuffer())
                st.success("تم الرفع")
    st.stop()

# ================= Home =================
if st.session_state.page == "home":
    st.title("لوحة المعلومات")

    # ===== Top buttons =====
    cols1 = st.columns(5)
    for i, name in enumerate(list(DATA_FILES.keys())[:5]):
        if name != "الافتراضي":
            with cols1[i]:
                if st.button(name):
                    st.session_state.top_nav = name
                    st.rerun()

    cols2 = st.columns(5)
    for i, name in enumerate(list(DATA_FILES.keys())[5:10]):
        with cols2[i]:
            if st.button(name):
                st.session_state.top_nav = name
                st.rerun()

    st.caption(f"📊 التحليل الحالي: {st.session_state.top_nav}")

    df = load_data()
    if df is None:
        st.warning("لم يتم رفع ملف")
        st.stop()

    # ===== الفلاتر =====
    f1,f2,f3 = st.columns(3)
    with f1:
        proj = st.selectbox("اسم المشروع", ["الكل"] + df["اسم المشروع"].dropna().unique().tolist())
    with f2:
        stat = st.selectbox("حالة المشروع", ["الكل"] + df["حالة المشروع"].dropna().unique().tolist())
    with f3:
        ent = st.selectbox("الجهة", ["الكل"] + df["الجهة"].dropna().unique().tolist())

    filtered = df.copy()
    if proj != "الكل":
        filtered = filtered[filtered["اسم المشروع"] == proj]
    if stat != "الكل":
        filtered = filtered[filtered["حالة المشروع"] == stat]
    if ent != "الكل":
        filtered = filtered[filtered["الجهة"] == ent]

    # ===== KPI =====
    k1,k2,k3 = st.columns(3)
    k1.markdown(f"<div class='card blue'><h2>{len(filtered)}</h2>عدد المشاريع</div>", unsafe_allow_html=True)
    k2.markdown(f"<div class='card green'><h2>{filtered['قيمة العقد'].sum():,.0f}</h2>قيمة العقود</div>", unsafe_allow_html=True)
    k3.markdown(f"<div class='card orange'><h2>{filtered['قيمة المستخلصات'].sum():,.0f}</h2>المستخلصات</div>", unsafe_allow_html=True)

    # ===== حالة المشاريع =====
    st.subheader("حالة المشاريع")
    st.bar_chart(build_status_df(filtered).set_index("الحالة"))

    # ===== شارتين جنب بعض =====
    c1,c2 = st.columns(2)
    with c1:
        st.subheader("المشاريع حسب الجهة")
        st.bar_chart(filtered["الجهة"].value_counts())
    with c2:
        st.subheader("المشاريع حسب الحالة")
        st.bar_chart(filtered["حالة المشروع"].value_counts())

    # ===== تنبيهات =====
    overdue = filtered[filtered["حالة المشروع"].str.contains("متأخر|متعثر", na=False)]
    risk = filtered[
        (filtered["تاريخ الانتهاء"] <= pd.Timestamp.today() + timedelta(days=30)) &
        (filtered["نسبة الإنجاز"] < 70)
    ]

    b1,b2 = st.columns(2)
    if b1.button(f"المشاريع المتأخرة ({len(overdue)})"):
        st.session_state.show_overdue = not st.session_state.show_overdue
    if b2.button(f"المشاريع المتوقع تأخرها ({len(risk)})"):
        st.session_state.show_risk = not st.session_state.show_risk

    if st.session_state.show_overdue:
        st.dataframe(overdue, use_container_width=True)
    if st.session_state.show_risk:
        st.dataframe(risk, use_container_width=True)

    st.markdown("---")
    st.subheader("تفاصيل المشاريع")
    st.dataframe(filtered, use_container_width=True)
