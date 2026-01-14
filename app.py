import streamlit as st
import pandas as pd
from pathlib import Path

# ================= إعدادات الصفحة =================
st.set_page_config(page_title="منصة PMO", layout="wide")

# ================= الحالة =================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "role" not in st.session_state:
    st.session_state.role = "viewer"

# ================= بيانات المسؤول =================
ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# ================= المسارات =================
BASE_DIR = Path(".")
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

EXCEL_PATH = DATA_DIR / "data.xlsx"
LOGO_PATH = ASSETS_DIR / "logo.png"

# ================= CSS (سنترة + هوية) =================
st.markdown("""
<style>
html,body,[class*="css"]{
direction:rtl;text-align:center;font-family:'Segoe UI'
}
section[data-testid="stSidebar"]{
background:#0f2d33;
display:flex;flex-direction:column;
justify-content:center;align-items:center
}
.stButton button{
width:230px;height:56px;border-radius:16px;
background:#153e46;color:white;border:none;
font-size:16px;margin-bottom:14px
}
.block-container{
display:flex;flex-direction:column;
justify-content:center;align-items:center;
min-height:90vh
}
.card{
background:white;padding:22px;border-radius:18px;
box-shadow:0 8px 25px rgba(0,0,0,.08);width:100%
}
</style>
""", unsafe_allow_html=True)

# ================= دالة قراءة Excel (نسخة قوية) =================
def load_data():
    if not EXCEL_PATH.exists():
        return None

    # المحاولة 1: قراءة مباشرة
    try:
        df = pd.read_excel(EXCEL_PATH, engine="openpyxl")
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception:
        pass

    # المحاولة 2: قراءة أول Sheet يدويًا
    try:
        xls = pd.ExcelFile(EXCEL_PATH, engine="openpyxl")
        sheet = xls.sheet_names[0]
        df = pd.read_excel(EXCEL_PATH, sheet_name=sheet, engine="openpyxl")
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error("تعذر قراءة ملف Excel بسبب تنسيق غير سليم.")
        st.info(
            "الرجاء إعادة حفظ الملف بصيغة Excel (.xlsx) من Microsoft Excel "
            "ثم إعادة رفعه."
        )
        st.code(str(e))
        return None

# ================= Sidebar =================
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=120)
    else:
        st.markdown("<b style='color:white'>منصة PMO</b>", unsafe_allow_html=True)

    if st.button("الصفحة الرئيسية"):
        st.session_state.page = "home"

    if st.session_state.role == "admin":
        if st.button("رفع البيانات"):
            st.session_state.page = "upload"

    if st.session_state.role != "admin":
        if st.button("تسجيل دخول المسؤول"):
            st.session_state.page = "login"
    else:
        if st.button("تسجيل خروج"):
            st.session_state.role = "viewer"
            st.session_state.page = "home"
            st.rerun()

# ================= تسجيل الدخول =================
if st.session_state.page == "login":
    st.title("تسجيل دخول المسؤول")

    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")

    if st.button("دخول"):
        if u == ADMIN_USER and p == ADMIN_PASS:
            st.session_state.role = "admin"
            st.session_state.page = "home"
            st.success("تم تسجيل الدخول بنجاح")
            st.rerun()
        else:
            st.error("بيانات الدخول غير صحيحة")

# ================= رفع البيانات =================
if st.session_state.page == "upload":
    if st.session_state.role != "admin":
        st.warning("غير مصرح لك بالوصول")
    else:
        st.title("رفع البيانات")

        excel = st.file_uploader("رفع ملف Excel", type=["xlsx"])
        if excel:
            with open(EXCEL_PATH, "wb") as f:
                f.write(excel.getbuffer())

            st.success("تم رفع الملف بنجاح")
            st.session_state.page = "home"
            st.rerun()

        st.divider()

        logo = st.file_uploader("رفع شعار الجهة", type=["png","jpg","jpeg"])
        if logo:
            with open(LOGO_PATH, "wb") as f:
                f.write(logo.getbuffer())
            st.success("تم حفظ الشعار")
            st.rerun()

# ================= الصفحة الرئيسية =================
if st.session_state.page == "home":
    st.title("لوحة التحكم")

    df = load_data()

    if df is None:
        st.warning("لا توجد بيانات بعد. ارفع ملف Excel من صفحة رفع البيانات.")
    else:
        st.success("تم تحميل البيانات بنجاح")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                f"<div class='card'>عدد المشاريع<br><h2>{len(df)}</h2></div>",
                unsafe_allow_html=True
            )

        with col2:
            total_contract = pd.to_numeric(df.get("قيمة العقد", 0), errors="coerce").sum()
            st.markdown(
                f"<div class='card'>إجمالي قيمة العقود<br><h2>{total_contract:,.0f}</h2></div>",
                unsafe_allow_html=True
            )

        with col3:
            avg_spend = pd.to_numeric(df.get("نسبة الصرف", 0), errors="coerce").mean()
            st.markdown(
                f"<div class='card'>متوسط نسبة الصرف<br><h2>{avg_spend:.1f}%</h2></div>",
                unsafe_allow_html=True
            )

        st.divider()
        st.dataframe(df, use_container_width=True)
