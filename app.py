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

.card {
    background:#fff;
    padding:18px;
    border-radius:18px;
    box-shadow:0 10px 28px rgba(0,0,0,0.08);
    text-align:center;
    min-height:140px;
}
.card h2 { font-size:22px; margin-bottom:6px; }
.card.blue { border-top:4px solid #2c7be5; }
.card.green { border-top:4px solid #00a389; }
.card.orange { border-top:4px solid #f4a261; }
.card.gray { border-top:4px solid #6c757d; }

.topbar-btn button{
    background:#1e5055 !important;
    color:#fff !important;
    border-radius:14px !important;
    min-width:160px;
    height:44px;
}
.topbar-btn button:hover{
    background:#24666c !important;
}
</style>
""", unsafe_allow_html=True)

# ================= أدوات =================
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

    for c in ["قيمة العقد","قيمة المستخلصات","نسبة الإنجاز","نسبة الانجاز","التكلفة"]:
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

# ===== Top Buttons =====
items = list(DATA_FILES.keys())
items.remove("الافتراضي")

r1 = st.columns(5)
for name, col in zip(items[:5], r1):
    with col:
        if st.button(name):
            st.session_state.top_nav = name
            st.rerun()

r2 = st.columns(5)
for name, col in zip(items[5:], r2):
    with col:
        if st.button(name):
            st.session_state.top_nav = name
            st.rerun()

st.caption(f"📊 التحليل الحالي: {st.session_state.top_nav}")

df = load_data()
if df is None:
    st.warning("لا يوجد ملف لهذا القسم")
    st.stop()

# ================= تحليل مشاريع بهجة فقط =================
if st.session_state.top_nav == "مشاريع بهجة":

    st.subheader("تحليل مشاريع بهجة")

    f1,f2,f3,f4 = st.columns(4)

    with f1:
        mun = st.selectbox("البلدية", ["الكل"] + sorted(df["البلدية"].dropna().unique()))
    with f2:
        project = st.selectbox("اسم المشروع", ["الكل"] + sorted(df["اسم المشروع"].dropna().unique()))
    with f3:
        ptype = st.selectbox("نوع المشروع", ["الكل"] + sorted(df["نوع المشروع"].dropna().unique()))
    with f4:
        approval = st.selectbox("حالة الاعتماد", ["الكل"] + sorted(df["حالة الاعتماد"].dropna().unique()))

    filtered = df.copy()
    if mun != "الكل": filtered = filtered[filtered["البلدية"] == mun]
    if project != "الكل": filtered = filtered[filtered["اسم المشروع"] == project]
    if ptype != "الكل": filtered = filtered[filtered["نوع المشروع"] == ptype]
    if approval != "الكل": filtered = filtered[filtered["حالة الاعتماد"] == approval]

    c1,c2,c3 = st.columns(3)

    total_cost = filtered["التكلفة"].sum()

    progress_col = "نسبة الإنجاز" if "نسبة الإنجاز" in filtered.columns else "نسبة الانجاز"
    avg_progress = pd.to_numeric(filtered[progress_col], errors="coerce").mean()
    completed = (pd.to_numeric(filtered[progress_col], errors="coerce") >= 100).sum()

    c1.markdown(f"<div class='card green'><h2>{total_cost:,.0f}</h2>إجمالي التكلفة</div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='card blue'><h2>{completed}</h2>المشاريع المكتملة</div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='card orange'><h2>{avg_progress:.1f}%</h2>نسبة الإنجاز</div>", unsafe_allow_html=True)

    ch1,ch2 = st.columns(2)
    with ch1:
        st.subheader("المستهدف")
        st.bar_chart(filtered["المستهدف"].value_counts())
    with ch2:
        st.subheader("حالة المشروع")
        st.bar_chart(filtered["حالة المشروع"].value_counts())

    st.markdown("---")
    st.subheader("تفاصيل مشاريع بهجة")
    st.dataframe(filtered, use_container_width=True)
    st.stop()

# ================= باقي الصفحات (الباب الثالث والرابع وغيرها) =================

filtered = df.copy()

f1,f2,f3,f4,f5 = st.columns(5)
with f1:
    if "البلدية" in filtered.columns:
        mun = st.selectbox("البلدية", ["الكل"] + sorted(filtered["البلدية"].dropna().unique()))
        if mun != "الكل": filtered = filtered[filtered["البلدية"] == mun]
with f2:
    project = st.selectbox("اسم المشروع", ["الكل"] + sorted(filtered["اسم المشروع"].dropna().unique()))
    if project != "الكل": filtered = filtered[filtered["اسم المشروع"] == project]
with f3:
    if "نوع المشروع" in filtered.columns:
        pt = st.selectbox("نوع المشروع", ["الكل"] + sorted(filtered["نوع المشروع"].dropna().unique()))
        if pt != "الكل": filtered = filtered[filtered["نوع المشروع"] == pt]
with f4:
    if "حالة الاعتماد" in filtered.columns:
        ap = st.selectbox("حالة الاعتماد", ["الكل"] + sorted(filtered["حالة الاعتماد"].dropna().unique()))
        if ap != "الكل": filtered = filtered[filtered["حالة الاعتماد"] == ap]
with f5:
    if "حالة المشروع" in filtered.columns:
        stt = st.selectbox("حالة المشروع", ["الكل"] + sorted(filtered["حالة المشروع"].dropna().unique()))
        if stt != "الكل": filtered = filtered[filtered["حالة المشروع"] == stt]

k1,k2,k3,k4,k5,k6 = st.columns(6)
k1.markdown(f"<div class='card blue'><h2>{len(filtered)}</h2>عدد المشاريع</div>", unsafe_allow_html=True)
k2.markdown(f"<div class='card green'><h2>{filtered['قيمة العقد'].sum():,.0f}</h2>قيمة العقود</div>", unsafe_allow_html=True)
k3.markdown(f"<div class='card gray'><h2>{filtered['قيمة المستخلصات'].sum():,.0f}</h2>المستخلصات</div>", unsafe_allow_html=True)
k4.markdown(f"<div class='card orange'><h2>{filtered.get('المتبقي من المستخلص',0).sum():,.0f}</h2>المتبقي</div>", unsafe_allow_html=True)

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

c1,c2 = st.columns(2)
with c1:
    st.subheader("حسب البلدية")
    st.bar_chart(filtered["البلدية"].value_counts())
with c2:
    st.subheader("حسب حالة المشروع")
    st.bar_chart(filtered["حالة المشروع"].value_counts())

st.subheader("تنبيهات المشاريع")
overdue = filtered[filtered["حالة المشروع"].astype(str).str.contains("متأخر|متعثر", na=False)]
risk = filtered[(filtered["تاريخ الانتهاء"] <= pd.Timestamp.today()+timedelta(days=30)) &
                (filtered["نسبة الإنجاز"] < 70)]

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
