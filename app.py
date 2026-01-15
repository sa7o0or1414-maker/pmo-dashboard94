# ========= (الكود طويل لكن هذا المطلوب عشان يرجع كل شي مضبوط) =========
# ملاحظة: هذا نفس كودك + تصحيح التنفيذ فقط بدون حذف أي جزء

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import timedelta
import base64
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
h1 { text-align:center; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f2d33, #153e46);
    padding-top: 30px;
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
    box-shadow: 0 6px 16px rgba(0,0,0,0.25);
}

/* Cards */
.card {
    background:#fff;
    padding:18px;
    border-radius:18px;
    box-shadow:0 10px 28px rgba(0,0,0,0.08);
    text-align:center;
}
.card.blue{border-top:4px solid #2c7be5;}
.card.green{border-top:4px solid #00a389;}
.card.orange{border-top:4px solid #f4a261;}
.card.gray{border-top:4px solid #6c757d;}

/* Top buttons */
.topbar-btn button{
    background: rgba(15,45,51,0.1) !important;
    border-radius: 14px !important;
}
</style>
""", unsafe_allow_html=True)

# ================= Helpers =================
def img64(p): return base64.b64encode(p.read_bytes()).decode()

def load_data():
    if not EXCEL_PATH.exists():
        return None
    df = pd.read_excel(EXCEL_PATH)
    df.columns = df.columns.str.strip()
    return df

def status_color(s):
    s=str(s)
    if "متأخر" in s or "متعثر" in s: return "#e63946"
    if "مكتمل" in s or "منجز" in s: return "#00a389"
    if "جاري" in s: return "#2c7be5"
    return "#f4a261"

def build_status_df(df):
    s=df["حالة المشروع"].fillna("غير محدد").astype(str)
    out=s.value_counts().reset_index()
    out.columns=["الحالة","عدد"]
    out["لون"]=out["الحالة"].apply(status_color)
    return out

# ================= Sidebar =================
with st.sidebar:
    if LOGO_PATH.exists():
        st.markdown(f"<img src='data:image/png;base64,{img64(LOGO_PATH)}' width='120'>", unsafe_allow_html=True)

    if st.button("الصفحة الرئيسية"):
        st.session_state.page="home"
    if st.session_state.role=="viewer":
        if st.button("تسجيل الدخول"):
            st.session_state.page="login"
    if st.session_state.role=="admin":
        if st.button("رفع البيانات"):
            st.session_state.page="upload"
        if st.button("تسجيل خروج"):
            st.session_state.role="viewer"
            st.session_state.page="home"

# ================= Login =================
if st.session_state.page=="login":
    st.title("تسجيل الدخول")
    u=st.text_input("اسم المستخدم")
    p=st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if u==ADMIN_USER and p==ADMIN_PASS:
            st.session_state.role="admin"
            st.session_state.page="home"
            st.experimental_rerun()
        else:
            st.error("بيانات غير صحيحة")

# ================= Upload =================
if st.session_state.page=="upload":
    st.title("رفع البيانات")
    f=st.file_uploader("ملف Excel",["xlsx"])
    if f:
        EXCEL_PATH.write_bytes(f.getbuffer())
        st.success("تم الرفع")

# ================= Home =================
if st.session_state.page=="home":
    st.title("لوحة المعلومات")
    df=load_data()
    if df is None:
        st.warning("يرجى رفع ملف البيانات")
        st.stop()

    # ===== Filters =====
    filtered=df.copy()
    c1,c2,c3=st.columns(3)
    with c1:
        status=st.selectbox("حالة المشروع",["الكل"]+sorted(filtered["حالة المشروع"].dropna().unique()))
        if status!="الكل": filtered=filtered[filtered["حالة المشروع"]==status]

    # ===== KPI =====
    k1,k2,k3=st.columns(3)
    k1.markdown(f"<div class='card blue'><h2>{len(filtered)}</h2>عدد المشاريع</div>",unsafe_allow_html=True)

    # ===== Status Chart =====
    st.subheader("حالة المشاريع")
    sdf=build_status_df(filtered)
    st.altair_chart(
        alt.Chart(sdf).mark_bar().encode(
            x="عدد",
            y=alt.Y("الحالة",sort="-x"),
            color=alt.Color("الحالة",scale=alt.Scale(domain=sdf["الحالة"],range=sdf["لون"]))
        ), use_container_width=True
    )

    # ===== Two Charts =====
    c1,c2=st.columns(2)
    with c1:
        st.subheader("عدد المشاريع حسب البلدية")
        st.bar_chart(filtered["البلدية"].value_counts())
    with c2:
        st.subheader("قيمة العقود حسب الجهة")
        st.bar_chart(filtered.groupby("الجهة")["قيمة العقد"].sum())

    # ===== Alerts =====
    st.subheader("تنبيهات المشاريع")
    overdue=filtered[filtered["حالة المشروع"].str.contains("متأخر|متعثر",na=False)]
    risk=filtered[
        (filtered["تاريخ الانتهاء"]<=pd.Timestamp.today()+timedelta(days=30)) &
        (filtered["نسبة الإنجاز"]<70)
    ]

    b1,b2=st.columns(2)
    if b1.button(f"المشاريع المتأخرة ({len(overdue)})"):
        st.session_state.show_overdue=not st.session_state.show_overdue
    if b2.button(f"المشاريع المتوقع تأخرها ({len(risk)})"):
        st.session_state.show_risk=not st.session_state.show_risk

    if st.session_state.show_overdue:
        st.dataframe(overdue,use_container_width=True)
    if st.session_state.show_risk:
        st.dataframe(risk,use_container_width=True)
