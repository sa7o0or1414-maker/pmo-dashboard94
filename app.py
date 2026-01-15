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
    "top_nav": ""   # <<< NEW
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

# ================= ربط الأزرار بالملفات =================
DATASETS = {   # <<< NEW
    "مشاريع الباب الثالث": "bab3.xlsx",
    "مشاريع الباب الرابع": "bab4.xlsx",
    "مشاريع بهجة": "bahja.xlsx",
    "تطبيق دليل PMD": "pmd.xlsx",
    "المشاريع المنجزة": "completed.xlsx",
    "مشاريع المحفظة": "portfolio.xlsx",
    "الدراسات وقوائم التحقق": "studies.xlsx",
    "دورة المشتريات": "procurement.xlsx",
    "مواقع المشاريع": "sites.xlsx",
    "مشاريع الإسكان": "housing.xlsx",
}

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
h1,h2,h3{text-align:center}

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
    box-shadow: 0 6px 16px rgba(0,0,0,0.25);
}

/* Cards */
.card {
    background:#fff;
    padding:18px;
    border-radius:18px;
    box-shadow:0 10px 28px rgba(0,0,0,.08);
    text-align:center;
}
.card.blue{border-top:4px solid #2c7be5}
.card.green{border-top:4px solid #00a389}
.card.orange{border-top:4px solid #f4a261}
.card.gray{border-top:4px solid #6c757d}
</style>
""", unsafe_allow_html=True)

# ================= أدوات =================
def img64(path):
    return base64.b64encode(path.read_bytes()).decode()

def load_data():
    # <<< NEW: اختيار الملف حسب الزر العلوي
    file_name = DATASETS.get(st.session_state.top_nav, "data.xlsx")
    path = DATA_DIR / file_name

    if not path.exists():
        return None

    df = pd.read_excel(path, engine="openpyxl")
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
    s = str(s)
    if "متأخر" in s or "متعثر" in s: return "#e63946"
    if "مكتمل" in s or "منجز" in s: return "#00a389"
    if "جاري" in s or "قيد" in s: return "#2c7be5"
    if "متوقف" in s: return "#6c757d"
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

# ================= Upload =================
if st.session_state.page == "upload":
    st.title("رفع البيانات")

    dataset = st.selectbox(   # <<< NEW
        "نوع المشاريع",
        list(DATASETS.keys())
    )

    excel = st.file_uploader("ملف Excel", ["xlsx"])
    if excel:
        save_path = DATA_DIR / DATASETS[dataset]
        save_path.write_bytes(excel.getbuffer())
        st.success(f"تم رفع ملف {dataset} بنجاح")

# ================= Home =================
if st.session_state.page == "home":
    st.title("لوحة المعلومات")

    # ================= البار العلوي =================
    top_items = list(DATASETS.keys())

    r1 = st.columns(5)
    for i, name in enumerate(top_items[:5]):
        if r1[i].button(name):
            st.session_state.top_nav = name

    r2 = st.columns(5)
    for i, name in enumerate(top_items[5:]):
        if r2[i].button(name):
            st.session_state.top_nav = name

    if st.session_state.top_nav:
        st.caption(f"📌 التحليل الحالي: {st.session_state.top_nav}")

    # ================= التحليل =================
    df = load_data()
    if df is None:
        st.warning("لا يوجد ملف بيانات مرفوع لهذا القسم")
        st.stop()

    filtered = df.copy()

    # ===== الفلاتر =====
    f1,f2,f3 = st.columns(3)
    with f1:
        p = st.selectbox("اسم المشروع", ["الكل"]+sorted(filtered["اسم المشروع"].dropna().unique()))
        if p!="الكل": filtered=filtered[filtered["اسم المشروع"]==p]
    with f2:
        s = st.selectbox("حالة المشروع", ["الكل"]+sorted(filtered["حالة المشروع"].dropna().unique()))
        if s!="الكل": filtered=filtered[filtered["حالة المشروع"]==s]
    with f3:
        m = st.selectbox("البلدية", ["الكل"]+sorted(filtered["البلدية"].dropna().unique()))
        if m!="الكل": filtered=filtered[filtered["البلدية"]==m]

    # ===== KPI =====
    k1,k2,k3 = st.columns(3)
    k1.markdown(f"<div class='card blue'>{len(filtered)}<br>عدد المشاريع</div>",unsafe_allow_html=True)
    k2.markdown(f"<div class='card green'>{filtered['قيمة العقد'].sum():,.0f}<br>قيمة العقود</div>",unsafe_allow_html=True)
    k3.markdown(f"<div class='card orange'>{filtered['قيمة المستخلصات'].sum():,.0f}<br>المستخلصات</div>",unsafe_allow_html=True)

    # ===== حالة المشاريع =====
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

    # ===== تنبيهات (فتح / إغلاق) =====
    overdue = filtered[filtered["حالة المشروع"].astype(str).str.contains("متأخر|متعثر")]
    risk = filtered[
        (filtered["تاريخ الانتهاء"] <= pd.Timestamp.today()+timedelta(days=30)) &
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

    # ===== جدول =====
    st.markdown("---")
    st.subheader("تفاصيل المشاريع")
    st.dataframe(filtered, use_container_width=True)
