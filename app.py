import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import timedelta
import base64
import altair as alt

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

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

DATA_DIR = Path("data")
ASSETS_DIR = Path("assets")
DATA_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

EXCEL_PATH = DATA_DIR / "data.xlsx"
LOGO_PATH = ASSETS_DIR / "logo.png"

# ================= CSS (معدل للبار فقط) =================
st.markdown("""
<style>
html, body, [class*="css"] {
    direction: rtl;
    font-family: 'Segoe UI', sans-serif;
    color: #153e46;
}

/* ===== Sidebar ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f2d33, #153e46);
    padding-top: 30px;
}
section[data-testid="stSidebar"] * {
    color: white !important;
    text-align: center;
}

/* زر متوازن مع النص */
section[data-testid="stSidebar"] .stButton {
    display: flex;
    justify-content: center;
}

section[data-testid="stSidebar"] .stButton > button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 10px 26px;
    margin: 10px 0;
    background: rgba(255,255,255,0.18);
    border-radius: 20px;
    border: none;
    font-size: 14px;
    white-space: nowrap;
    box-shadow: 0 6px 16px rgba(0,0,0,0.25);
    width: auto;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.28);
    transform: translateY(-1px);
}

/* ===== Cards ===== */
.card {
    background: #fff;
    padding: 18px;
    border-radius: 18px;
    box-shadow: 0 10px 28px rgba(0,0,0,0.08);
    text-align: center;
}
.card h2 { font-size: 20px; margin: 0; }
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

def status_color(s):
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

# ================= Sidebar =================
with st.sidebar:
    if LOGO_PATH.exists():
        st.markdown(
            f"<img src='data:image/png;base64,{img64(LOGO_PATH)}' width='120' style='margin-bottom:25px;'>",
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

r1 = st.columns(5)
for i, name in enumerate(items[:5]):
    with r1[i]:
        active = "selected" if st.session_state.top_nav == name else ""
        st.markdown(f"<div class='topbar-btn {active}'>", unsafe_allow_html=True)
        if st.button(name, key=f"top_{name}"):
            st.session_state.top_nav = name
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

r2 = st.columns(5)
for i, name in enumerate(items[5:]):
    with r2[i]:
        active = "selected" if st.session_state.top_nav == name else ""
        st.markdown(f"<div class='topbar-btn {active}'>", unsafe_allow_html=True)
        if st.button(name, key=f"top2_{name}"):
            st.session_state.top_nav = name
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


st.caption(f"📊 التحليل الحالي: {st.session_state.top_nav}")

df = load_data()
if df is None:
    st.warning("لا يوجد ملف لهذا القسم")
    st.stop()
# ================= تحليل خاص بمشاريع بهجة =================
if st.session_state.top_nav == "مشاريع بهجة":

    st.subheader("تحليل مشاريع بهجة")



# ================= Home =================
if st.session_state.page == "home":
    st.title("لوحة التحكم")

    df = load_data()
    if df is None:
        st.warning("يرجى رفع ملف Excel")
        st.stop()

    # ===== الفلاتر =====
    filtered = df.copy()
    f0,f1,f2 = st.columns(3)
    f3,f4,f5 = st.columns(3)

    with f0:
        project = st.selectbox("اسم المشروع", ["الكل"] + sorted(filtered["اسم المشروع"].dropna().unique()))
        if project != "الكل":
            filtered = filtered[filtered["اسم المشروع"] == project]

    with f1:
        status = st.selectbox("حالة المشروع", ["الكل"] + sorted(filtered["حالة المشروع"].dropna().unique()))
        if status != "الكل":
            filtered = filtered[filtered["حالة المشروع"] == status]

    with f2:
        ctype = st.selectbox("نوع العقد", ["الكل"] + sorted(filtered["نوع العقد"].dropna().unique()))
        if ctype != "الكل":
            filtered = filtered[filtered["نوع العقد"] == ctype]

    with f3:
        cat = st.selectbox("التصنيف", ["الكل"] + sorted(filtered["التصنيف"].dropna().unique()))
        if cat != "الكل":
            filtered = filtered[filtered["التصنيف"] == cat]

    with f4:
        ent = st.selectbox("الجهة الرسمية", ["الكل"] + sorted(filtered["الجهة"].dropna().unique()))
        if ent != "الكل":
            filtered = filtered[filtered["الجهة"] == ent]

    with f5:
        mun = st.selectbox("البلدية", ["الكل"] + sorted(filtered["البلدية"].dropna().unique()))
        if mun != "الكل":
            filtered = filtered[filtered["البلدية"] == mun]

    # ===== KPI =====
    k1,k2,k3,k4,k5,k6 = st.columns(6)

    total_contract = filtered["قيمة العقد"].sum()
    total_claims = filtered["قيمة المستخلصات"].sum()
    total_remain = filtered["المتبقي من المستخلص"].sum()
    spend_ratio = (total_claims / total_contract * 100) if total_contract > 0 else 0

    progress_ratio = 0
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
        st.bar_chart(filtered["البلدية"].value_counts())

    with c2:
        st.subheader("قيمة العقود حسب الجهة الرسمية")
        st.bar_chart(filtered.groupby("الجهة")["قيمة العقد"].sum())

    # ===== تنبيهات =====
    st.subheader("تنبيهات المشاريع")
    overdue = filtered[filtered["حالة المشروع"].astype(str).str.contains("متأخر|متعثر")]
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
