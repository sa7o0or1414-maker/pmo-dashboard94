import streamlit as st

# إعدادات الصفحة
st.set_page_config(
    page_title="منصة PMO",
    layout="wide"
)

# الحالة
if "page" not in st.session_state:
    st.session_state.page = "home"

# CSS الهوية البصرية + الاتجاه
st.markdown("""
<style>
    :root {
        --main-color: #153e46;
        --main-color-light: #1f5661;
        --main-color-dark: #0f2d33;
    }

    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', sans-serif;
    }

    /* الشريط الجانبي */
    section[data-testid="stSidebar"] {
        background-color: var(--main-color-dark);
        padding-top: 20px;
    }

    /* عنوان القائمة */
    .sidebar-title {
        color: white;
        font-size: 20px;
        margin-bottom: 20px;
        font-weight: 600;
    }

    /* أزرار القائمة */
    .stButton button {
        width: 100%;
        height: 55px;
        background-color: var(--main-color);
        color: white;
        border: none;
        border-radius: 12px;
        font-size: 16px;
        margin-bottom: 12px;
        transition: 0.3s;
    }

    .stButton button:hover {
        background-color: var(--main-color-light);
        color: white;
    }

    /* العناوين */
    h1, h2, h3 {
        color: var(--main-color);
    }

    /* البطاقات */
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# البار الجانبي
with st.sidebar:
    st.markdown('<div class="sidebar-title">القائمة</div>', unsafe_allow_html=True)

    if st.button("الصفحة الرئيسية"):
        st.session_state.page = "home"

    if st.button("رفع البيانات"):
        st.session_state.page = "upload"

    if st.button("تسجيل الدخول"):
        st.session_state.page = "login"

# محتوى الصفحات
if st.session_state.page == "home":
    st.title("الصفحة الرئيسية")
    st.write("مرحبًا بك في منصة إدارة المشاريع.")
    st.info("سيتم هنا عرض مؤشرات الأداء ولوحات المتابعة.")

elif st.session_state.page == "upload":
    st.title("رفع البيانات")
    st.write("هذه الصفحة مخصصة لرفع ملفات البيانات.")
    st.warning("هذه الصفحة ستتطلب تسجيل دخول لاحقًا.")

elif st.session_state.page == "login":
    st.title("تسجيل الدخول")
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    st.button("دخول")
