import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date, timedelta

# ---------------- إعدادات الصفحة ----------------
st.set_page_config(page_title="منصة PMO", layout="wide")

# ---------------- الحالة ----------------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "role" not in st.session_state:
    st.session_state.role = "viewer"  # مشاهد افتراضي
if "show_overdue" not in st.session_state:
    st.session_state.show_overdue = False
if "show_risk" not in st.session_state:
    st.session_state.show_risk = False

# ---------------- بيانات المسؤول ----------------
ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# ---------------- المسارات ----------------
DATA_DIR = Path("data")
ASSETS_DIR = Path("assets")
DATA_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

EXCEL_PATH = DATA_DIR / "data.xlsx"
LOGO_PATH = ASSETS_DIR / "logo.png"

# ---------------- CSS (سنترة + هوية + تنسيق جميل) ----------------
st.markdown("""
<style>
:root{
--main:#153e46;--light:#1f5661;--dark:#0f2d33;
--card:#ffffff;
--shadow: 0 10px 26px rgba(0,0,0,0.08);
}

/* سنترة شاملة */
html, body, [class*="css"] {
    direction: rtl;
    text-align: center !important;
    font-family: 'Segoe UI', sans-serif;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: var(--dark);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

/* أزرار */
.stButton button {
    width: 230px;
    height: 56px;
    background: var(--main);
    color: white;
    border: none;
    border-radius: 16px;
    font-size: 16px;
    margin-bottom: 14px;
    text-align: center;
    transition: 0.25s;
}
.stButton button:hover { background: var(--light); }

/* محتوى الصفحة */
.block-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 90vh;
}

/* عناوين */
h1, h2, h3 { color: var(--main); text-align: center !important; }
p, label, span, div { text-align: center !important; }

/* Inputs */
input { text-align: center !important; }

/* Cards */
.card {
    background: var(--card);
    padding: 22px 18px;
    border-radius: 20px;
    box-shadow: var(--shadow);
    width: 100%;
}
.card-title {
    font-size: 14px;
    color: rgba(0,0,0,0.65);
    margin-bottom: 8px;
}
.card-value {
    font-size: 26px;
    font-weight: 700;
    color: var(--main);
}

/* Mini cards for buttons */
.action-btn button{
    width: 100%;
    height: 54px;
    border-radius: 18px;
}

/* Logo */
img { display: block; margin: 0 auto 14px auto; }
</style>
""", unsafe_allow_html=True)

# ---------------- أدوات مساعدة ----------------
def _norm_col(c: str) -> str:
    return str(c).strip().replace("\u200f", "").replace("\u200e", "")

def load_data():
    if not EXCEL_PATH.exists():
        return None

    try:
        # تفضيل شيت Data، وإن ما وجد نقرأ أول شيت
        xls = pd.ExcelFile(EXCEL_PATH)
        sheet = "Data" if "Data" in xls.sheet_names else xls.sheet_names[0]
        df0 = pd.read_excel(EXCEL_PATH, sheet_name=sheet)
        df0.columns = [_norm_col(c) for c in df0.columns]
        return df0
    except Exception:
        return None

def to_num(series):
    # يحول أرقام مع فواصل/نصوص إلى رقم
    s = series.astype(str).str.replace(",", "", regex=False).str.replace("٪", "", regex=False).str.strip()
    return pd.to_numeric(s, errors="coerce")

def fmt_money(x):
    if pd.isna(x):
        return "0"
    return f"{x:,.0f}"

def safe_dt(series):
    return pd.to_datetime(series, errors="coerce")

REQUIRED_COLS = [
    "التصنيف","الجهة","البلدية","اسم المشروع","تاريخ التسليم","تاريخ الانتهاء","حالة المشروع",
    "نوع العقد","رقم العقد","قيمة العقد","قيمة المستخلصات المعتمدة","المتبقي من المستخلص","نسبة الصرف","المقاول"
]

# ---------------- تحميل البيانات ----------------
df = load_data()

# ---------------- Sidebar ----------------
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=120)
    else:
        st.markdown("<b style='color:white'>منصة PMO</b>", unsafe_allow_html=True)

    if st.button("الصفحة الرئيسية"):
        st.session_state.page = "home"

    # تظهر للمسؤول فقط
    if st.session_state.role == "admin":
        if st.button("رفع البيانات"):
            st.session_state.page = "upload"

    # دخول/خروج
    if st.session_state.role != "admin":
        if st.button("تسجيل دخول المسؤول"):
            st.session_state.page = "login"
    else:
        if st.button("تسجيل خروج"):
            st.session_state.role = "viewer"
            st.session_state.page = "home"
            st.rerun()

# ---------------- صفحة تسجيل الدخول ----------------
if st.session_state.page == "login":
    st.title("تسجيل دخول المسؤول")

    u = st.text_input("اسم المستخدم", key="login_user")
    p = st.text_input("كلمة المرور", type="password", key="login_pass")

    if st.button("دخول"):
        if u == ADMIN_USER and p == ADMIN_PASS:
            st.session_state.role = "admin"
            st.session_state.page = "home"
            st.success("تم تسجيل الدخول بنجاح")
            st.rerun()  # ظهور أيقونة الرفع مباشرة
        else:
            st.error("بيانات الدخول غير صحيحة")

# ---------------- صفحة رفع البيانات (Admin فقط) ----------------
if st.session_state.page == "upload":
    if st.session_state.role != "admin":
        st.warning("غير مصرح لك بالوصول")
    else:
        st.title("رفع البيانات")

        st.subheader("رفع ملف Excel")
        excel = st.file_uploader("رفع ملف Excel", type=["xlsx"])
        if excel:
            with open(EXCEL_PATH, "wb") as f:
                f.write(excel.getbuffer())
            st.success("تم حفظ ملف البيانات")
            st.rerun()

        st.divider()

        st.subheader("رفع شعار الجهة")
        logo = st.file_uploader("رفع شعار الجهة", type=["png","jpg","jpeg"])
        if logo:
            with open(LOGO_PATH, "wb") as f:
                f.write(logo.getbuffer())
            st.success("تم حفظ الشعار")
            st.rerun()

# ---------------- الصفحة الرئيسية (Dashboard) ----------------
if st.session_state.page == "home":
    st.title("لوحة التحكم")

    if df is None:
        st.warning("لا توجد بيانات بعد. ارفع ملف Excel من صفحة رفع البيانات (للمسؤول).")
    else:
        # تحقق الأعمدة
        missing = [c for c in REQUIRED_COLS if c not in df.columns]
        if missing:
            st.error("يوجد أعمدة ناقصة في ملف Excel:")
            st.write(missing)
        else:
            # تجهيز الأنواع
            work = df.copy()

            work["تاريخ التسليم"] = safe_dt(work["تاريخ التسليم"])
            work["تاريخ الانتهاء"] = safe_dt(work["تاريخ الانتهاء"])

            work["قيمة العقد"] = to_num(work["قيمة العقد"]).fillna(0)
            work["قيمة المستخلصات المعتمدة"] = to_num(work["قيمة المستخلصات المعتمدة"]).fillna(0)
            work["المتبقي من المستخلص"] = to_num(work["المتبقي من المستخلص"]).fillna(
                (work["قيمة العقد"] - work["قيمة المستخلصات المعتمدة"]).clip(lower=0)
            )

            # نسبة الصرف: إذا مو موجودة بشكل صحيح نحسبها
            spend = to_num(work["نسبة الصرف"])
            spend_calc = (work["قيمة المستخلصات المعتمدة"] / work["قيمة العقد"].replace(0, pd.NA)) * 100
            work["نسبة الصرف"] = spend.fillna(spend_calc).fillna(0)

            # ---------------- الفلاتر (Drop-down) ----------------
            st.subheader("الفلاتر")

            c1, c2, c3 = st.columns(3)
            with c1:
                f_cat = st.selectbox("التصنيف", ["الكل"] + sorted(work["التصنيف"].dropna().astype(str).unique().tolist()))
            with c2:
                f_ent = st.selectbox("الجهة", ["الكل"] + sorted(work["الجهة"].dropna().astype(str).unique().tolist()))
            with c3:
                f_mun = st.selectbox("البلدية", ["الكل"] + sorted(work["البلدية"].dropna().astype(str).unique().tolist()))

            c4, c5 = st.columns(2)
            with c4:
                f_status = st.selectbox("حالة المشروع", ["الكل"] + sorted(work["حالة المشروع"].dropna().astype(str).unique().tolist()))
            with c5:
                f_contract = st.selectbox("نوع العقد", ["الكل"] + sorted(work["نوع العقد"].dropna().astype(str).unique().tolist()))

            filtered = work.copy()
            if f_cat != "الكل":
                filtered = filtered[filtered["التصنيف"].astype(str) == f_cat]
            if f_ent != "الكل":
                filtered = filtered[filtered["الجهة"].astype(str) == f_ent]
            if f_mun != "الكل":
                filtered = filtered[filtered["البلدية"].astype(str) == f_mun]
            if f_status != "الكل":
                filtered = filtered[filtered["حالة المشروع"].astype(str) == f_status]
            if f_contract != "الكل":
                filtered = filtered[filtered["نوع العقد"].astype(str) == f_contract]

            # ---------------- تحليل التأخير ----------------
            today = date.today()
            today_ts = pd.to_datetime(today)

            # المشاريع المتأخرة: تاريخ الانتهاء أقل من اليوم وحالة ليست مكتمل/منجز
            done_like = {"مكتمل", "منجز", "تم الإنجاز", "مغلق"}
            filtered["__status_norm"] = filtered["حالة المشروع"].astype(str).str.strip()
            overdue = filtered[
                (filtered["تاريخ الانتهاء"].notna()) &
                (filtered["تاريخ الانتهاء"] < today_ts) &
                (~filtered["__status_norm"].isin(done_like))
            ].copy()

            # المتوقع تأخرها: نهاية خلال 30 يوم + (نسبة صرف منخفضة أو مستخلصات قليلة أو حالة تعطّل)
            horizon = today_ts + pd.Timedelta(days=30)
            risk = filtered[
                (filtered["تاريخ الانتهاء"].notna()) &
                (filtered["تاريخ الانتهاء"] >= today_ts) &
                (filtered["تاريخ الانتهاء"] <= horizon) &
                (~filtered["__status_norm"].isin(done_like))
            ].copy()

            # أسباب التوقع (قواعد بسيطة قابلة للتطوير)
            def risk_reason(row):
                reasons = []
                # قرب تاريخ الانتهاء
                if pd.notna(row["تاريخ الانتهاء"]):
                    days_left = (row["تاريخ الانتهاء"].date() - today).days
                    if days_left <= 14:
                        reasons.append("قرب تاريخ الانتهاء (أقل من 14 يوم)")
                    else:
                        reasons.append("قرب تاريخ الانتهاء (خلال 30 يوم)")
                # نسبة صرف
                if row["نسبة الصرف"] < 50:
                    reasons.append("نسبة الصرف منخفضة")
                # مستخلصات
                if row["قيمة المستخلصات المعتمدة"] < (0.5 * row["قيمة العقد"]):
                    reasons.append("المستخلصات أقل من المتوقع")
                # حالة قد تعني تعثر
                status = str(row["حالة المشروع"]).strip()
                if any(k in status for k in ["متوقف", "متعثر", "متأخر"]):
                    reasons.append("حالة المشروع تشير لتعثر")
                # دمج
                return "، ".join(dict.fromkeys(reasons)) if reasons else "مؤشرات تنفيذ غير كافية مقارنة بالمدة المتبقية"

            if not risk.empty:
                risk["سبب التوقع"] = risk.apply(risk_reason, axis=1)

            # ---------------- كروت KPI (إبداعي + مرتب) ----------------
            st.divider()

            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.markdown(
                    f"<div class='card'><div class='card-title'>عدد المشاريع</div><div class='card-value'>{len(filtered)}</div></div>",
                    unsafe_allow_html=True
                )
            with k2:
                st.markdown(
                    f"<div class='card'><div class='card-title'>إجمالي قيمة العقود</div><div class='card-value'>{fmt_money(filtered['قيمة العقد'].sum())}</div></div>",
                    unsafe_allow_html=True
                )
            with k3:
                st.markdown(
                    f"<div class='card'><div class='card-title'>إجمالي المستخلصات المعتمدة</div><div class='card-value'>{fmt_money(filtered['قيمة المستخلصات المعتمدة'].sum())}</div></div>",
                    unsafe_allow_html=True
                )
            with k4:
                st.markdown(
                    f"<div class='card'><div class='card-title'>إجمالي المتبقي من المستخلص</div><div class='card-value'>{fmt_money(filtered['المتبقي من المستخلص'].sum())}</div></div>",
                    unsafe_allow_html=True
                )

            # كارد نسبة الصرف (متوسط)
            st.markdown(
                f"<div class='card' style='max-width:720px; margin-top:14px;'>"
                f"<div class='card-title'>متوسط نسبة الصرف</div>"
                f"<div class='card-value'>{filtered['نسبة الصرف'].mean():.1f}%</div>"
                f"</div>",
                unsafe_allow_html=True
            )

            # ---------------- أيقونات/أزرار قوائم المتأخر والمتوقع ----------------
            st.divider()
            a1, a2 = st.columns(2)

            with a1:
                if st.button("المشاريع المتأخرة"):
                    st.session_state.show_overdue = not st.session_state.show_overdue

            with a2:
                if st.button("المشاريع المتوقع تأخرها"):
                    st.session_state.show_risk = not st.session_state.show_risk

            # عرض قائمة المتأخر
            if st.session_state.show_overdue:
                st.subheader("قائمة المشاريع المتأخرة")
                if overdue.empty:
                    st.info("لا توجد مشاريع متأخرة حسب الفلاتر الحالية.")
                else:
                    show_cols = ["اسم المشروع", "المقاول", "الجهة", "البلدية", "تاريخ الانتهاء", "حالة المشروع", "رقم العقد"]
                    st.dataframe(overdue[show_cols].sort_values("تاريخ الانتهاء"), use_container_width=True)

            # عرض قائمة المتوقع
            if st.session_state.show_risk:
                st.subheader("قائمة المشاريع المتوقع تأخرها")
                if risk.empty:
                    st.info("لا توجد مشاريع متوقع تأخرها حسب الفلاتر الحالية.")
                else:
                    show_cols = ["اسم المشروع", "المقاول", "الجهة", "البلدية", "تاريخ الانتهاء", "حالة المشروع", "سبب التوقع"]
                    st.dataframe(risk[show_cols].sort_values("تاريخ الانتهاء"), use_container_width=True)

            # ---------------- تفاصيل المشاريع (يظهر المقاول/القيم...) ----------------
            st.divider()
            st.subheader("تفاصيل المشاريع")

            detail_cols = [
                "التصنيف", "الجهة", "البلدية", "اسم المشروع", "المقاول",
                "تاريخ التسليم", "تاريخ الانتهاء", "حالة المشروع",
                "نوع العقد", "رقم العقد",
                "قيمة العقد", "قيمة المستخلصات المعتمدة", "المتبقي من المستخلص", "نسبة الصرف"
            ]
            st.dataframe(filtered[detail_cols], use_container_width=True)
