import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import timedelta
import base64
import altair as alt

# ================= إعدادات الصفحة =================
st.set_page_config(
    page_title="لوحة المعلومات | PMO",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= Session State =================
defaults = {
    "role": "viewer",
    "page": "home",
    "show_overdue": False,
    "show_risk": False,
    "top_nav": "الافتراضي"
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

DATA_DIR = Path("data")
ASSETS_DIR = Path("assets")
DATA_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

LOGO_PATH = ASSETS_DIR / "logo.png"

DATA_FILES = {
    "مشاريع الباب الثالث": "bab3.xlsx",
    "مشاريع الباب الرابع": "bab4.xlsx",
    "مشاريع بهجة": "bahja.xlsx",
    "الافتراضي": "data.xlsx"
}

# ================= CSS (نفس اللي عندك/خفيف) =================
st.markdown("""
<style>
html, body, [class*="css"] {
    direction: rtl;
    font-family: 'Segoe UI', sans-serif;
}
h1 { text-align:center; }

section[data-testid="stSidebar"] {
    background: #1e5055 !important;
}
section[data-testid="stSidebar"] * {
    color: #ffffff !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: #1e5055 !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #24666c !important;
}

.topbar-btn button{
    background-color: #1e5055 !important;
    color: #ffffff !important;
    border: 1.5px solid rgba(255,255,255,0.35) !important;
    min-width: 160px;
    height: 44px;
    padding: 8px 18px !important;
    border-radius: 14px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    white-space: nowrap !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    transition: all 0.25s ease-in-out;
}
.topbar-btn button:hover{
    background-color: #24666c !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.25) !important;
}
.topbar-btn.selected button{
    background-color: #163f43 !important;
    border: 2px solid #ffffff !important;
    box-shadow: 0 0 0 4px rgba(255,255,255,0.25) !important;
}

.card {
    background:#fff;
    padding:18px;
    border-radius:18px;
    box-shadow:0 10px 28px rgba(0,0,0,0.08);
    text-align:center;
    min-height: 120px;
    display:flex;
    flex-direction:column;
    justify-content:center;
}
.card h2 {
    font-size: 22px !important;
    font-weight: 700;
    margin: 0 0 6px 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.card.blue { border-top:4px solid #2c7be5; }
.card.green { border-top:4px solid #00a389; }
.card.orange { border-top:4px solid #f4a261; }
.card.gray { border-top:4px solid #6c757d; }
</style>
""", unsafe_allow_html=True)

# ================= أدوات =================
def load_data():
    file = DATA_FILES.get(st.session_state.top_nav, "data.xlsx")
    path = DATA_DIR / file
    if not path.exists():
        return None

    df = pd.read_excel(path, engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]

    df.rename(columns={
        "إسم المشـــروع": "اسم المشروع",
        "تاريخ الانتهاء من المشروع": "تاريخ الانتهاء",
        "تاريخ تسليم الموقع": "تاريخ التسليم",
        "قيمة المستخلصات المعتمده": "قيمة المستخلصات",
    }, inplace=True)

    # تواريخ
    for c in ["تاريخ الانتهاء", "تاريخ التسليم"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")

    # أرقام
    for c in ["قيمة العقد", "قيمة المستخلصات", "المتبقي من المستخلص", "نسبة الصرف", "نسبة الإنجاز"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df

def status_color(s):
    s = str(s)
    if any(k in s for k in ["متأخر","متعثر"]): return "#e63946"
    if any(k in s for k in ["مكتمل","منجز"]): return "#00a389"
    if any(k in s for k in ["جاري","قيد"]): return "#2c7be5"
    if any(k in s for k in ["متوقف"]): return "#6c757d"
    return "#f4a261"

def build_status_df(df):
    s = df["حالة المشروع"].fillna("غير محدد").astype(str)
    out = s.value_counts().rename_axis("الحالة").reset_index(name="عدد")
    out["لون"] = out["الحالة"].apply(status_color)
    return out

def require_cols(df, cols):
    missing = [c for c in cols if c not in df.columns]
    return missing

# ================= Sidebar =================
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(LOGO_PATH, width=120)

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
    st.title("تسجيل الدخول")
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if u == ADMIN_USER and p == ADMIN_PASS:
            st.session_state.role = "admin"
            st.session_state.page = "home"
            st.rerun()
        else:
            st.error("بيانات غير صحيحة")
    st.stop()

# ================= Upload =================
if st.session_state.page == "upload":
    st.title("رفع الملفات حسب نوع المشاريع")
    for name, file in DATA_FILES.items():
        if name == "الافتراضي":
            continue
        with st.expander(name):
            up = st.file_uploader(name, type=["xlsx"], key=file)
            if up:
                (DATA_DIR / file).write_bytes(up.getbuffer())
                st.success("تم رفع الملف")
    st.stop()

# ================= Home =================
st.title("لوحة المعلومات")

# ===== Top Buttons =====
items = list(DATA_FILES.keys())
items.remove("الافتراضي")

r1 = st.columns(3)
for i, name in enumerate(items[:3]):
    with r1[i]:
        active = "selected" if st.session_state.top_nav == name else ""
        st.markdown(f"<div class='topbar-btn {active}'>", unsafe_allow_html=True)
        if st.button(name, key=f"top_{name}"):
            st.session_state.top_nav = name
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

st.caption(f"📊 التحليل الحالي: {st.session_state.top_nav}")

df = load_data()
if df is None:
    st.warning("لا يوجد ملف لهذا القسم")
    st.stop()

# ======================================================================
# ✅ تحليل الباب الثالث (نفس بلوكك حرفيًا + حماية بسيطة للأعمدة فقط)
# ======================================================================
if st.session_state.top_nav in ["مشاريع الباب الثالث", "مشاريع الباب الرابع"]:

    # التأكد من الأعمدة المطلوبة (بدون تغيير الشكل)
    needed = [
        "اسم المشروع","حالة المشروع","نوع العقد","التصنيف","الجهة","البلدية",
        "قيمة العقد","قيمة المستخلصات","المتبقي من المستخلص","نسبة الإنجاز","تاريخ الانتهاء"
    ]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        st.warning(f"⚠️ أعمدة ناقصة في الملف: {missing}")
        # نكمّل التحليل قدر الإمكان بدل ما نوقف

    # ===== الفلاتر =====
    filtered = df.copy()
    f0,f1,f2 = st.columns(3)
    f3,f4,f5 = st.columns(3)

    with f0:
        if "اسم المشروع" in filtered.columns:
            project = st.selectbox("اسم المشروع", ["الكل"] + sorted(filtered["اسم المشروع"].dropna().unique()))
            if project != "الكل":
                filtered = filtered[filtered["اسم المشروع"] == project]

    with f1:
        if "حالة المشروع" in filtered.columns:
            status = st.selectbox("حالة المشروع", ["الكل"] + sorted(filtered["حالة المشروع"].dropna().unique()))
            if status != "الكل":
                filtered = filtered[filtered["حالة المشروع"] == status]

    with f2:
        if "نوع العقد" in filtered.columns:
            ctype = st.selectbox("نوع العقد", ["الكل"] + sorted(filtered["نوع العقد"].dropna().unique()))
            if ctype != "الكل":
                filtered = filtered[filtered["نوع العقد"] == ctype]

    with f3:
        if "التصنيف" in filtered.columns:
            cat = st.selectbox("التصنيف", ["الكل"] + sorted(filtered["التصنيف"].dropna().unique()))
            if cat != "الكل":
                filtered = filtered[filtered["التصنيف"] == cat]

    with f4:
        if "الجهة" in filtered.columns:
            ent = st.selectbox("الجهة الرسمية", ["الكل"] + sorted(filtered["الجهة"].dropna().unique()))
            if ent != "الكل":
                filtered = filtered[filtered["الجهة"] == ent]

    with f5:
        if "البلدية" in filtered.columns:
            mun = st.selectbox("البلدية", ["الكل"] + sorted(filtered["البلدية"].dropna().unique()))
            if mun != "الكل":
                filtered = filtered[filtered["البلدية"] == mun]

    # ===== KPI =====
    k1,k2,k3,k4,k5,k6 = st.columns(6)

    total_contract = filtered["قيمة العقد"].sum() if "قيمة العقد" in filtered.columns else 0
    total_claims = filtered["قيمة المستخلصات"].sum() if "قيمة المستخلصات" in filtered.columns else 0
    total_remain = filtered["المتبقي من المستخلص"].sum() if "المتبقي من المستخلص" in filtered.columns else 0
    spend_ratio = (total_claims / total_contract * 100) if total_contract and total_contract > 0 else 0

    progress_ratio = 0
    if "قيمة العقد" in filtered.columns and "نسبة الإنجاز" in filtered.columns:
        w = filtered.dropna(subset=["قيمة العقد","نسبة الإنجاز"])
        if not w.empty and w["قيمة العقد"].sum() > 0:
            progress_ratio = (w["قيمة العقد"] * w["نسبة الإنجاز"]).sum() / w["قيمة العقد"].sum()

    k1.markdown(f"<div class='card blue'><h2>{len(filtered)}</h2>عدد المشاريع</div>", unsafe_allow_html=True)
    k2.markdown(f"<div class='card green'><h2>{total_contract:,.0f}</h2>قيمة العقود</div>", unsafe_allow_html=True)
    k3.markdown(f"<div class='card gray'><h2>{total_claims:,.0f}</h2>المستخلصات</div>", unsafe_allow_html=True)
    k4.markdown(f"<div class='card orange'><h2>{total_remain:,.0f}</h2>المتبقي</div>", unsafe_allow_html=True)
    k5.markdown(f"<div class='card blue'><h2>{spend_ratio:.1f}%</h2>نسبة الصرف</div>", unsafe_allow_html=True)
    k6.markdown(f"<div class='card green'><h2>{progress_ratio:.1f}%</h2>نسبة الإنجاز</div>", unsafe_allow_html=True)

    # ===== حالة المشاريع =====
    st.subheader("حالة المشاريع")
    if "حالة المشروع" in filtered.columns:
        sdf = build_status_df(filtered)
        st.altair_chart(
            alt.Chart(sdf).mark_bar().encode(
                x="عدد",
                y=alt.Y("الحالة", sort="-x"),
                color=alt.Color("الحالة", scale=alt.Scale(domain=sdf["الحالة"], range=sdf["لون"]))
            ),
            use_container_width=True
        )

    # ===== الشارتين =====
    c1,c2 = st.columns(2)
    with c1:
        st.subheader("عدد المشاريع حسب البلدية")
        if "البلدية" in filtered.columns:
            st.bar_chart(filtered["البلدية"].value_counts())

    with c2:
        st.subheader("قيمة العقود حسب الجهة الرسمية")
        if "الجهة" in filtered.columns and "قيمة العقد" in filtered.columns:
            st.bar_chart(filtered.groupby("الجهة")["قيمة العقد"].sum())

    # ===== تنبيهات =====
    st.subheader("تنبيهات المشاريع")
    overdue = pd.DataFrame()
    if "حالة المشروع" in filtered.columns:
        overdue = filtered[filtered["حالة المشروع"].astype(str).str.contains("متأخر|متعثر", na=False)]

    risk = pd.DataFrame()
    if "تاريخ الانتهاء" in filtered.columns and "نسبة الإنجاز" in filtered.columns:
        risk = filtered[
            (filtered["تاريخ الانتهاء"] <= pd.Timestamp.today() + timedelta(days=30)) &
            (filtered["نسبة الإنجاز"] < 70)
        ]

    b1,b2 = st.columns(2)
    if b1.button(f"المشاريع المتأخرة ({len(overdue)})"):
        st.dataframe(overdue, use_container_width=True)
    if b2.button(f"المشاريع المتوقع تأخرها ({len(risk)})"):
        st.dataframe(risk.assign(سبب="قرب تاريخ الانتهاء مع انخفاض الإنجاز"), use_container_width=True)

    # ===== جدول =====
    st.markdown("---")
    st.subheader("تفاصيل المشاريع")
    st.dataframe(filtered, use_container_width=True)

    st.stop()

# ======================================================================
# أي قسم آخر (بهجة حالياً)
# ======================================================================
st.info("حاليًا التحليل التفصيلي مطبق على الباب الثالث/الرابع. إذا تبين بهجة بنفسه نضيفه بنفس البلوك.")
