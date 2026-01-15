import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import timedelta
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
DATA_DIR.mkdir(exist_ok=True)

DATA_FILES = {
    "مشاريع الباب الثالث": "bab3.xlsx",
    "مشاريع الباب الرابع": "bab4.xlsx",
    "مشاريع بهجة": "bahja.xlsx",
    "مواقع المشاريع": "sites.xlsx",
    "الافتراضي": "data.xlsx"
}

# ================= CSS =================
st.markdown("""
<style>
html, body {direction: rtl; font-family: 'Segoe UI', sans-serif;}
h1 {text-align:center;}

.card {
    background:#fff;
    padding:18px;
    border-radius:18px;
    box-shadow:0 10px 28px rgba(0,0,0,0.08);
    text-align:center;
}
.card.blue {border-top:4px solid #2c7be5;}
.card.green {border-top:4px solid #00a389;}
.card.orange {border-top:4px solid #f4a261;}
.card.gray {border-top:4px solid #6c757d;}

.topbar-btn button {
    background:#1e5055 !important;
    color:#fff !important;
    border-radius:14px !important;
    border:1px solid rgba(255,255,255,0.3) !important;
}
</style>
""", unsafe_allow_html=True)

# ================= تحميل البيانات =================
def load_data():
    file = DATA_FILES.get(st.session_state.top_nav, "data.xlsx")
    path = DATA_DIR / file
    if not path.exists():
        return None

    df = pd.read_excel(path, engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]

    rename_map = {
        "إسم المشـــروع": "اسم المشروع",
        "قيمة المستخلصات المعتمده": "قيمة المستخلصات",
        "تاريخ الانتهاء من المشروع": "تاريخ الانتهاء",
        "نسبة الانجاز": "نسبة الانجاز"
    }
    df.rename(columns=rename_map, inplace=True)

    for c in ["قيمة العقد","قيمة المستخلصات","المستهدف","نسبة الانجاز","التكلفة"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    if "تاريخ الانتهاء" in df.columns:
        df["تاريخ الانتهاء"] = pd.to_datetime(df["تاريخ الانتهاء"], errors="coerce")

    return df

# ================= Top Navigation =================
st.title("لوحة المعلومات")

cols = st.columns(4)
for i, name in enumerate(DATA_FILES.keys()):
    if name == "الافتراضي":
        continue
    with cols[i % 4]:
        if st.button(name):
            st.session_state.top_nav = name
            st.rerun()

st.caption(f"📊 التحليل الحالي: {st.session_state.top_nav}")

df = load_data()
if df is None:
    st.warning("لا يوجد ملف لهذا القسم")
    st.stop()

# ================= تحليل خاص بمشاريع بهجة =================
if st.session_state.top_nav == "مشاريع بهجة":

    st.subheader("تحليل مشاريع بهجة")

    # ---------- فلاتر مترابطة ----------
    filtered = df.copy()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        mun = st.selectbox("البلدية", ["الكل"] + sorted(filtered["البلدية"].dropna().unique()))
        if mun != "الكل":
            filtered = filtered[filtered["البلدية"] == mun]

    with c2:
        project = st.selectbox("اسم المشروع", ["الكل"] + sorted(filtered["اسم المشروع"].dropna().unique()))
        if project != "الكل":
            filtered = filtered[filtered["اسم المشروع"] == project]

    with c3:
        ptype = st.selectbox("نوع المشروع", ["الكل"] + sorted(filtered["نوع المشروع"].dropna().unique()))
        if ptype != "الكل":
            filtered = filtered[filtered["نوع المشروع"] == ptype]

    with c4:
        approval = st.selectbox("حالة الاعتماد", ["الكل"] + sorted(filtered["حالة الاعتماد"].dropna().unique()))
        if approval != "الكل":
            filtered = filtered[filtered["حالة الاعتماد"] == approval]

    # ---------- كاردات ----------
    k1, k2, k3 = st.columns(3)

    k1.markdown(
        f"<div class='card blue'><h2>{len(filtered)}</h2>عدد المشاريع</div>",
        unsafe_allow_html=True
    )

    if "التكلفة" in filtered.columns:
        k2.markdown(
            f"<div class='card green'><h2>{filtered['التكلفة'].sum():,.0f}</h2>إجمالي التكلفة</div>",
            unsafe_allow_html=True
        )

    if "نسبة الانجاز" in filtered.columns:
        k3.markdown(
            f"<div class='card orange'><h2>{filtered['نسبة الانجاز'].mean():.1f}%</h2>نسبة الإنجاز</div>",
            unsafe_allow_html=True
        )

    # ---------- الخريطة ----------
    st.subheader("مواقع المشاريع")

    if all(col in filtered.columns for col in ["خط العرض", "خط الطول"]):
        map_df = filtered[["خط العرض", "خط الطول"]].dropna()
        map_df.columns = ["lat", "lon"]
        if not map_df.empty:
            st.map(map_df)
        else:
            st.info("لا توجد إحداثيات")
    else:
        st.warning("أعمدة خط الطول/العرض غير موجودة")

    # ---------- الشارتات ----------
    ch1, ch2 = st.columns(2)

    with ch1:
        st.subheader("حالة المشروع")
        st.bar_chart(filtered["حالة المشروع"].value_counts())

    with ch2:
        st.subheader("المستهدف مقابل الإنجاز")
        if all(col in filtered.columns for col in ["اسم المشروع", "نسبة الانجاز", "المستهدف"]):
            target_df = filtered[["اسم المشروع", "نسبة الانجاز", "المستهدف"]].set_index("اسم المشروع")
            st.bar_chart(target_df)
        else:
            st.warning("أعمدة المستهدف أو نسبة الإنجاز غير موجودة")

    # ---------- جدول ----------
    st.markdown("---")
    st.subheader("تفاصيل مشاريع بهجة")
    st.dataframe(filtered, use_container_width=True)

    st.stop()

# ================= الداشبورد العام =================
st.subheader("تفاصيل المشاريع")
st.dataframe(df, use_container_width=True)
