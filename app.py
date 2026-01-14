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
    st.session_state.role = "viewer"   # viewer | admin
if "page" not in st.session_state:
    st.session_state.page = "home"
for k in ["show_overdue", "show_risk"]:
    if k not in st.session_state:
        st.session_state[k] = False

# ================= بيانات الدخول =================
ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# ================= المسارات =================
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
EXCEL_PATH = DATA_DIR / "data.xlsx"

# ================= CSS (هوية + توسيط كامل) =================
st.markdown("""
<style>
html, body, [class*="css"] {
    direction: rtl;
    font-family: 'Segoe UI', sans-serif;
}
h1,h2,h3,p,label { text-align:center !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0f2d33;
    display: flex;
    justify-content: center;
}
section[data-testid="stSidebar"] > div {
    width: 100%;
}
section[data-testid="stSidebar"] * {
    color: white !important;
    text-align: center !important;
}
section[data-testid="stSidebar"] .stButton button {
    width: 85%;
    margin: 10px auto;
    background: #153e46;
    border-radius: 16px;
    border: none;
    height: 48px;
    font-size: 15px;
}

/* Sections */
.section {
    margin-top: 30px;
}

/* Cards */
.card {
    background: #ffffff;
    padding: 22px;
    border-radius: 18px;
    box-shadow: 0 10px 28px rgba(0,0,0,0.08);
    text-align: center;
}
.card.blue { border-top: 5px solid #2c7be5; }
.card.green { border-top: 5px solid #00a389; }
.card.orange { border-top: 5px solid #f4a261; }
.card.gray { border-top: 5px solid #6c757d; }

/* Filters */
.filter-box {
    background: #f6f7f9;
    padding: 18px;
    border-radius: 16px;
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
    st.markdown("## PMO")
    st.markdown("مكتب إدارة المشاريع")
    st.divider()

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

    st.divider()
    st.caption("لوحة تحكم PMO")

# ================= صفحة تسجيل الدخول =================
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

# ================= رفع البيانات =================
if st.session_state.page == "upload":
    st.title("رفع البيانات")
    file = st.file_uploader("رفع ملف Excel", type=["xlsx"])
    if file:
        with open(EXCEL_PATH, "wb") as f:
            f.write(file.getbuffer())
        st.success("تم رفع الملف بنجاح")
        st.session_state.page = "home"
        st.rerun()

# ================= الصفحة الرئيسية =================
if st.session_state.page == "home":
    st.title("لوحة التحكم")

    df = load_data()
    if df is None:
        st.warning("ارفع ملف Excel لعرض لوحة التحكم")
        st.stop()

    # ================= الفلاتر =================
    st.markdown("<div class='section filter-box'>", unsafe_allow_html=True)

    f1,f2,f3 = st.columns(3)
    with f1:
        cat = st.selectbox("التصنيف", ["الكل"] + sorted(df["التصنيف"].dropna().unique()))
    with f2:
        ent = st.selectbox("الجهة", ["الكل"] + sorted(df["الجهة"].dropna().unique()))
    with f3:
        mun = st.selectbox("البلدية", ["الكل"] + sorted(df["البلدية"].dropna().unique()))

    f4,f5 = st.columns(2)
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

    # ================= KPI =================
    st.markdown("<div class='section'>", unsafe_allow_html=True)

    k1,k2,k3,k4,k5,k6 = st.columns(6)

    k1.markdown(f"<div class='card blue'>عدد المشاريع<br><h2>{len(filtered)}</h2></div>", unsafe_allow_html=True)
    k2.markdown(f"<div class='card green'>قيمة العقود<br><h2>{filtered['قيمة العقد'].sum():,.0f}</h2></div>", unsafe_allow_html=True)
    k3.markdown(f"<div class='card gray'>المستخلصات<br><h2>{filtered['قيمة المستخلصات'].sum():,.0f}</h2></div>", unsafe_allow_html=True)
    k4.markdown(f"<div class='card orange'>المتبقي<br><h2>{filtered['المتبقي من المستخلص'].sum():,.0f}</h2></div>", unsafe_allow_html=True)
    k5.markdown(f"<div class='card blue'>متوسط الصرف<br><h2>{filtered['نسبة الصرف'].mean():.1f}%</h2></div>", unsafe_allow_html=True)
    k6.markdown(f"<div class='card green'>متوسط الإنجاز<br><h2>{filtered['نسبة الإنجاز'].mean():.1f}%</h2></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ================= الشارتات =================
    st.markdown("<div class='section'>", unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        st.subheader("عدد المشاريع حسب الحالة")
        st.bar_chart(filtered["حالة المشروع"].value_counts())

    with c2:
        st.subheader("قيمة العقود حسب الجهة")
        st.bar_chart(filtered.groupby("الجهة")["قيمة العقد"].sum())

    st.markdown("</div>", unsafe_allow_html=True)

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

    st.markdown("<div class='section'>", unsafe_allow_html=True)

    b1,b2 = st.columns(2)
    with b1:
        if st.button(f"المشاريع المتأخرة ({len(overdue)})"):
            st.session_state.show_overdue = not st.session_state.show_overdue

    with b2:
        if st.button(f"المشاريع المتوقع تأخرها ({len(risk)})"):
            st.session_state.show_risk = not st.session_state.show_risk

    if st.session_state.show_overdue:
        st.dataframe(
            overdue[["اسم المشروع","المقاول","رقم العقد","تاريخ التسليم","تاريخ الانتهاء","حالة المشروع"]],
            use_container_width=True
        )

    if st.session_state.show_risk:
        st.dataframe(
            risk[["اسم المشروع","المقاول","رقم العقد","تاريخ الانتهاء","نسبة الإنجاز","سبب التوقع"]],
            use_container_width=True
        )

    st.markdown("</div>", unsafe_allow_html=True)
