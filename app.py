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
html, body, [class*="css"] {
    direction: rtl;
    font-family: 'Segoe UI', sans-serif;
}
h1 { text-align:center; }

section[data-testid="stSidebar"] {
    background: #1e5055 !important;
}
section[data-testid="stSidebar"] * {
    color: #ffffff !important;
}
section[data-testid="stSidebar"] button {
    background: #1e5055 !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    color: #ffffff !important;
}

.topbar-btn button {
    background: #1e5055 !important;
    color: #ffffff !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    min-width: 160px;
    height: 44px;
}

.topbar-btn button:hover {
    background: #24666c !important;
}

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

.card h2 {
    font-size: 22px;
    margin-bottom: 6px;
    white-space: nowrap;
}
</style>
""", unsafe_allow_html=True)

# ================= أدوات =================
def load_data():
    file = DATA_FILES.get(st.session_state.top_nav, "data.xlsx")
    path = DATA_DIR / file
    if not path.exists():
        return None

    df = pd.read_excel(path)
    df.columns = [str(c).strip() for c in df.columns]

    df.rename(columns={
        "إسم المشـــروع": "اسم المشروع",
        "قيمة المستخلصات المعتمده": "قيمة المستخلصات",
        "تاريخ الانتهاء من المشروع": "تاريخ الانتهاء",
    }, inplace=True)

    return df

def get_progress_column(df):
    if "نسبة الإنجاز" in df.columns:
        return "نسبة الإنجاز"
    if "نسبة الانجاز" in df.columns:
        return "نسبة الانجاز"
    return None

def status_color(s):
    s = str(s)
    if "متأخر" in s or "متعثر" in s: return "#e63946"
    if "مكتمل" in s or "منجز" in s: return "#00a389"
    if "جاري" in s or "قيد" in s: return "#2c7be5"
    return "#f4a261"

def build_status_df(df):
    if "حالة المشروع" not in df.columns:
        return pd.DataFrame(columns=["الحالة","عدد","لون"])
    s = df["حالة المشروع"].fillna("غير محدد").astype(str)
    out = s.value_counts().rename_axis("الحالة").reset_index(name="عدد")
    out["لون"] = out["الحالة"].apply(status_color)
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
    st.title("رفع الملفات حسب نوع المشاريع")
    for name, file in DATA_FILES.items():
        if name == "الافتراضي":
            continue
        with st.expander(name):
            up = st.file_uploader(name, type=["xlsx"], key=file)
            if up:
                (DATA_DIR / file).write_bytes(up.getbuffer())
                st.success("تم رفع الملف")
    st.stop()

# ================= Home =================
st.title("لوحة المعلومات")

items = list(DATA_FILES.keys())
items.remove("الافتراضي")

r1 = st.columns(5)
for i, name in enumerate(items[:5]):
    with r1[i]:
        st.markdown("<div class='topbar-btn'>", unsafe_allow_html=True)
        if st.button(name):
            st.session_state.top_nav = name
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

r2 = st.columns(5)
for i, name in enumerate(items[5:]):
    with r2[i]:
        st.markdown("<div class='topbar-btn'>", unsafe_allow_html=True)
        if st.button(name):
            st.session_state.top_nav = name
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

st.caption(f"📊 التحليل الحالي: {st.session_state.top_nav}")

df = load_data()
if df is None:
    st.warning("لا يوجد ملف لهذا القسم")
    st.stop()

filtered = df.copy()

# ================= كارد المشاريع المكتملة =================
progress_col = get_progress_column(filtered)

completed_projects = 0
avg_progress = 0

if progress_col:
    filtered[progress_col] = pd.to_numeric(filtered[progress_col], errors="coerce")
    completed_projects = (filtered[progress_col] >= 100).sum()
    avg_progress = filtered[progress_col].mean()

c1, c2 = st.columns(2)

c1.markdown(
    f"<div class='card green'><h2>{completed_projects}</h2>عدد المشاريع المكتملة</div>",
    unsafe_allow_html=True
)

c2.markdown(
    f"<div class='card blue'><h2>{avg_progress:.1f}%</h2>متوسط نسبة الإنجاز</div>",
    unsafe_allow_html=True
)

# ================= حالة المشاريع =================
st.subheader("حالة المشاريع")
sdf = build_status_df(filtered)
if not sdf.empty:
    st.altair_chart(
        alt.Chart(sdf).mark_bar().encode(
            x="عدد",
            y=alt.Y("الحالة", sort="-x"),
            color=alt.Color("الحالة", scale=alt.Scale(domain=sdf["الحالة"], range=sdf["لون"]))
        ),
        use_container_width=True
    )

# ================= جدول =================
st.markdown("---")
st.subheader("تفاصيل المشاريع")
st.dataframe(filtered, use_container_width=True)
