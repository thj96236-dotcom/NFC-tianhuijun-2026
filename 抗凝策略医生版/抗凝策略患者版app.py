import streamlit as st
import datetime

# 【修改点 1】：删除了 st.set_page_config，交给 main.py 统一管理

def show():
    # 【修改点 2】：所有业务代码缩进，包裹在 show() 函数内
    
    # ==========================================
    # 权限管理 (移至 show 内部，确保在子页面也能独立逻辑)
    # ==========================================
    current_code = datetime.datetime.now().strftime("%m%d")

    with st.sidebar:
        st.title("🔐 权限管理")
        code = st.text_input("输入授权码", type="password", key="doctor_auth_code")

        is_pro = False
        if code in [current_code, "8888"]:
            is_pro = True
            st.success("Pro已解锁")
        elif code != "":
            st.error("授权失败")

    # ==========================================
    # 内部评分函数
    # ==========================================
    def calc_cha(p):
        s = 0
        if p["age"] >= 75: s += 2
        elif p["age"] >= 65: s += 1
        if p["sex"] == "女": s += 1
        if p["htn"]: s += 1
        if p["dm"]: s += 1
        if p["stroke"]: s += 2
        if p["hf"]: s += 1
        if p["vascular"]: s += 1
        return s

    def calc_bleed(p):
        s = 0
        if p["htn"]: s += 1
        if p["renal"]: s += 1
        if p["stroke"]: s += 1
        if p["bleeding"]: s += 1
        if p["age"] > 65: s += 1
        if p["drug"] or p["alcohol"]: s += 1
        return s

    # 抗凝时机（ELAN + LVO修正）
    def timing_decision(p):
        nihss = p["nihss"]
        infarct = p["infarct"]
        ht = p["ht"]
        bleed_risk = p["hasbled"]
        lvo = p["lvo"]

        if ht == "PH":
            return "❌ 延迟 ≥14天（或暂缓抗凝）"
        if nihss <= 4 and infarct == "小" and ht == "无" and bleed_risk < 3 and not lvo:
            return "🟢 超早期启动（0–2天）"
        if lvo:
            if nihss <= 15:
                return "🟡 3–5天启动（LVO患者建议谨慎）"
            else:
                return "🔴 6–10天或更晚（LVO + 重型卒中）"
        if nihss <= 4:
            return "🟢 早期启动（0–3天）"
        elif nihss <= 15:
            return "🟡 3–5天启动"
        else:
            return "🔴 6–10天或更晚"

    def drug_decision(p):
        renal = p["renal_level"]
        if renal == "重度下降（<30）":
            return "华法林（INR 2–3）"
        elif renal == "中度下降（30-44）":
            return "NOAC减量（如利伐沙班15mg）"
        else:
            return "标准NOAC（利伐沙班20mg / 阿哌沙班5mg bid）"

    # ==========================================
    # UI 界面
    # ==========================================
    st.title("卒中后抗凝决策系统（V6.3 指南强化版）")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📋 基本信息")
        af = st.toggle("房颤", True)
        age = st.number_input("年龄", 18, 100, 70, key="dr_age")
        sex = st.radio("性别", ["男", "女"], key="dr_sex")
        nihss_val = st.slider("NIHSS", 0, 42, 8, key="dr_nihss")

        st.subheader("🧠 脑影像评估")
        infarct = st.radio("梗死范围", ["小", "中", "大"], help="小：腔隙性或小皮质灶（NIHSS≤5）...")
        ht = st.radio("出血转化", ["无", "HI", "PH"])
        lvo = st.radio("大血管闭塞（LVO）", ["否", "是"]) == "是"

        st.markdown("### 风险因素")
        htn = st.checkbox("高血压", key="dr_htn")
        dm = st.checkbox("糖尿病", key="dr_dm")
        stroke_history = st.checkbox("卒中史", key="dr_stroke")
        hf = st.checkbox("心衰", key="dr_hf")
        vascular = st.checkbox("血管病", key="dr_vas")
        smoking = st.checkbox("吸烟", key="dr_smoke")

    with col2:
        st.subheader("⚠️ 出血风险")
        renal_level = st.radio("肾功能分级", ["正常（≥60）", "轻度下降（45-59）", "中度下降（30-44）", "重度下降（<30）"])
        bleeding = st.checkbox("出血史", key="dr_bleed")
        drug_use = st.checkbox("抗血小板/NSAIDs", key="dr_drug")
        alcohol = st.checkbox("饮酒", key="dr_alc")

    # ==========================================
    # 计算与报告生成
    # ==========================================
    if st.button("🚀 生成报告", key="dr_report_btn"):
        p = {
            "age": age, "sex": sex, "htn": htn, "dm": dm, "stroke": stroke_history,
            "hf": hf, "vascular": vascular, "renal": renal_level != "正常（≥60）",
            "bleeding": bleeding, "drug": drug_use, "alcohol": alcohol,
            "nihss": nihss_val, "infarct": infarct, "ht": ht,
            "renal_level": renal_level, "smoking": smoking, "lvo": lvo
        }

        cha = calc_cha(p)
        hasbled = calc_bleed(p)
        p["hasbled"] = hasbled

        timing = timing_decision(p)
        drug_plan = drug_decision(p)

        st.markdown("## 📊 基础评估")
        c1, c2 = st.columns(2)
        c1.metric("CHA₂DS₂-VASc", cha)
        c2.metric("HAS-BLED", hasbled)

        if is_pro:
            st.divider()
            st.subheader("🧬 Pro 专业报告（指南强化版）")
            st.markdown("### ⏱ 抗凝启动时机")
            st.info(timing)
            
            st.markdown("**📚 指南依据：**")
            st.write("- ELAN研究：早期抗凝安全性不劣，可能降低复发")
            st.write("- AHA/ASA：基于卒中严重程度个体化")

            st.markdown("### 💊 个体化抗凝方案")
            st.success(drug_plan)

            st.markdown("### 🧠 临床解释")
            if lvo: st.write("• LVO提示梗死负荷大，需谨慎抗凝")
            if hasbled >= 3: st.warning("• 高出血风险：建议严格控制血压")
        else:
            st.warning("🔒 专业报告已锁定，请输入正确的授权码查看时机建议")

    st.markdown("---")
    st.markdown("<div style='text-align:center;color:gray;font-size:0.8em;'>© 2026 田慧军医生 | 技术支持：NFC Center</div>", unsafe_allow_html=True)