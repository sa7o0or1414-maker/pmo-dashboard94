import streamlit as st

# إعدادات الصفحة
st.set_page_config(
    page_title="منصة PMO",
    page_icon="📊",
    layout="wide"
)

# --- تهيئة الحالة ---
if "page" not in st.session_state:
    st.session_state.page = "home"

# --- CSS اتجاه عربي + تنسيق الأزرار ---
st.markdown("""
<style>
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
    }

    section[data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }

    .menu-button button {
        width: 100%;
        height: 60px;
        font-size: 18px;
        margin-bottom: 10px;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# --- البار الجانبي بالأيقونات ---
with st.sidebar:
    st.markdown("## 🧭 القائمة")

    if st.button("🏠 الصفحة الرئيسية", key="home_btn"):
        st.session_state.page = "home"

    if st.button("📤 رفع البيانات", key="upload_btn"):
        st.session_state.page = "upload"

    if st.button("🔐 تسجيل الدخول", key="login_btn"):
        st.session_state.page = "login"

# --- محتوى الصفحات ---
if st.session_state.page == "home":
    st.title("📊 الصفحة الرئيسية")
    st.write("مرحبًا بك في منصة إدارة المشاريع (PMO).")
    st.info("هنا سيتم لاحقًا عرض مؤشرات الأداء ولوحات المعلومات.")

elif st.session_state.page == "upload":
    st.title("📤 رفع البيانات")
    st.write("سيتم لاحقًا رفع ملفات Excel لتحديث الداشبورد.")
    st.warning("🔒 هذه الصفحة ستُقفل لاحقًا وتتطلب تسجيل دخول.")

elif st.session_state.page == "login":
    st.title("🔐 تسجيل الدخول")
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    st.button("تسجيل الدخول")
