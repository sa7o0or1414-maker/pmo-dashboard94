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
    "تطبيق دليل PMD": "pmd.xlsx",
    "المشاريع المنجزة": "done.xlsx",
    "مشاريع المحفظة": "portfolio.xlsx",
    "الدراسات وقوائم التحقق": "studies.xlsx",
    "دورة المشتريات": "procurement.xlsx",
    "مواقع المشاريع": "sites.xlsx",
    "مشاريع الإسكان": "housing.xlsx",
    "الافتراضي": "data.xlsx"
}

# ================= CSS =================
st.markdown("""
<style>
/* ===== Sidebar ===== */
section[data-testid="stSidebar"] {
    background: #1e5055 !important;
}

section[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

/* أزرار السايدبار */
section[data-testid="stSidebar"] .stButton > button {
    background: #1e5055 !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: #24666c !important;
}

/* ===== Top Bar Buttons ===== */
.topbar-btn button {
    background: #1e5055 !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.35) !important;
}

/* Hover */
.topbar-btn button:hover {
    background: #24666c !important;
    color: #ffffff !important;
}

/* الزر المختار */
.topbar-btn.selected button {
    background: #163f43 !important;
    color: #ffffff !important;
    border: 2px solid #ffffff !important;
    box-shadow: 0 0 0 3px rgba(255,255,255,0.25) !important;
}
</style>

<style>
/* ===== Top Navigation Buttons ===== */
.topbar-btn button {
    min-width: 160px;
    height: 44px;
    padding: 8px 18px !important;
    border-radius: 14px !important;
    background: #ffffff !important;
    border: 1.5px solid #d0d7de !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #153e46 !important;
    white-space: nowrap !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
    transition: all 0.25s ease-in-out;
}

/* Hover */
.topbar-btn button:hover {
    border-color: #2c7be5 !important;
    background: #f5f9ff !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(44,123,229,0.15) !important;
}

/* الزر المختار */
.topbar-btn button:focus,
.topbar-btn button:active {
    border: 2px solid #ff8c82 !important;
    background: #fff5f4 !important;
    color: #b42318 !important;
    box-shadow: 0 0 0 4px rgba(255,140,130,0.25) !important;
}

/* ترتيب الصفوف */
[data-testid="column"] {
    display: flex;
    justify-content: center;
}
</style>

<style>
/* ===== تحسين تنسيق الكاردات ===== */
.card {
    min-height: 140px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

/* الرقم داخل الكارد */
.card h2 {
    font-size: 22px !important;
    font-weight: 700;
    margin-bottom: 6px;
    white-space: nowrap;        /* يمنع النزول لسطر */
    overflow: hidden;
    text-overflow: ellipsis;
}

/* النص أسفل الرقم */
.card div,
.card span,
.card p {
    font-size: 13px;
    line-height: 1.4;
    white-space: nowrap;
}

/* معالجة الأرقام الكبيرة (ملايين) */
.card h2 {
    letter-spacing: -0.5px;
}

/* توحيد ارتفاع الصف */
[data-testid="column"] > div {
    height: 100%;
}
</style>

<style>
html, body, [class*="css"] {
    direction: rtl;
    font-family: 'Segoe UI', sans-serif;
}
h1 { text-align:center; }

.card {
    background:#fff;
    padding:18px;
    border-radius:18px;
    box-shadow:0 10px 28px rgba(0,0,0,0.08);
    text-align:center;
}
.card.blue { border-top:4px solid #2c7be5; }
.card.green { border-top:4px solid #00a389; }
.card.orange { border-top:4px solid #f4a261; }
.card.gray { border-top:4px solid #6c757d; }
</style>
<style>
/* ===== Top Navigation Buttons (بنفس لون البار) ===== */
.topbar-btn button {
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

/* Hover */
.topbar-btn button:hover {
    background-color: #24666c !important;
    color: #ffffff !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.25) !important;
}

/* الزر المختار */
.topbar-btn button:focus,
.topbar-btn button:active {
    background-color: #163f43 !important;
    color: #ffffff !important;
    border: 2px solid #ffffff !important;
    box-shadow: 0 0 0 4px rgba(255,255,255,0.25) !important;
}
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
        "قيمة المستخلصات المعتمده": "قيمة المستخلصات",
        "تاريخ الانتهاء من المشروع": "تاريخ الانتهاء",
    }, inplace=True)

    for c in ["قيمة العقد","قيمة المستخلصات","نسبة الانجاز"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    if "تاريخ الانتهاء" in df.columns:
        df["تاريخ الانتهاء"] = pd.to_datetime(df["تاريخ الانتهاء"], errors="coerce")

    return df

def status_color(s):
    s = str(s)
    if "متأخر" in s or "متعثر" in s: return "#e63946"
    if "مكتمل" in s or "منجز" in s: return "#00a389"
    if "جاري" in s or "قيد" in s: return "#2c7be5"
    return "#f4a261"

def build_status_df(df):
    s = df["حالة المشروع"].fillna("غير محدد").astype(str)
    out = s.value_counts().rename_axis("الحالة").reset_index(name="عدد")
    out["لون"] = out["الحالة"].apply(status_color)
    return out

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

    # ---------- فلاتر ----------
    f1, f2, f3, f4 = st.columns(4)

    with f1:
        mun = st.selectbox(
            "البلدية",
            ["الكل"] + sorted(df["البلدية"].dropna().unique())
        )

    with f2:
        project = st.selectbox(
            "اسم المشروع",
            ["الكل"] + sorted(df["اسم المشروع"].dropna().unique())
        )

    with f3:
        ptype = st.selectbox(
            "نوع المشروع",
            ["الكل"] + sorted(df["نوع المشروع"].dropna().unique())
        )

    with f4:
        approval = st.selectbox(
            "حالة الاعتماد",
            ["الكل"] + sorted(df["حالة الاعتماد"].dropna().unique())
        )

    filtered = df.copy()

    if mun != "الكل":
        filtered = filtered[filtered["البلدية"] == mun]

    if project != "الكل":
        filtered = filtered[filtered["اسم المشروع"] == project]

    if ptype != "الكل":
        filtered = filtered[filtered["نوع المشروع"] == ptype]

    if approval != "الكل":
        filtered = filtered[filtered["حالة الاعتماد"] == approval]

    # ---------- كاردات ----------
    c1, c2, c3 = st.columns(3)

    total_cost = filtered["التكلفة"].sum()
# دعم الاسمين: نسبة الإنجاز / نسبة الانجاز
progress_col = None
if "نسبة الانجاز" in filtered.columns:
    progress_col = "نسبة الإنجاز"
elif "نسبة الانجاز" in filtered.columns:
    progress_col = "نسبة الانجاز"

avg_progress = 0
if progress_col:
    avg_progress = pd.to_numeric(filtered[progress_col], errors="coerce").mean()

    projects_count = len(filtered)

    c1.markdown(
        f"<div class='card blue'><h2>{projects_count}</h2>عدد المشاريع</div>",
        unsafe_allow_html=True
    )

    c2.markdown(
        f"<div class='card green'><h2>{total_cost:,.0f}</h2>إجمالي التكلفة</div>",
        unsafe_allow_html=True
    )

    c3.markdown(
        f"<div class='card orange'><h2>{avg_progress:.1f}%</h2>نسبة الإنجاز</div>",
        unsafe_allow_html=True
    )

      # ---------- كارد المشاريع المكتملة ----------
    completed_projects = 0
if progress_col:
    completed_projects = (
        pd.to_numeric(filtered[progress_col], errors="coerce") >= 100
    ).sum()


    # دعم الاسمين: نسبة الإنجاز / نسبة الانجاز
    progress_col = None
    if "نسبة الإنجاز" in filtered.columns:
        progress_col = "نسبة الإنجاز"
    elif "نسبة الانجاز" in filtered.columns:
        progress_col = "نسبة الانجاز"

    if progress_col:
        completed_projects = filtered[
            pd.to_numeric(filtered[progress_col], errors="coerce") >= 100
        ].shape[0]

    st.markdown(
        f"""
        <div class="card green">
            <h2>{completed_projects}</h2>
            المشاريع المكتملة
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------- الشارتات ----------
    ch1, ch2 = st.columns(2)

    with ch1:
        st.subheader("حالة المشروع")
        st.bar_chart(filtered["حالة المشروع"].value_counts())

    with ch2:
        st.subheader("المستهدف")
        st.bar_chart(filtered["المستهدف"].value_counts())

    # ---------- جدول ----------
    st.markdown("---")
    st.subheader("تفاصيل مشاريع بهجة")
    st.dataframe(filtered, use_container_width=True)

    st.stop()  # ⛔ يمنع تنفيذ بقية الداشبورد العام

# ================= الفلاتر (مُعادة كما طلبت) =================
filtered = df.copy()

f1,f2,f3,f4,f5 = st.columns(5)

with f1:
    if "التصنيف" in filtered.columns:
        cat = st.selectbox("التصنيف", ["الكل"] + sorted(filtered["التصنيف"].dropna().unique()))
        if cat != "الكل":
            filtered = filtered[filtered["التصنيف"] == cat]

with f2:
    if "الجهة" in filtered.columns:
        ent = st.selectbox("الجهة", ["الكل"] + sorted(filtered["الجهة"].dropna().unique()))
        if ent != "الكل":
            filtered = filtered[filtered["الجهة"] == ent]

with f3:
    if "البلدية" in filtered.columns:
        mun = st.selectbox("البلدية", ["الكل"] + sorted(filtered["البلدية"].dropna().unique()))
        if mun != "الكل":
            filtered = filtered[filtered["البلدية"] == mun]

with f4:
    if "حالة المشروع" in filtered.columns:
        stt = st.selectbox("حالة المشروع", ["الكل"] + sorted(filtered["حالة المشروع"].dropna().unique()))
        if stt != "الكل":
            filtered = filtered[filtered["حالة المشروع"] == stt]

with f5:
    if "نوع العقد" in filtered.columns:
        ct = st.selectbox("نوع العقد", ["الكل"] + sorted(filtered["نوع العقد"].dropna().unique()))
        if ct != "الكل":
            filtered = filtered[filtered["نوع العقد"] == ct]

# ================= KPI (محدثة) =================
k1,k2,k3,k4,k5,k6,k7 = st.columns(7)

# عدد المشاريع
projects_count = len(filtered)

# عدد العقود (رقم العقد عدّ)
contracts_count = (
    filtered["رقم العقد"].nunique()
    if "رقم العقد" in filtered.columns
    else 0
)

# القيم المالية
total_contract = filtered["قيمة العقد"].sum(skipna=True) if "قيمة العقد" in filtered.columns else 0
total_claims = filtered["قيمة المستخلصات"].sum(skipna=True) if "قيمة المستخلصات" in filtered.columns else 0
total_remain = filtered["المتبقي من المستخلص"].sum(skipna=True) if "المتبقي من المستخلص" in filtered.columns else 0

# نسبة الصرف
spend_ratio = (total_claims / total_contract * 100) if total_contract > 0 else 0

# نسبة الإنجاز (مرجّحة بقيمة العقد)
progress_ratio = 0
if "قيمة العقد" in filtered.columns and "نسبة الإنجاز" in filtered.columns:
    w = filtered.dropna(subset=["قيمة العقد","نسبة الإنجاز"])
    if not w.empty and w["قيمة العقد"].sum() > 0:
        progress_ratio = (w["قيمة العقد"] * w["نسبة الإنجاز"]).sum() / w["قيمة العقد"].sum()

# ===== عرض الكاردات =====
k1.markdown(f"<div class='card blue'><h2>{projects_count}</h2>عدد المشاريع</div>", unsafe_allow_html=True)

k2.markdown(f"<div class='card gray'><h2>{contracts_count}</h2>عدد العقود</div>", unsafe_allow_html=True)

k3.markdown(f"<div class='card green'><h2>{total_contract:,.0f}</h2>قيمة العقود</div>", unsafe_allow_html=True)

k4.markdown(f"<div class='card blue'><h2>{total_claims:,.0f}</h2>قيمة المستخلصات المعتمدة</div>", unsafe_allow_html=True)

k5.markdown(f"<div class='card orange'><h2>{total_remain:,.0f}</h2>المتبقي من المستخلص</div>", unsafe_allow_html=True)

k6.markdown(f"<div class='card gray'><h2>{spend_ratio:.1f}%</h2>نسبة الصرف</div>", unsafe_allow_html=True)

k7.markdown(f"<div class='card green'><h2>{progress_ratio:.1f}%</h2>نسبة الإنجاز</div>", unsafe_allow_html=True)

# ================= حالة المشاريع =================
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

# ================= الشارتين =================
c1,c2 = st.columns(2)
with c1:
    st.subheader("عدد المشاريع حسب البلدية")
    st.bar_chart(filtered["البلدية"].value_counts())

with c2:
    st.subheader("عدد المشاريع حسب حالة المشروع")
    st.bar_chart(filtered["حالة المشروع"].value_counts())

# ================= التنبيهات =================
st.subheader("تنبيهات المشاريع")
overdue = filtered[filtered["حالة المشروع"].astype(str).str.contains("متأخر|متعثر", na=False)]
risk = filtered[
    (filtered["تاريخ الانتهاء"] <= pd.Timestamp.today() + timedelta(days=30)) &
    (filtered["نسبة الإنجاز"] < 70)
]

b1,b2 = st.columns(2)
if b1.button(f"المشاريع المتأخرة ({len(overdue)})"):
    st.session_state.show_overdue = not st.session_state.show_overdue
if b2.button(f"المشاريع المتوقع تأخرها ({len(risk)})"):
    st.session_state.show_risk = not st.session_state.show_risk

if st.session_state.show_overdue:
    st.dataframe(overdue, use_container_width=True)
if st.session_state.show_risk:
    st.dataframe(risk, use_container_width=True)

# ================= جدول =================
st.markdown("---")
st.subheader("تفاصيل المشاريع")
st.dataframe(filtered, use_container_width=True)
