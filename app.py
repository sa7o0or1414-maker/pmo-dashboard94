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
