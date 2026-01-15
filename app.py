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

/* Sidebar */
section[data-testid="stSidebar"] {
    background:#1e5055;
}
section[data-testid="stSidebar"] * {
    color:white !important;
}

/* Cards */
.card {
    background:#fff;
    padding:18px;
    border-radius:18px;
    box-shadow:0 8px 22px rgba(0,0,0,0.08);
    text-align:center;
    min-height:140px;
}
.card h2 {
    font-size:22px;
    margin:0;
    white-space:nowrap;
}
.card.blue { border-top:4px solid #2c7be5; }
.card.green { border-top:4px solid #00a389; }
.card.orange { border-top:4px solid #f4a261; }
.card.gray { border-top:4px solid #6c757d; }

/* Top buttons */
.topbar-btn button{
    background:#1e5055 !important;
    color:white !important;
    border-radius:14px !important;
    padding:10px 18px !important;
    border:1px solid rgba(255,255,255,0.3) !important;
}
.topbar-btn button:hover{
    background:#24666c !important;
}
</style>
""", unsafe_allow_html=True)

# ================= Helpers =================
def load_data():
    file = DATA_FILES.get(st.session_state.top_nav, "data.xlsx")
    path = DATA_DIR / file
    if not path.exists():
        return None

    df = pd.read_excel(path, engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]

    df.rename(columns={
        "إسم المشـــروع": "اسم المشروع",
        "قيمة المستخلصات المعتمده": "قيمة المستخلصات",
        "تاريخ الانتهاء من المشروع": "تاريخ الانتهاء",
    }, inplace=True)

    for c in ["قيمة العقد","قيمة المستخلصات","المتبقي من المستخلص","نسبة الإنجاز"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    if "تاريخ الانتهاء" in df.columns:
        df["تاريخ الانتهاء"] = pd.to_datetime(df["تاريخ الانتهاء"], errors="coerce")

    return df

def status_color(s):
    s = str(s)
    if "متأخر" in s or "متعثر" in s: return "#e63946"
    if "مكتمل" in s or "منجز" in s: return "#00a389"
    if "جاري" in s or "قيد" in s: return "#2c7be5"
    return "#f4a261"

def build_status_df(df):
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

# ================= Home =================
st.title("لوحة المعلومات")

# ===== Top Navigation =====
items = list(DATA_FILES.keys())
items.remove("الافتراضي")

r1 = st.columns(len(items))
for i, name in enumerate(items):
    with r1[i]:
        st.markdown("<div class='topbar-btn'>", unsafe_allow_html=True)
        if st.button(name, key=name):
            st.session_state.top_nav = name
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

st.caption(f"📊 التحليل الحالي: {st.session_state.top_nav}")

df = load_data()
if df is None:
    st.warning("لا يوجد ملف لهذا القسم")
    st.stop()

# ======================================================
# ================= تحليل بهجة (خاص) ===================
# ======================================================
if st.session_state.top_nav == "مشاريع بهجة":

    st.subheader("تحليل مشاريع بهجة")

    f1,f2,f3,f4 = st.columns(4)

    with f1:
        mun = st.selectbox("البلدية", ["الكل"] + sorted(df["البلدية"].dropna().unique()))
    with f2:
        proj = st.selectbox("اسم المشروع", ["الكل"] + sorted(df["اسم المشروع"].dropna().unique()))
    with f3:
        ptype = st.selectbox("نوع المشروع", ["الكل"] + sorted(df["نوع المشروع"].dropna().unique()))
    with f4:
        appr = st.selectbox("حالة الاعتماد", ["الكل"] + sorted(df["حالة الاعتماد"].dropna().unique()))

    filtered = df.copy()
    if mun!="الكل": filtered = filtered[filtered["البلدية"]==mun]
    if proj!="الكل": filtered = filtered[filtered["اسم المشروع"]==proj]
    if ptype!="الكل": filtered = filtered[filtered["نوع المشروع"]==ptype]
    if appr!="الكل": filtered = filtered[filtered["حالة الاعتماد"]==appr]

    c1,c2,c3 = st.columns(3)
    c1.markdown(f"<div class='card blue'><h2>{len(filtered)}</h2>عدد المشاريع</div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='card green'><h2>{filtered['التكلفة'].sum():,.0f}</h2>إجمالي التكلفة</div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='card orange'><h2>{filtered['نسبة الإنجاز'].mean():.1f}%</h2>نسبة الإنجاز</div>", unsafe_allow_html=True)

    ch1,ch2 = st.columns(2)
    with ch1:
        st.subheader("حالة المشروع")
        st.bar_chart(filtered["حالة المشروع"].value_counts())
    with ch2:
        st.subheader("المستهدف")
        st.bar_chart(filtered["المستهدف"].value_counts())

    st.subheader("تفاصيل مشاريع بهجة")
    st.dataframe(filtered, use_container_width=True)

    st.stop()

# ======================================================
# ========== تحليل الباب الثالث والرابع ================
# ======================================================

# -------- الفلاتر --------
filtered = df.copy()
f1,f2,f3,f4,f5 = st.columns(5)

with f1:
    if "التصنيف" in filtered.columns:
        cat = st.selectbox("التصنيف", ["الكل"]+sorted(filtered["التصنيف"].dropna().unique()))
        if cat!="الكل": filtered=filtered[filtered["التصنيف"]==cat]
with f2:
    if "الجهة" in filtered.columns:
        ent = st.selectbox("الجهة", ["الكل"]+sorted(filtered["الجهة"].dropna().unique()))
        if ent!="الكل": filtered=filtered[filtered["الجهة"]==ent]
with f3:
    mun = st.selectbox("البلدية", ["الكل"]+sorted(filtered["البلدية"].dropna().unique()))
    if mun!="الكل": filtered=filtered[filtered["البلدية"]==mun]
with f4:
    stt = st.selectbox("حالة المشروع", ["الكل"]+sorted(filtered["حالة المشروع"].dropna().unique()))
    if stt!="الكل": filtered=filtered[filtered["حالة المشروع"]==stt]
with f5:
    if "نوع العقد" in filtered.columns:
        ct = st.selectbox("نوع العقد", ["الكل"]+sorted(filtered["نوع العقد"].dropna().unique()))
        if ct!="الكل": filtered=filtered[filtered["نوع العقد"]==ct]

# -------- KPI --------
k1,k2,k3,k4,k5,k6 = st.columns(6)
k1.markdown(f"<div class='card blue'><h2>{len(filtered)}</h2>عدد المشاريع</div>", unsafe_allow_html=True)
k2.markdown(f"<div class='card green'><h2>{filtered['قيمة العقد'].sum():,.0f}</h2>قيمة العقود</div>", unsafe_allow_html=True)
k3.markdown(f"<div class='card gray'><h2>{filtered['قيمة المستخلصات'].sum():,.0f}</h2>المستخلصات</div>", unsafe_allow_html=True)
k4.markdown(f"<div class='card orange'><h2>{filtered['المتبقي من المستخلص'].sum():,.0f}</h2>المتبقي</div>", unsafe_allow_html=True)
k5.markdown(f"<div class='card blue'><h2>{(filtered['قيمة المستخلصات'].sum()/filtered['قيمة العقد'].sum()*100 if filtered['قيمة العقد'].sum()>0 else 0):.1f}%</h2>نسبة الصرف</div>", unsafe_allow_html=True)
k6.markdown(f"<div class='card green'><h2>{filtered['نسبة الإنجاز'].mean():.1f}%</h2>نسبة الإنجاز</div>", unsafe_allow_html=True)

# -------- حالة المشاريع --------
st.subheader("حالة المشاريع")
sdf = build_status_df(filtered)
st.altair_chart(
    alt.Chart(sdf).mark_bar().encode(
        x="عدد",
        y=alt.Y("الحالة", sort="-x"),
        color=alt.Color("الحالة", scale=alt.Scale(domain=sdf["الحالة"], range=sdf["لون"]))
    ),
    use_container_width=True
)

# -------- شارتين --------
c1,c2 = st.columns(2)
with c1:
    st.subheader("عدد المشاريع حسب البلدية")
    st.bar_chart(filtered["البلدية"].value_counts())
with c2:
    st.subheader("عدد المشاريع حسب حالة المشروع")
    st.bar_chart(filtered["حالة المشروع"].value_counts())

# -------- التنبيهات --------
st.subheader("تنبيهات المشاريع")
overdue = filtered[filtered["حالة المشروع"].astype(str).str.contains("متأخر|متعثر", na=False)]
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

# -------- جدول --------
st.markdown("---")
st.subheader("تفاصيل المشاريع")
st.dataframe(filtered, use_container_width=True)
