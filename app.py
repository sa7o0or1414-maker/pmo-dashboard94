import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import timedelta
import base64

# Altair
try:
    import altair as alt
    ALTAIR_OK = True
except Exception:
    ALTAIR_OK = False


# ================= إعدادات الصفحة =================
st.set_page_config(
    page_title="لوحة التحكم | PMO",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= Session State =================
defaults = {
    "role": "viewer",
    "page": "home",
    "logo_align": "center",
    "show_overdue": False,
    "show_risk": False
}
for k, v in defaults.items():
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
h1,h2,h3 { text-align:center; color:#153e46; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f2d33, #153e46);
    padding-top: 20px;
}
section[data-testid="stSidebar"] * {
    color: white !important;
    text-align: center;
}
section[data-testid="stSidebar"] .stButton {
    display: flex;
    justify-content: center;
}
section[data-testid="stSidebar"] .stButton > button {
    padding: 10px 26px;
    margin: 10px auto;
    background: rgba(255,255,255,0.14);
    border-radius: 18px;
    border: none;
    font-size: 14px;
    white-space: nowrap;
    box-shadow: 0 6px 18px rgba(0,0,0,0.18);
}

/* Cards */
.card {
    background: #fff;
    padding: 18px;
    border-radius: 18px;
    box-shadow: 0 10px 28px rgba(0,0,0,0.08);
    text-align: center;
}
.card h2 { font-size: 20px; white-space: nowrap; }
.card.blue { border-top:4px solid #2c7be5; }
.card.green { border-top:4px solid #00a389; }
.card.orange { border-top:4px solid #f4a261; }
.card.gray { border-top:4px solid #6c757d; }
</style>
""", unsafe_allow_html=True)

# ================= أدوات =================
def img64(path: Path) -> str:
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

    for c in ["تاريخ الانتهاء","تاريخ التسليم"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")

    for c in ["قيمة العقد","قيمة المستخلصات","المتبقي من المستخلص","نسبة الصرف","نسبة الإنجاز"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df

def status_color(txt):
    s = (txt or "").strip()
    if any(k in s for k in ["متأخر","متعثر"]): return "#e63946"
    if any(k in s for k in ["مكتمل","منجز"]): return "#00a389"
    if any(k in s for k in ["جاري","قيد"]): return "#2c7be5"
    if any(k in s for k in ["متوقف"]): return "#6c757d"
    return "#f4a261"

def build_status_df(filtered):
    if "حالة المشروع" not in filtered.columns:
        return pd.DataFrame({"الحالة":["غير محدد"],"عدد":[0],"لون":["#f4a261"]})
    s = filtered["حالة المشروع"].fillna("غير محدد").astype(str)
    df = s.value_counts().rename_axis("الحالة").reset_index(name="عدد")
    df["لون"] = df["الحالة"].apply(status_color)
    return df

# ================= Sidebar =================
with st.sidebar:
    if LOGO_PATH.exists():
        st.markdown(
            f"<div style='text-align:{st.session_state.logo_align}; margin-bottom:20px;'>"
            f"<img src='data:image/png;base64,{img64(LOGO_PATH)}' width='120'></div>",
            unsafe_allow_html=True
        )

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
        st.warning("يرجى رفع ملف Excel")
        st.stop()

    # ===== Cascading Filters =====
    filtered = df.copy()
    f1,f2,f3 = st.columns(3)
    f4,f5 = st.columns(2)

    with f4:
        if "حالة المشروع" in filtered.columns:
            status = st.selectbox("حالة المشروع", ["الكل"] + sorted(filtered["حالة المشروع"].dropna().unique()))
            if status!="الكل": filtered = filtered[filtered["حالة المشروع"]==status]

    with f5:
        if "نوع العقد" in filtered.columns:
            ctype = st.selectbox("نوع العقد", ["الكل"] + sorted(filtered["نوع العقد"].dropna().unique()))
            if ctype!="الكل": filtered = filtered[filtered["نوع العقد"]==ctype]

    with f1:
        if "التصنيف" in filtered.columns:
            cat = st.selectbox("التصنيف", ["الكل"] + sorted(filtered["التصنيف"].dropna().unique()))
            if cat!="الكل": filtered = filtered[filtered["التصنيف"]==cat]

    with f2:
        if "الجهة" in filtered.columns:
            ent = st.selectbox("الجهة", ["الكل"] + sorted(filtered["الجهة"].dropna().unique()))
            if ent!="الكل": filtered = filtered[filtered["الجهة"]==ent]

    with f3:
        if "البلدية" in filtered.columns:
            mun = st.selectbox("البلدية", ["الكل"] + sorted(filtered["البلدية"].dropna().unique()))
            if mun!="الكل": filtered = filtered[filtered["البلدية"]==mun]

    # ===== KPI =====
    k1,k2,k3,k4,k5,k6 = st.columns(6)
    k1.markdown(f"<div class='card blue'><h2>{len(filtered)}</h2>عدد المشاريع</div>", unsafe_allow_html=True)
    k2.markdown(f"<div class='card green'><h2>{filtered['قيمة العقد'].sum():,.0f}</h2>قيمة العقود</div>", unsafe_allow_html=True)
    k3.markdown(f"<div class='card gray'><h2>{filtered['قيمة المستخلصات'].sum():,.0f}</h2>المستخلصات</div>", unsafe_allow_html=True)
    k4.markdown(f"<div class='card orange'><h2>{filtered['المتبقي من المستخلص'].sum():,.0f}</h2>المتبقي</div>", unsafe_allow_html=True)
    k5.markdown(f"<div class='card blue'><h2>{filtered['نسبة الصرف'].mean():.1f}%</h2>متوسط الصرف</div>", unsafe_allow_html=True)
    k6.markdown(f"<div class='card green'><h2>{filtered['نسبة الإنجاز'].mean():.1f}%</h2>متوسط الإنجاز</div>", unsafe_allow_html=True)

    # ===== حالة المشاريع =====
    st.subheader("حالة المشاريع")
    sdf = build_status_df(filtered)

    if ALTAIR_OK:
        chart = alt.Chart(sdf).mark_bar().encode(
            x=alt.X("عدد:Q"),
            y=alt.Y("الحالة:N", sort="-x"),
            color=alt.Color("الحالة:N", scale=alt.Scale(domain=sdf["الحالة"].tolist(), range=sdf["لون"].tolist())),
            tooltip=["الحالة","عدد"]
        ).properties(height=260)
        st.altair_chart(chart, use_container_width=True)

    # ===== شارتين جنب بعض =====
    c1,c2 = st.columns(2)
    with c1:
        st.subheader("عدد المشاريع حسب البلدية")
        st.bar_chart(filtered["البلدية"].value_counts())
    with c2:
        st.subheader("قيمة العقود حسب الجهة")
        st.bar_chart(filtered.groupby("الجهة")["قيمة العقد"].sum())

    # ===== جدول تفصيلي =====
    st.markdown("---")
    st.subheader("تفاصيل المشاريع")
    cols = ["اسم المشروع","الجهة","البلدية","المقاول","حالة المشروع","تاريخ الانتهاء","قيمة العقد"]
    cols = [c for c in cols if c in filtered.columns]
    st.dataframe(filtered[cols], use_container_width=True)
