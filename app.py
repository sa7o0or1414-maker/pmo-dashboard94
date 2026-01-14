import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

# ================= إعدادات الصفحة =================
st.set_page_config(page_title="منصة PMO", layout="wide")

# ================= الحالة =================
if "show_overdue" not in st.session_state:
    st.session_state.show_overdue = False
if "show_risk" not in st.session_state:
    st.session_state.show_risk = False

# ================= المسارات =================
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
EXCEL_PATH = DATA_DIR / "data.xlsx"

# ================= CSS =================
st.markdown("""
<style>
html, body, [class*="css"] {
    direction: rtl;
    text-align: center !important;
    font-family: 'Segoe UI', sans-serif;
}
section[data-testid="stSidebar"] {
    display:none;
}
.card {
    background:white;
    padding:22px;
    border-radius:18px;
    box-shadow:0 8px 25px rgba(0,0,0,.08);
}
h1,h2,h3,p,label { text-align:center !important; }
</style>
""", unsafe_allow_html=True)

# ================= قراءة Excel + توحيد الأعمدة =================
def load_data():
    if not EXCEL_PATH.exists():
        return None

    df = pd.read_excel(EXCEL_PATH, engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]

    rename_map = {
        "إسم المشـــروع": "اسم المشروع",
        "تاريخ الانتهاء من المشروع": "تاريخ الانتهاء",
        "تاريخ تسليم الموقع": "تاريخ التسليم",
        "قيمة المستخلصات المعتمده": "قيمة المستخلصات",
    }

    df.rename(columns=rename_map, inplace=True)

    df["تاريخ الانتهاء"] = pd.to_datetime(df["تاريخ الانتهاء"], errors="coerce")
    df["تاريخ التسليم"] = pd.to_datetime(df["تاريخ التسليم"], errors="coerce")

    return df

# ================= الصفحة الرئيسية =================
st.title("لوحة التحكم")

df = load_data()
if df is None:
    st.warning("ارفع ملف Excel لعرض لوحة التحكم")
    st.stop()

# ================= الفلاتر =================
f1,f2,f3,f4,f5 = st.columns(5)

with f1:
    cat = st.selectbox("التصنيف", ["الكل"] + sorted(df["التصنيف"].dropna().unique()))
with f2:
    ent = st.selectbox("الجهة", ["الكل"] + sorted(df["الجهة"].dropna().unique()))
with f3:
    mun = st.selectbox("البلدية", ["الكل"] + sorted(df["البلدية"].dropna().unique()))
with f4:
    status = st.selectbox("حالة المشروع", ["الكل"] + sorted(df["حالة المشروع"].dropna().unique()))
with f5:
    ctype = st.selectbox("نوع العقد", ["الكل"] + sorted(df["نوع العقد"].dropna().unique()))

filtered = df.copy()
if cat != "الكل": filtered = filtered[filtered["التصنيف"] == cat]
if ent != "الكل": filtered = filtered[filtered["الجهة"] == ent]
if mun != "الكل": filtered = filtered[filtered["البلدية"] == mun]
if status != "الكل": filtered = filtered[filtered["حالة المشروع"] == status]
if ctype != "الكل": filtered = filtered[filtered["نوع العقد"] == ctype]

# ================= KPI Cards =================
k1,k2,k3,k4,k5,k6 = st.columns(6)

with k1:
    st.markdown(f"<div class='card'>عدد المشاريع<br><h2>{len(filtered)}</h2></div>", unsafe_allow_html=True)
with k2:
    st.markdown(f"<div class='card'>قيمة العقود<br><h2>{filtered['قيمة العقد'].sum():,.0f}</h2></div>", unsafe_allow_html=True)
with k3:
    st.markdown(f"<div class='card'>المستخلصات المعتمدة<br><h2>{filtered['قيمة المستخلصات'].sum():,.0f}</h2></div>", unsafe_allow_html=True)
with k4:
    st.markdown(f"<div class='card'>المتبقي<br><h2>{filtered['المتبقي من المستخلص'].sum():,.0f}</h2></div>", unsafe_allow_html=True)
with k5:
    st.markdown(f"<div class='card'>متوسط نسبة الصرف<br><h2>{filtered['نسبة الصرف'].mean():.1f}%</h2></div>", unsafe_allow_html=True)
with k6:
    st.markdown(f"<div class='card'>متوسط الإنجاز<br><h2>{filtered['نسبة الإنجاز'].mean():.1f}%</h2></div>", unsafe_allow_html=True)

st.divider()

# ================= تحليل التأخير =================
today = pd.Timestamp.today()

overdue = filtered[
    (filtered["تاريخ الانتهاء"] < today) &
    (~filtered["حالة المشروع"].isin(["مكتمل","منجز"]))
]

risk = filtered[
    (filtered["تاريخ الانتهاء"] >= today) &
    (filtered["تاريخ الانتهاء"] <= today + timedelta(days=30)) &
    (filtered["نسبة الإنجاز"] < 70)
].copy()

risk["سبب التوقع"] = "قرب تاريخ الانتهاء مع انخفاض نسبة الإنجاز"

# ================= كروت التأخير =================
c1,c2 = st.columns(2)

with c1:
    if st.button(f"المشاريع المتأخرة ({len(overdue)})"):
        st.session_state.show_overdue = not st.session_state.show_overdue

with c2:
    if st.button(f"المشاريع المتوقع تأخرها ({len(risk)})"):
        st.session_state.show_risk = not st.session_state.show_risk

# ================= القوائم =================
if st.session_state.show_overdue:
    st.subheader("قائمة المشاريع المتأخرة")
    st.dataframe(
        overdue[
            ["اسم المشروع","المقاول","رقم العقد","تاريخ التسليم","تاريخ الانتهاء","حالة المشروع"]
        ],
        use_container_width=True
    )

if st.session_state.show_risk:
    st.subheader("قائمة المشاريع المتوقع تأخرها")
    st.dataframe(
        risk[
            ["اسم المشروع","المقاول","رقم العقد","تاريخ الانتهاء","نسبة الإنجاز","سبب التوقع"]
        ],
        use_container_width=True
    )
