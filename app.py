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
    "top_nav": ""
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

EXCEL_PATH = DATA_DIR / "data.xlsx"
LOGO_PATH = ASSETS_DIR / "logo.png"

# ================= CSS =================
st.markdown("""
<style>
html, body, [class*="css"] {
    direction: rtl;
    font-family: 'Segoe UI', sans-serif;
    color: #153e46;
}
h1,h2,h3 { text-align:center; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f2d33, #153e46);
    padding-top: 30px;
}
section[data-testid="stSidebar"] * {
    color: white !important;
    text-align: center;
}
section[data-testid="stSidebar"] .stButton > button {
    padding: 10px 26px;
    margin: 10px auto;
    background: rgba(255,255,255,0.18);
    border-radius: 20px;
    border: none;
    font-size: 14px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.25);
}

/* Cards */
.card {
    background: #fff;
    padding: 18px;
    border-radius: 18px;
    box-shadow: 0 10px 28px rgba(0,0,0,0.08);
    text-align: center;
}
.card h2 { font-size: 20px; margin: 0; }
.card.blue { border-top:4px solid #2c7be5; }
.card.green { border-top:4px solid #00a389; }
.card.orange { border-top:4px solid #f4a261; }
.card.gray { border-top:4px solid #6c757d; }
</style>
""", unsafe_allow_html=True)

# ================= أدوات =================
def img64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()

def load_data():
    if not EXCEL_PATH.exists():
        return None
    df = pd.read_excel(EXCEL_PATH, engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]

    df.rename(columns={
        "إسم المشـــروع": "اسم المشروع",
        "تاريخ الانتهاء من المشروع": "تاريخ الانتهاء",
        "تاريخ تسليم الموقع": "تاريخ التسليم",
        "قيمة المستخلصات المعتمده": "قيمة المستخلصات",
    }, inplace=True)

    for c in ["تاريخ الانتهاء","تاريخ التسليم"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")

    for c in ["قيمة العقد","قيمة المستخلصات","المتبقي من المستخلص","نسبة الصرف","نسبة الإنجاز"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df

def status_color(s):
    if any(k in s for k in ["متأخر","متعثر"]): return "#e63946"
    if any(k in s for k in ["مكتمل","منجز"]): return "#00a389"
    if any(k in s for k in ["جاري","قيد"]): return "#2c7be5"
    if any(k in s for k in ["متوقف"]): return "#6c757d"
    return "#f4a261"

def build_status_df(df):
    s = df["حالة المشروع"].fillna("غير محدد").astype(str)
    out = s.value_counts().rename_axis("الحالة").reset_index(name="عدد")
    out["لون"] = out["الحالة"].apply(status_color)
    return out

# ================= Sidebar =================
with st.sidebar:
    if LOGO_PATH.exists():
        st.markdown(
            f"<img src='data:image/png;base64,{img64(LOGO_PATH)}' width='120'>",
            unsafe_allow_html=True
        )

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

    st.stop()   # <<< الحل الأساسي


# ================= Upload =================
if st.session_state.page == "upload":
    st.title("رفع البيانات")
    excel = st.file_uploader("ملف Excel", ["xlsx"])
    logo = st.file_uploader("اللوقو", ["png"])

    if excel:
        EXCEL_PATH.write_bytes(excel.getbuffer())
        st.success("تم رفع البيانات")
    if logo:
        LOGO_PATH.write_bytes(logo.getbuffer())
        st.success("تم رفع اللوقو")

    st.stop()   # <<< مهم


# ================= Home =================
st.title("لوحة المعلومات")

df = load_data()
if df is None:
    st.warning("يرجى رفع ملف Excel")
    st.stop()

# (بقية الكود التحليلي يبقى كما هو عندك بدون تغيير)
