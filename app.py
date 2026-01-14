import streamlit as st

# إعدادات الصفحة
st.set_page_config(
    page_title="منصة PMO",
    layout="wide"
)

# الحالة
if "page" not in st.session_state:
    st.session_state.page = "home"

# CSS التنسيق والهوية
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

    /* الشريط الجانبي */
    section[data-testid="stSidebar"] {
        background-color: var(--main-color-dark);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    /* عنوان القائمة */
    .sidebar-title {
        color: white;
        font-size: 22px;
        margin-bottom: 30px;
        font-weight: 600;
        text-align: center;
    }

    /* أزرار القائمة */
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
        color: white;
    }

    /* محتوى الصفحة */
    .block-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 90vh;
    }

    /* العناوين */
    h1 {
        color: var(--main-color);
        text-align: center;
    }

    /* النصوص */
    p {
        text-align: center;
        font-size: 16px;
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
    st.write("سيتم هنا عرض مؤشرات الأداء ولوحات المتابعة.")

elif st.session_state.page == "upload":
    st.title("رفع البيانات")
    st.write("هذه الصفحة مخصصة لرفع ملفات البيانات.")
    st.write("ستتطلب هذه الصفحة تسجيل دخول لاحقًا.")

elif st.session_state.page == "login":
    st.title("تسجيل الدخول")
    st.text_input("اسم المستخدم")
    st.text_input("كلمة المرور", type="password")
    st.button("دخول")
