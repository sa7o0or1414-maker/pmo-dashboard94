import streamlit as st
from pathlib import Path
import base64

# ================== إعداد الصفحة ==================
st.set_page_config(
    page_title="PMO Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================== CSS ==================
st.markdown("""
<style>

/* إخفاء الهيدر */
header {visibility: hidden;}

/* ================= Sidebar ================= */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f2d33, #153e46);
    width: 260px;
}

/* محتوى البار */
section[data-testid="stSidebar"] > div {
    display: flex;
    flex-direction: column;
    justify-content: center;   /* توسيط عمودي */
    align-items: center;       /* توسيط أفقي */
    height: 100vh;
}

/* أزرار البار */
section[data-testid="stSidebar"] .stButton > button {
    width: 180px;
    padding: 12px 0;
    margin: 12px 0;
    background: rgba(255,255,255,0.15);
    border-radius: 20px;
    border: none;
    font-size: 14px;
    white-space: nowrap;
    color: white;
    box-shadow: 0 6px 18px rgba(0,0,0,0.18);
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.28);
    transform: scale(1.03);
}

/* ================= Main ================= */
.main-title {
    text-align: center;
    font-size: 36px;
    font-weight: 700;
    color: #153e46;
    margin-top: 20px;
}

/* ================= Mobile ================= */
@media (max-width: 768px) {

    section[data-testid="stSidebar"] {
        width: 200px;
    }

    section[data-testid="stSidebar"] .stButton > button {
        width: 150px;
        font-size: 12px;
        padding: 10px 0;
    }

    .main-title {
        font-size: 26px;
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
    LOGO_PATH = "logo.png"

    if Path(LOGO_PATH).exists():
        st.markdown(
            f"<img src='data:image/png;base64,{img64(LOGO_PATH)}' width='110'>",
            unsafe_allow_html=True
        )

    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)

    st.button("الصفحة الرئيسية")
    st.button("رفع البيانات")
    st.button("تسجيل خروج")

# ================== المحتوى ==================
st.markdown("<div class='main-title'>لوحة التحكم</div>", unsafe_allow_html=True)

st.markdown(
    "<p style='text-align:center;color:#666;'>الداشبورد متوافق مع الديسكتوب والجوال</p>",
    unsafe_allow_html=True
)

# ===== كروت (مكانها محفوظ للكود الحقيقي) =====
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("عدد المشاريع", "—")
with c2:
    st.metric("قيمة العقود", "—")
with c3:
    st.metric("نسبة الإنجاز", "—")
