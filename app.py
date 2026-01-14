import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import timedelta
import base64

# ================= إعدادات الصفحة =================
st.set_page_config(
    page_title="لوحة التحكم | PMO",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= Session State =================
for k, v in {
    "role": "viewer",
    "page": "home",
    "logo_align": "center",
    "show_overdue": False,
    "show_risk": False,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

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

# ================= CSS =================
st.markdown("""
<style>
html, body, [class*="css"] {
    direction: rtl;
    font-family: 'Segoe UI', sans-serif;
    color: #153e46;
}
h1,h2,h3 {
    text-align:center;
    color:#153e46;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f2d33, #153e46);
}
section[data-testid="stSidebar"] * {
    color: white !important;
    text-align: center;
}
section[data-testid="stSidebar"] .stButton > button {
    width: 78%;
    height: 40px;
    margin: 10px 0;
    background: #1f4f58;
    border-radius: 14px;
    border: none;
    font-size: 14px;
    white-space: nowrap;
}

/* Cards */
.card {
    background: #fff;
    padding: 18px;
    border-radius: 18px;
    box-shadow: 0 10px 28px rgba(0,0,0,0.08);
    text-align: center;
}
.card h2 { font-size:20px; white-space:nowrap; }
.card.blue { border-top:4px solid #2c7be5; }
.card.green { border-top:4px solid #00a389; }
.card.red { border-top:4px solid #e63946; }
.card.gray { border-top:4px solid #6c757d; }
.card.orange { border-top:4px solid #f4a261; }
</style>
""", unsafe_allow_html=True)

# ================= أدوات =================
def img64(path):
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
    df["تاريخ الانتهاء"] = pd.to_datetime(df["تاريخ الانتهاء"], errors="coerce")
    df["تاريخ التسليم"] = pd.to_datetime(df["تاريخ التسليم"], errors="coerce")
    return df

STATUS_COLORS = {
    "مكتمل": "#00a389",
    "جاري": "#2c7be5",
    "متأخر": "#e63946",
    "متوقف": "#6c757d",
    "غير محدد": "#f4a261"
}

# ================= Sidebar =================
with st.sidebar:
    if LOGO_PATH.exists():
        st.markdown(
            f"<div style='text-align:{st.session_state.logo_align}'>"
            f"<img src='data:image/png;base64,{img64(LOGO_PATH)}' width='110'></div>",
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
            st.error("بيانات غير صحيحة")

# ================= Upload =================
if st.session_state.page == "upload":
    st.title("رفع البيانات")
    excel = st.file_uploader("ملف Excel", ["xlsx"])
    logo = st.file_uploader("لوقو PNG", ["png"])
    st.session_state.logo_align = st.selectbox("محاذاة اللوقو", ["center","right","left"])
    if excel:
        EXCEL_PATH.write_bytes(excel.getbuffer())
        st.success("تم رفع البيانات")
    if logo:
        LOGO_PATH.write_bytes(logo.getbuffer())
        st.success("تم رفع اللوقو")

# ================= Home =================
if st.session_state.page == "home":
    st.title("لوحة التحكم")
    df = load_data()
    if df is None:
        st.warning("ارفع ملف Excel")
        st.stop()

    # ===== Filters =====
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

    filtered = df.copy()
    if cat!="الكل": filtered = filtered[filtered["التصنيف"]==cat]
    if ent!="الكل": filtered = filtered[filtered["الجهة"]==ent]
    if mun!="الكل": filtered = filtered[filtered["البلدية"]==mun]
    if status!="الكل": filtered = filtered[filtered["حالة المشروع"]==status]
    if ctype!="الكل": filtered = filtered[filtered["نوع العقد"]==ctype]

    # ===== KPI =====
    k1,k2,k3,k4,k5,k6 = st.columns(6)
    k1.markdown(f"<div class='card blue'><h2>{len(filtered)}</h2>عدد المشاريع</div>", unsafe_allow_html=True)
    k2.markdown(f"<div class='card green'><h2>{filtered['قيمة العقد'].sum():,.0f}</h2>قيمة العقود</div>", unsafe_allow_html=True)
    k3.markdown(f"<div class='card gray'><h2>{filtered['قيمة المستخلصات'].sum():,.0f}</h2>المستخلصات</div>", unsafe_allow_html=True)
    k4.markdown(f"<div class='card orange'><h2>{filtered['المتبقي من المستخلص'].sum():,.0f}</h2>المتبقي</div>", unsafe_allow_html=True)
    k5.markdown(f"<div class='card blue'><h2>{filtered['نسبة الصرف'].mean():.1f}%</h2>متوسط الصرف</div>", unsafe_allow_html=True)
    k6.markdown(f"<div class='card green'><h2>{filtered['نسبة الإنجاز'].mean():.1f}%</h2>متوسط الإنجاز</div>", unsafe_allow_html=True)

    # ===== حالة المشاريع (أفقي + ملون) =====
    st.subheader("حالة المشاريع")
    status_counts = filtered["حالة المشروع"].fillna("غير محدد").value_counts()
    status_df = pd.DataFrame({
        "الحالة": status_counts.index,
        "عدد المشاريع": status_counts.values
    })
    st.bar_chart(
        status_df.set_index("الحالة"),
        use_container_width=True
    )

    # ===== جدول تفصيلي =====
    st.markdown("---")
    st.subheader("تفاصيل المشاريع")

    st.dataframe(
        filtered[
            [
                "اسم المشروع","الجهة","البلدية","المقاول",
                "حالة المشروع","تاريخ التسليم","تاريخ الانتهاء",
                "قيمة العقد","نسبة الإنجاز","نسبة الصرف"
            ]
        ].sort_values("تاريخ الانتهاء"),
        use_container_width=True,
        hide_index=True
    )

    # ===== تفاصيل مشروع بالاختيار =====
    st.markdown("---")
    st.subheader("تفاصيل مشروع")

    project = st.selectbox(
        "اختر مشروع",
        filtered["اسم المشروع"].dropna().unique()
    )

    p = filtered[filtered["اسم المشروع"] == project].iloc[0]

    st.markdown(
        f"""
        <div class="card">
        <h3>{project}</h3>
        <p><b>الجهة:</b> {p['الجهة']}</p>
        <p><b>البلدية:</b> {p['البلدية']}</p>
        <p><b>المقاول:</b> {p['المقاول']}</p>
        <p><b>الحالة:</b> <span style="color:{STATUS_COLORS.get(p['حالة المشروع'],'#000')}">
        {p['حالة المشروع']}</span></p>
        <p><b>قيمة العقد:</b> {p['قيمة العقد']:,.0f}</p>
        <p><b>نسبة الإنجاز:</b> {p['نسبة الإنجاز']}%</p>
        </div>
        """,
        unsafe_allow_html=True
    )
