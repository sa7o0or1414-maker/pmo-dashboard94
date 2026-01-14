import streamlit as st

# ------------------ إعدادات الصفحة ------------------
st.set_page_config(
    page_title="منصة PMO",
    layout="wide"
)

# ------------------ الحالة ------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ------------------ بيانات الدخول (مؤقتة) ------------------
VALID_USER = "admin"
VALID_PASS = "1234"

# ------------------ CSS الهوية ------------------
st.markdown("""
<style>
    :root {
        --main-color: #153e46;
        --main-color-light: #1f5661;
        --main-color-dark: #0f2d33;
    }

    html, body, [class*="css"] {
        direction: rtl;
        text-align: center;
        font-family: 'Segoe UI', sans-serif;
    }

    section[data-testid="stSidebar"] {
        background-color: var(--main-color-dark);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    .sidebar-title {
        color: white;
        font-size: 22px;
        margin: 20px 0;
        font-weight: 600;
    }

    .stButton button {
        width: 220px;
        height: 55px;
        background-color: var(--main-color);
        color: white;
        border: none;
        border-radius: 14px;
        font-size: 16px;
        margin-bottom: 16px;
        transition: 0.3s;
    }

    .stButton button:hover {
        background-color: var(--main-color-light);
    }

    .block-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 90vh;
    }

    h1 {
        color: var(--main-color);
    }
</style>
""", unsafe_allow_html=True)

# ------------------ البار الجانبي ------------------
with st.sidebar:

    # اللوقو
    st.image("assets/logo.png", width=120)

    st.markdown('<div class="sidebar-title">القائمة</div>', unsafe_allow_html=True)

    if st.button("الصفحة الرئيسية"):
        st.session_state.page = "home"

    if st.button("رفع البيانات"):
        st.session_state.page = "upload"

    if not st.session_state.logged_in:
        if st.button("تسجيل الدخول"):
            st.session_state.page = "login"
    else:
        if st.button("تسجيل خروج"):
            st.session_state.logged_in = False
            st.session_state.page = "home"

# ------------------ الصفحات ------------------

# الصفحة الرئيسية
if st.session_state.page == "home":
    st.title("الصفحة الرئيسية")
    st.write("منصة داخلية لإدارة ومتابعة بيانات المشاريع.")
    st.write("سيتم عرض المؤشرات ولوحات التحكم هنا.")

# صفحة تسجيل الدخول
elif st.session_state.page == "login":
    st.title("تسجيل الدخول")

    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")

    if st.button("دخول"):
        if username == VALID_USER and password == VALID_PASS:
            st.session_state.logged_in = True
            st.success("تم تسجيل الدخول بنجاح")
            st.session_state.page = "home"
        else:
            st.error("بيانات الدخول غير صحيحة")

# صفحة رفع البيانات (مقفلة)
elif st.session_state.page == "upload":
    if not st.session_state.logged_in:
        st.title("غير مصرح")
        st.warning("يجب تسجيل الدخول للوصول إلى هذه الصفحة")
    else:
        st.title("رفع البيانات")
        st.write("ارفع ملفات البيانات لتحديث لوحة التحكم")
        st.file_uploader("اختر ملف Excel", type=["xlsx"])
