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
        "تاريخ الانتهاء من المشروع": "تاريخ الانتهاء"
    }
    df.rename(columns=rename_map, inplace=True)

    for c in ["قيمة العقد", "قيمة المستخلصات", "نسبة الإنجاز", "نسبة الانجاز"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    if "تاريخ الانتهاء" in df.columns:
        df["تاريخ الانتهاء"] = pd.to_datetime(df["تاريخ الانتهاء"], errors="coerce")

    return df

# ================= ألوان الحالة =================
def status_color(s):
    s = str(s)
    if "متأخر" in s or "متعثر" in s:
        return "#e63946"
    if "مكتمل" in s or "منجز" in s:
        return "#00a389"
    if "جاري" in s or "قيد" in s:
        return "#2c7be5"
    return "#f4a261"

def build_status_df(df):
    if "حالة المشروع" not in df.columns:
        return pd.DataFrame(columns=["الحالة", "عدد", "لون"])
    s = df["حالة المشروع"].fillna("غير محدد").astype(str)
    out = s.value_counts().rename_axis("الحالة").reset_index(name="عدد")
    out["لون"] = out["الحالة"].apply(status_color)
    return out

# ================= Sidebar =================
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(LOGO_PATH, width=120)

    if st.button("الصفحة الرئيسية"):
        st.session_state.top_nav = "الافتراضي"

# ================= الصفحة الرئيسية =================
st.title("لوحة المعلومات")

# ===== أزرار الأقسام =====
cols = st.columns(3)
items = list(DATA_FILES.keys())
items.remove("الافتراضي")

for i, name in enumerate(items):
    with cols[i % 3]:
        if st.button(name):
            st.session_state.top_nav = name
            st.rerun()

st.caption(f"📊 التحليل الحالي: {st.session_state.top_nav}")

df = load_data()
if df is None or df.empty:
    st.warning("لا يوجد ملف لهذا القسم")
    st.stop()

# ================= الفلاتر =================
filtered = df.copy()

filters = st.columns(5)

def dropdown(col, label):
    if label in filtered.columns:
        val = st.selectbox(label, ["الكل"] + sorted(filtered[label].dropna().unique()))
        if val != "الكل":
            return filtered[filtered[label] == val]
    return filtered

with filters[0]:
    filtered = dropdown("التصنيف", "التصنيف")
with filters[1]:
    filtered = dropdown("الجهة", "الجهة")
with filters[2]:
    filtered = dropdown("البلدية", "البلدية")
with filters[3]:
    filtered = dropdown("حالة المشروع", "حالة المشروع")
with filters[4]:
    filtered = dropdown("نوع العقد", "نوع العقد")

# ================= KPI =================
k1,k2,k3,k4,k5,k6,k7 = st.columns(7)

projects_count = len(filtered)

contracts_count = filtered["رقم العقد"].nunique() if "رقم العقد" in filtered.columns else 0

total_contract = filtered["قيمة العقد"].sum() if "قيمة العقد" in filtered.columns else 0
total_claims = filtered["قيمة المستخلصات"].sum() if "قيمة المستخلصات" in filtered.columns else 0
total_remain = filtered["المتبقي من المستخلص"].sum() if "المتبقي من المستخلص" in filtered.columns else 0

spend_ratio = (total_claims / total_contract * 100) if total_contract > 0 else 0

progress_col = "نسبة الإنجاز" if "نسبة الإنجاز" in filtered.columns else "نسبة الانجاز" if "نسبة الانجاز" in filtered.columns else None
progress_ratio = filtered[progress_col].mean() if progress_col else 0

k1.metric("عدد المشاريع", projects_count)
k2.metric("عدد العقود", contracts_count)
k3.metric("قيمة العقود", f"{total_contract:,.0f}")
k4.metric("قيمة المستخلصات", f"{total_claims:,.0f}")
k5.metric("المتبقي", f"{total_remain:,.0f}")
k6.metric("نسبة الصرف", f"{spend_ratio:.1f}%")
k7.metric("نسبة الإنجاز", f"{progress_ratio:.1f}%")

# ================= حالة المشاريع =================
st.subheader("حالة المشاريع")
sdf = build_status_df(filtered)
if not sdf.empty:
    st.altair_chart(
        alt.Chart(sdf).mark_bar().encode(
            x="عدد",
            y=alt.Y("الحالة", sort="-x"),
            color=alt.Color("الحالة", scale=alt.Scale(domain=sdf["الحالة"], range=sdf["لون"]))
        ),
        use_container_width=True
    )

# ================= الشارتين =================
c1, c2 = st.columns(2)

with c1:
    if "البلدية" in filtered.columns:
        st.subheader("عدد المشاريع حسب البلدية")
        st.bar_chart(filtered["البلدية"].value_counts())

with c2:
    if "حالة المشروع" in filtered.columns:
        st.subheader("عدد المشاريع حسب حالة المشروع")
        st.bar_chart(filtered["حالة المشروع"].value_counts())

# ================= التنبيهات =================
st.subheader("تنبيهات المشاريع")

overdue = filtered[filtered["حالة المشروع"].astype(str).str.contains("متأخر|متعثر", na=False)] if "حالة المشروع" in filtered.columns else pd.DataFrame()

risk = pd.DataFrame()
if progress_col and "تاريخ الانتهاء" in filtered.columns:
    risk = filtered[
        (filtered["تاريخ الانتهاء"] <= pd.Timestamp.today() + timedelta(days=30)) &
        (filtered[progress_col] < 70)
    ]

b1,b2 = st.columns(2)
if b1.button(f"المشاريع المتأخرة ({len(overdue)})"):
    st.session_state.show_overdue = not st.session_state.show_overdue
if b2.button(f"المشاريع المتوقع تأخرها ({len(risk)})"):
    st.session_state.show_risk = not st.session_state.show_risk

if st.session_state.show_overdue and not overdue.empty:
    st.dataframe(overdue, use_container_width=True)
if st.session_state.show_risk and not risk.empty:
    st.dataframe(risk, use_container_width=True)

# ================= جدول =================
st.markdown("---")
st.subheader("تفاصيل المشاريع")
st.dataframe(filtered, use_container_width=True)
