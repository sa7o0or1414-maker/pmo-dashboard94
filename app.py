import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import timedelta

# ================= إعدادات الصفحة =================
st.set_page_config(
    page_title="لوحة التحكم | PMO",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= Session State =================
if "role" not in st.session_state:
    st.session_state.role = "viewer"
if "page" not in st.session_state:
    st.session_state.page = "home"
if "logo_align" not in st.session_state:
    st.session_state.logo_align = "center"

for k in ["show_overdue", "show_risk"]:
    if k not in st.session_state:
        st.session_state[k] = False

# ================= بيانات الدخول =================
ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# ================= المسارات =================
DATA_DIR = Path("data")
ASSETS_DIR = Path("assets")
DATA_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

EXCEL_PATH = DATA_DIR / "data.xlsx"
LOGO_PATH = ASSETS_DIR / "logo.png"

# ================= CSS (البار + لون الخط) =================
st.markdown("""
<style>
html, body, [class*="css"] {
    direction: rtl;
    font-family: 'Segoe UI', sans-serif;
    color: #153e46;
}
h1,h2,h3,p,label {
    text-align:center !important;
    color: #153e46 !important;
}

/* ===== Sidebar ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f2d33, #153e46);
}
section[data-testid="stSidebar"] * {
    color: white !important;
    text-align: center !important;
}

/* Sidebar buttons */
section[data-testid="stSidebar"] .stButton {
    display: flex;
    justify-content: center;
}
section[data-testid="stSidebar"] .stButton > button {
    width: 78%;
    height: 48px;
    margin: 12px 0;
    background: #1f4f58;
    border-radius: 16px;
    border: none;
    font-size: 15px;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #2b6772;
}

/* ===== Cards ===== */
.card {
    background: #ffffff;
    padding: 18px;
    border-radius: 18px;
    box-shadow: 0 10px 28px rgba(0,0,0,0.08);
    text-align: center;
}
.card span {
    font-size: 13px;
}
.card h2 {
    font-size: 22px;
    margin-top: 6px;
    white-space: nowrap;
}
.card.blue { border-top: 4px solid #2c7be5; }
.card.green { border-top: 4px solid #00a389; }
.card.orange { border-top: 4px solid #f4a261; }
.card.gray { border-top: 4px solid #6c757d; }
.card.red { border-top: 4px solid #e63946; }

/* ===== Filters ===== */
.filter-row .stSelectbox > div {
    background: #f3f5f7;
    border-radius: 14px;
}
</style>
""", unsafe_allow_html=True)

# ================= قراءة البيانات =================
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

    df["تاريخ الانتهاء"] = pd.to_datetime(df["تاريخ الانتهاء"], errors="coerce")
    df["تاريخ التسليم"] = pd.to_datetime(df["تاريخ التسليم"], errors="coerce")

    return df

# ================= Sidebar =================
with st.sidebar:

    # ===== Logo =====
    if LOGO_PATH.exists():
        align = st.session_state.logo_align
        st.markdown(
            f"<div style='text-align:{'center' if align=='center' else 'right' if align=='right' else 'left'};'>"
            f"<img src='data:image/png;base64,{LOGO_PATH.read_bytes().hex()}' width='120'>"
            f"</div>",
            unsafe_allow_html=True
        )

    st.markdown("## PMO")
    st.markdown("مكتب إدارة المشاريع")

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
    st.title("تسجيل دخول المسؤول")
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")

    if st.button("دخول"):
        if u == ADMIN_USER and p == ADMIN_PASS:
            st.session_state.role = "admin"
            st.session_state.page = "home"
            st.rerun()
        else:
            st.error("بيانات الدخول غير صحيحة")

# ================= Upload =================
if st.session_state.page == "upload":
    st.title("رفع البيانات")

    excel_file = st.file_uploader("رفع ملف Excel", type=["xlsx"])
    logo_file = st.file_uploader("رفع لوقو (PNG)", type=["png"])

    st.session_state.logo_align = st.selectbox(
        "محاذاة اللوقو في البار",
        ["center", "right", "left"],
        format_func=lambda x: "وسط" if x=="center" else "يمين" if x=="right" else "يسار"
    )

    if excel_file:
        with open(EXCEL_PATH, "wb") as f:
            f.write(excel_file.getbuffer())
        st.success("تم رفع ملف البيانات")

    if logo_file:
        with open(LOGO_PATH, "wb") as f:
            f.write(logo_file.getbuffer())
        st.success("تم رفع اللوقو")

# ================= Home =================
if st.session_state.page == "home":
    st.title("لوحة التحكم")

    df = load_data()
    if df is None:
        st.warning("ارفع ملف Excel لعرض لوحة التحكم")
        st.stop()

    # ===== Filters =====
    st.markdown("<div class='filter-row'>", unsafe_allow_html=True)
    f1,f2,f3 = st.columns(3)
    f4,f5 = st.columns(2)

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
    st.markdown("</div>", unsafe_allow_html=True)

    filtered = df.copy()
    if cat != "الكل": filtered = filtered[filtered["التصنيف"] == cat]
    if ent != "الكل": filtered = filtered[filtered["الجهة"] == ent]
    if mun != "الكل": filtered = filtered[filtered["البلدية"] == mun]
    if status != "الكل": filtered = filtered[filtered["حالة المشروع"] == status]
    if ctype != "الكل": filtered = filtered[filtered["نوع العقد"] == ctype]

    # ===== KPI =====
    k1,k2,k3,k4,k5,k6 = st.columns(6)
    k1.markdown(f"<div class='card blue'><span>عدد المشاريع</span><h2>{len(filtered)}</h2></div>", unsafe_allow_html=True)
    k2.markdown(f"<div class='card green'><span>قيمة العقود</span><h2>{pd.to_numeric(filtered['قيمة العقد'], errors='coerce').sum():,.0f}</h2></div>", unsafe_allow_html=True)
    k3.markdown(f"<div class='card gray'><span>المستخلصات</span><h2>{pd.to_numeric(filtered['قيمة المستخلصات'], errors='coerce').sum():,.0f}</h2></div>", unsafe_allow_html=True)
    k4.markdown(f"<div class='card orange'><span>المتبقي</span><h2>{pd.to_numeric(filtered['المتبقي من المستخلص'], errors='coerce').sum():,.0f}</h2></div>", unsafe_allow_html=True)
    k5.markdown(f"<div class='card blue'><span>متوسط الصرف</span><h2>{pd.to_numeric(filtered['نسبة الصرف'], errors='coerce').mean():.1f}%</h2></div>", unsafe_allow_html=True)
    k6.markdown(f"<div class='card green'><span>متوسط الإنجاز</span><h2>{pd.to_numeric(filtered['نسبة الإنجاز'], errors='coerce').mean():.1f}%</h2></div>", unsafe_allow_html=True)

    # ===== شارت حالة المشاريع (ملون حسب الحالة) =====
    st.subheader("حالة المشاريع")

    status_color_map = {
        "مكتمل": "#00a389",
        "جاري": "#2c7be5",
        "متأخر": "#e63946",
        "متوقف": "#6c757d"
    }

    vc = filtered["حالة المشروع"].fillna("غير محدد").astype(str).value_counts()
    status_df = vc.rename_axis("الحالة").reset_index(name="عدد المشاريع")

    colored_df = pd.DataFrame()
    for s in status_df["الحالة"]:
        colored_df[s] = status_df.apply(
            lambda r: r["عدد المشاريع"] if r["الحالة"] == s else 0,
            axis=1
        )

    st.bar_chart(colored_df, use_container_width=True)
