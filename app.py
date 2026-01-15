import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import timedelta
import base64
import altair as alt

# ================= إعدادات الصفحة =================
st.set_page_config(
    page_title="لوحة التحكم | PMO",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= Session State =================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "role" not in st.session_state:
    st.session_state.role = "viewer"
if "top_filter" not in st.session_state:
    st.session_state.top_filter = "الكل"

# ================= المسارات =================
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
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f2d33, #153e46);
}
section[data-testid="stSidebar"] * {
    color: white !important;
    text-align: center;
}
.sidebar-btn button {
    display: inline-flex;
    justify-content: center;
    align-items: center;
    padding: 10px 26px;
    margin: 8px auto;
    background: rgba(255,255,255,0.18);
    border-radius: 20px;
    border: none;
    font-size: 14px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.25);
}
.topbar {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 10px;
    background: #153e46;
    padding: 12px;
    border-radius: 16px;
    margin-bottom: 20px;
}
.topbar button {
    background: rgba(255,255,255,0.18);
    color: white;
    border: none;
    border-radius: 18px;
    padding: 8px 18px;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# ================= أدوات =================
def img64(p: Path):
    return base64.b64encode(p.read_bytes()).decode()

def load_data():
    if not EXCEL_PATH.exists():
        return None
    df = pd.read_excel(EXCEL_PATH, engine="openpyxl")
    df.columns = [c.strip() for c in df.columns]

    df.rename(columns={
        "إسم المشـــروع": "اسم المشروع",
        "تاريخ الانتهاء من المشروع": "تاريخ الانتهاء",
        "تاريخ تسليم الموقع": "تاريخ التسليم",
        "قيمة المستخلصات المعتمده": "قيمة المستخلصات",
    }, inplace=True)

    for c in ["تاريخ الانتهاء","تاريخ التسليم"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    for c in ["قيمة العقد","قيمة المستخلصات","المتبقي من المستخلص","نسبة الإنجاز"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

# ================= Sidebar =================
with st.sidebar:
    if LOGO_PATH.exists():
        st.markdown(
            f"<img src='data:image/png;base64,{img64(LOGO_PATH)}' width='120' style='margin:20px auto;'>",
            unsafe_allow_html=True
        )

    if st.button("الصفحة الرئيسية"):
        st.session_state.page = "home"
        st.rerun()

    if st.button("رفع البيانات"):
        st.session_state.page = "upload"
        st.rerun()

# ================= Upload =================
if st.session_state.page == "upload":
    st.title("رفع البيانات")
    excel = st.file_uploader("ملف Excel", ["xlsx"])
    if excel:
        EXCEL_PATH.write_bytes(excel.getbuffer())
        st.success("تم رفع الملف")
    st.stop()

# ================= Home =================
if st.session_state.page == "home":
    st.title("لوحة التحكم")

    df = load_data()
    if df is None:
        st.warning("يرجى رفع ملف Excel")
        st.stop()

    # ===== Top Bar =====
    top_items = [
        "مشاريع الباب الثالث","مشاريع الباب الرابع","مشاريع بهجة",
        "تطبيق دليل PMD","المشاريع المنجزة","مشاريع المحفظة",
        "الدراسات وقوائم التحقق","دورة المشتريات",
        "مواقع المشاريع","مشاريع الإسكان"
    ]

    cols = st.columns(len(top_items))
    for i, name in enumerate(top_items):
        if cols[i].button(name):
            st.session_state.top_filter = name

    filtered = df.copy()
    if st.session_state.top_filter != "الكل" and "التصنيف" in filtered.columns:
        filtered = filtered[
            filtered["التصنيف"].astype(str).str.contains(st.session_state.top_filter, na=False)
        ]

    # ===== KPI =====
    k1,k2,k3 = st.columns(3)
    k1.metric("عدد المشاريع", len(filtered))
    k2.metric("قيمة العقود", f"{filtered['قيمة العقد'].sum():,.0f}")
    k3.metric("نسبة الإنجاز", f"{filtered['نسبة الإنجاز'].mean():.1f}%")

    # ===== الشارتين =====
    c1,c2 = st.columns(2)
    with c1:
        st.bar_chart(filtered["البلدية"].value_counts())
    with c2:
        st.bar_chart(filtered.groupby("الجهة")["قيمة العقد"].sum())

    # ===== تنبيهات =====
    overdue = filtered[filtered["حالة المشروع"].astype(str).str.contains("متأخر|متعثر")]
    risk = filtered[
        (filtered["تاريخ الانتهاء"] <= pd.Timestamp.today() + timedelta(days=30)) &
        (filtered["نسبة الإنجاز"] < 70)
    ]

    st.subheader("تنبيهات المشاريع")
    st.write("المشاريع المتأخرة:", len(overdue))
    st.write("المشاريع المتوقع تأخرها:", len(risk))

    # ===== جدول =====
    st.subheader("تفاصيل المشاريع")
    st.dataframe(filtered, use_container_width=True)
