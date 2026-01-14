import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import timedelta
import base64

# Altair غالباً موجود مع Streamlit
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
/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f2d33, #153e46);
    display: flex;
    flex-direction: column;
}

/* محتوى البار كامل */
section[data-testid="stSidebar"] > div {
    display: flex;
    flex-direction: column;
    justify-content: center;   /* 👈 هذا اللي يوسّط عموديًا */
    align-items: center;       /* 👈 توسيط أفقي */
    height: 100vh;
}

/* اللوقو */
.sidebar-logo {
    margin-bottom: 30px;
}

/* الأزرار */
section[data-testid="stSidebar"] .stButton {
    display: flex;
    justify-content: center;
}

section[data-testid="stSidebar"] .stButton > button {
    padding: 10px 26px;
    margin: 12px 0;
    background: rgba(255,255,255,0.14);
    border-radius: 18px;
    border: none;
    font-size: 14px;
    white-space: nowrap;
    box-shadow: 0 6px 18px rgba(0,0,0,0.18);
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.25);
    transform: scale(1.03);
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

    # تواريخ
    if "تاريخ الانتهاء" in df.columns:
        df["تاريخ الانتهاء"] = pd.to_datetime(df["تاريخ الانتهاء"], errors="coerce")
    if "تاريخ التسليم" in df.columns:
        df["تاريخ التسليم"] = pd.to_datetime(df["تاريخ التسليم"], errors="coerce")

    # أرقام
    for c in ["قيمة العقد", "قيمة المستخلصات", "المتبقي من المستخلص", "نسبة الصرف", "نسبة الإنجاز"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df

def status_color(status_text: str) -> str:
    """تلوين ذكي حسب الكلمات داخل الحالة (يدعم أي تسميات جديدة)"""
    s = (status_text or "").strip()

    # أحمر: تأخر/تعثر
    if any(k in s for k in ["متأخر", "تأخر", "متعثر", "تعثّر", "متعثّر", "حرج", "خطير"]):
        return "#e63946"

    # أخضر: مكتمل/منجز/مستلم
    if any(k in s for k in ["مكتمل", "منجز", "مستلم", "تم الاستلام", "مغلق", "إغلاق"]):
        return "#00a389"

    # أزرق: جاري/قيد التنفيذ/تحت
    if any(k in s for k in ["جاري", "قيد", "تحت", "تنفيذ", "الاستلام", "استلام"]):
        return "#2c7be5"

    # رمادي: متوقف
    if any(k in s for k in ["متوقف", "موقوف", "إيقاف", "مجمّد", "مجمد"]):
        return "#6c757d"

    # برتقالي: افتراضي/غير محدد
    if s == "" or any(k in s for k in ["غير", "بدون", "محدد", "غير محدد"]):
        return "#f4a261"

    return "#f4a261"

def build_status_df(filtered: pd.DataFrame) -> pd.DataFrame:
    s = filtered.get("حالة المشروع")
    if s is None:
        return pd.DataFrame({"الحالة": ["غير محدد"], "عدد": [0], "لون": ["#f4a261"]})

    counts = s.fillna("غير محدد").astype(str).value_counts()
    df_status = counts.rename_axis("الحالة").reset_index(name="عدد")
    df_status["لون"] = df_status["الحالة"].apply(status_color)
    return df_status

# ================= Sidebar =================
with st.sidebar:
    # اللوقو فقط بدون نصوص
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
    st.session_state.logo_align = st.selectbox("محاذاة اللوقو", ["center", "right", "left"])

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
        st.warning("يرجى رفع ملف Excel من صفحة رفع البيانات")
        st.stop()

    # ===== Filters =====
    f1,f2,f3 = st.columns(3)
    f4,f5 = st.columns(2)

    with f1:
        cat = st.selectbox("التصنيف", ["الكل"] + sorted(df["التصنيف"].dropna().unique())) if "التصنيف" in df.columns else "الكل"
    with f2:
        ent = st.selectbox("الجهة", ["الكل"] + sorted(df["الجهة"].dropna().unique())) if "الجهة" in df.columns else "الكل"
    with f3:
        mun = st.selectbox("البلدية", ["الكل"] + sorted(df["البلدية"].dropna().unique())) if "البلدية" in df.columns else "الكل"
    with f4:
        status = st.selectbox("حالة المشروع", ["الكل"] + sorted(df["حالة المشروع"].dropna().unique())) if "حالة المشروع" in df.columns else "الكل"
    with f5:
        ctype = st.selectbox("نوع العقد", ["الكل"] + sorted(df["نوع العقد"].dropna().unique())) if "نوع العقد" in df.columns else "الكل"

    filtered = df.copy()
    if "التصنيف" in filtered.columns and cat!="الكل": filtered = filtered[filtered["التصنيف"]==cat]
    if "الجهة" in filtered.columns and ent!="الكل": filtered = filtered[filtered["الجهة"]==ent]
    if "البلدية" in filtered.columns and mun!="الكل": filtered = filtered[filtered["البلدية"]==mun]
    if "حالة المشروع" in filtered.columns and status!="الكل": filtered = filtered[filtered["حالة المشروع"]==status]
    if "نوع العقد" in filtered.columns and ctype!="الكل": filtered = filtered[filtered["نوع العقد"]==ctype]

    # ===== KPI =====
    k1,k2,k3,k4,k5,k6 = st.columns(6)

    k1.markdown(f"<div class='card blue'><h2>{len(filtered)}</h2>عدد المشاريع</div>", unsafe_allow_html=True)

    v_contract = filtered["قيمة العقد"].sum(skipna=True) if "قيمة العقد" in filtered.columns else 0
    v_claims = filtered["قيمة المستخلصات"].sum(skipna=True) if "قيمة المستخلصات" in filtered.columns else 0
    v_remain = filtered["المتبقي من المستخلص"].sum(skipna=True) if "المتبقي من المستخلص" in filtered.columns else 0
    avg_spend = filtered["نسبة الصرف"].mean(skipna=True) if "نسبة الصرف" in filtered.columns else 0
    avg_prog = filtered["نسبة الإنجاز"].mean(skipna=True) if "نسبة الإنجاز" in filtered.columns else 0

    k2.markdown(f"<div class='card green'><h2>{v_contract:,.0f}</h2>قيمة العقود</div>", unsafe_allow_html=True)
    k3.markdown(f"<div class='card gray'><h2>{v_claims:,.0f}</h2>المستخلصات</div>", unsafe_allow_html=True)
    k4.markdown(f"<div class='card orange'><h2>{v_remain:,.0f}</h2>المتبقي</div>", unsafe_allow_html=True)
    k5.markdown(f"<div class='card blue'><h2>{(avg_spend or 0):.1f}%</h2>متوسط الصرف</div>", unsafe_allow_html=True)
    k6.markdown(f"<div class='card green'><h2>{(avg_prog or 0):.1f}%</h2>متوسط الإنجاز</div>", unsafe_allow_html=True)

    # ===== حالة المشاريع (أفقي + كل الحالات ملونة) =====
    st.subheader("حالة المشاريع")
    status_df = build_status_df(filtered)

    if ALTAIR_OK:
        # Domain & Range من البيانات نفسها لضمان تلون كل حالة
        domain = status_df["الحالة"].tolist()
        range_colors = status_df["لون"].tolist()

        chart = alt.Chart(status_df).mark_bar().encode(
            x=alt.X("عدد:Q", title=""),
            y=alt.Y("الحالة:N", sort="-x", title=""),
            color=alt.Color(
                "الحالة:N",
                scale=alt.Scale(domain=domain, range=range_colors),
                legend=alt.Legend(title="")
            ),
            tooltip=["الحالة:N", "عدد:Q"]
        ).properties(height=260)
        st.altair_chart(chart, use_container_width=True)
    else:
        # fallback
        st.bar_chart(status_df.set_index("الحالة")[["عدد"]], use_container_width=True)

    # ===== شارتين جنب بعض =====
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("عدد المشاريع حسب البلدية")
        if "البلدية" in filtered.columns:
            st.bar_chart(filtered["البلدية"].value_counts(), use_container_width=True)
        else:
            st.info("عمود البلدية غير موجود في الملف")

    with c2:
        st.subheader("قيمة العقود حسب الجهة")
        if "الجهة" in filtered.columns and "قيمة العقد" in filtered.columns:
            st.bar_chart(filtered.groupby("الجهة")["قيمة العقد"].sum(), use_container_width=True)
        else:
            st.info("تأكد من وجود أعمدة الجهة + قيمة العقد")

    # ===== أيقونات التأخير =====
    today = pd.Timestamp.today()

    overdue = pd.DataFrame()
    if "تاريخ الانتهاء" in filtered.columns and "حالة المشروع" in filtered.columns:
        overdue = filtered[
            (filtered["تاريخ الانتهاء"] < today) &
            (~filtered["حالة المشروع"].astype(str).isin(["مكتمل", "منجز"]))
        ]

    risk = pd.DataFrame()
    if "تاريخ الانتهاء" in filtered.columns and "نسبة الإنجاز" in filtered.columns:
        risk = filtered[
            (filtered["تاريخ الانتهاء"] <= today + timedelta(days=30)) &
            (pd.to_numeric(filtered["نسبة الإنجاز"], errors="coerce") < 70)
        ].copy()
        if not risk.empty:
            risk["سبب التوقع"] = "قرب تاريخ الانتهاء مع انخفاض نسبة الإنجاز"

    b1, b2 = st.columns(2)
    if b1.button(f"المشاريع المتأخرة ({len(overdue)})"):
        st.session_state.show_overdue = not st.session_state.show_overdue
    if b2.button(f"المشاريع المتوقع تأخرها ({len(risk)})"):
        st.session_state.show_risk = not st.session_state.show_risk

    if st.session_state.show_overdue and not overdue.empty:
        cols = [c for c in ["اسم المشروع","المقاول","رقم العقد","تاريخ الانتهاء","حالة المشروع"] if c in overdue.columns]
        st.dataframe(overdue[cols], use_container_width=True)

    if st.session_state.show_risk and not risk.empty:
        cols = [c for c in ["اسم المشروع","المقاول","رقم العقد","تاريخ الانتهاء","سبب التوقع"] if c in risk.columns]
        st.dataframe(risk[cols], use_container_width=True)

    # ===== جدول تفصيلي (يعكس الفلاتر) =====
    st.markdown("---")
    st.subheader("تفاصيل المشاريع")
    cols = [
        "اسم المشروع","الجهة","البلدية","المقاول","حالة المشروع",
        "تاريخ التسليم","تاريخ الانتهاء","قيمة العقد","نسبة الإنجاز","نسبة الصرف"
    ]
    cols = [c for c in cols if c in filtered.columns]
    view = filtered[cols].copy()

    if "تاريخ الانتهاء" in view.columns:
        view = view.sort_values("تاريخ الانتهاء")

    st.dataframe(view, use_container_width=True, hide_index=True)
