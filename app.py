import streamlit as st
from pathlib import Path
import base64

# ================== إعداد الصفحة ==================
st.set_page_config(
    page_title="PMO Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================== CSS (Desktop + Mobile) ==================
st.markdown("""
<style>

/* إخفاء هيدر Streamlit */
header {visibility: hidden;}

/* ================= Desktop ================= */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f2d33, #153e46);
    display: flex;
    flex-direction: column;
}

section[data-testid="stSidebar"] > div {
    display: flex;
    flex-direction: column;
    justify-content: center;   /* توسيط عمودي */
    align-items: center;       /* توسيط أفقي */
    height: 100vh;
}

/* أزرار البار */
section[data-testid="stSidebar"] .stButton {
    display: flex;
    justify-content: center;
}

section[data-testid="stSidebar"] .stButton > button {
    padding: 12px 28px;
    margin: 12px 0;
    background: rgba(255,255,255,0.14);
    border-radius: 18px;
    border: none;
    font-size: 14px;
    font-weight: 500;
    white-space: nowrap;
    color: white;
    box-shadow: 0 6px 18px rgba(0,0,0,0.18);
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.25);
    transform: scale(1.03);
}

/* عنوان الصفحة */
.main-title {
    text-align: center;
    font-size: 34px;
    font-weight: 700;
    color: #153e46;
    margin: 20px 0;
}

/* ================= Mobile ================= */
@media (max-width: 768px) {

    /* Sidebar يصير Top Bar */
    section[data-testid="stSidebar"] {
        width: 100% !important;
        height: auto !important;
    }

    section[data-testid="stSidebar"] > div {
        flex-direction: row;
        justify-content: space-around;
        align-items: center;
        height: auto;
        padding: 10px 0;
    }

    /* تصغير اللوقو */
    section[data-testid="stSidebar"] img {
        width: 70px;
    }

    /* أزرار الجوال */
    section[data-testid="stSidebar"] .stButton > button {
        padding: 8px 14px;
        margin: 4px;
        font-size: 12px;
        border-radius: 14px;
    }

    /* عنوان الصفحة */
    .main-title {
        font-size: 24px;
    }

    /* الكروت */
    .stMetric {
        text-align: center;
    }
}
</style>
""", unsafe_allow_html=True)

# ================== دالة قراءة صورة ==================
def img64(path):
    if not Path(path).exists():
        return ""
    data = Path(path).read_bytes()
    return base64.b64encode(data).decode()

# ================== Sidebar ==================
with st.sidebar:
    LOGO_PATH = "logo.png"  # ترفعينه لاحقًا من رفع البيانات

    if Path(LOGO_PATH).exists():
        st.markdown(
            f"<img src='data:image/png;base64,{img64(LOGO_PATH)}'>",
            unsafe_allow_html=True
        )

    st.button("الصفحة الرئيسية")
    st.button("رفع البيانات")
    st.button("تسجيل خروج")

# ================== محتوى الصفحة ==================
st.markdown("<div class='main-title'>لوحة التحكم</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div style='text-align:center; margin-top:20px; color:#555;'>
        الداشبورد جاهز — متوافق مع الجوال والديسكتوب
    </div>
    """,
    unsafe_allow_html=True
)

# ===== مثال كروت (مكانها محفوظ للكود القديم) =====
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("عدد المشاريع", "—")
with col2:
    st.metric("قيمة العقود", "—")
with col3:
    st.metric("نسبة الإنجاز", "—")
