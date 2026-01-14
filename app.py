import streamlit as st
from pathlib import Path

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

# ------------------ المسارات ------------------
ASSETS_DIR = Path("assets")
LOGO_PATH = ASSETS_DIR / "logo.png"
ASSETS_DIR.mkdir(exist_ok=True)

# ------------------ CSS شامل (سنترة كاملة) ------------------
st.markdown("""
<style>
    :root {
        --main-color: #153e46;
        --main-color-light: #1f5661;
        --main-color-dark: #0f2d33;
    }

    /* سنترة كل شيء */
    html, body, [class*="css"] {
        direction: rtl;
        text-align: center !important;
        font-family: 'Segoe UI', sans-serif;
    }

    /* الشريط الجانبي */
    section[data-testid="stSidebar"] {
        background-color: var(--main-color-dark);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center !important;
    }

    /* نص اللوقو البديل */
    .brand-text {
        color: white;
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 14px;
    }

    /* عنوان القائمة */
    .sidebar-title {
        color: white;
        font-size: 22px;
        margin: 18px 0 26px 0;
        font-weight: 600;
    }

    /* أزرار البار */
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
        text-align: center;
    }

    .stButton button:hover {
        background-color: var(--main-color-light);
    }

    /* محتوى الصفحات */
    .block-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 90vh;
        text-align: center !important;
    }

    /* العناوين */
    h1, h2, h3, h4, h5, h6 {
        color: var(--main-color);
        text-align: center !important;
    }

    /* النصوص والرسائل */
    p, span, label, div {
        text-align: center !important;
    }

    /* حقول الإدخال */
    input {
        text-align: center !important;
    }

    /* اللوقو */
    img {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
</style>
""", unsafe_allow_html=True)

# ------------------ البار الجانبي ------------------
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=120)
    else:
        st.markdown('<div class="brand-text">منصة PMO</div>', unsafe_allow_html=True)

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

if st.session_state.page == "home":
    st.title("الصفحة الرئيسية")
    st.write("منصة داخلية لإدارة ومتابعة بيانات المشاريع.")
    st.write("سيتم عرض مؤشرات الأداء ولوحات التحكم هنا.")

elif st.session_state.page == "login":
    st.title("تسجيل الدخول")
    st.text_input("اسم المستخدم")
    st.text_input("كلمة المرور", type="password")

    if st.button("دخول"):
        if st.session_state.get("اسم المستخدم", "") == VALID_USER:
            st.session_state.logged_in = True
            st.success("تم تسجيل الدخول بنجاح")
            st.session_state.page = "home"
        else:
            st.error("بيانات الدخول غير صحيحة")

elif st.session_state.page == "upload":
    if not st.session_state.logged_in:
        st.title("غير مصرح")
        st.warning("يجب تسجيل الدخول للوصول إلى هذه الصفحة")
    else:
        st.title("رفع البيانات")

        st.subheader("رفع ملف Excel")
        excel_file = st.file_uploader("اختر ملف Excel", type=["xlsx"])

        if excel_file:
            st.success("تم رفع ملف Excel بنجاح")

        st.divider()

        st.subheader("رفع شعار الجهة")
        logo_file = st.file_uploader(
            "اختر صورة الشعار",
            type=["png", "jpg", "jpeg"]
        )

        if logo_file:
            with open(LOGO_PATH, "wb") as f:
                f.write(logo_file.getbuffer())

            st.success("تم حفظ الشعار بنجاح")
            st.image(str(LOGO_PATH), width=120)
