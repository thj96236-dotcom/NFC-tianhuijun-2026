import streamlit as st
import datetime

def show():
    # ==========================================
    # 1. 权限管理
    # ==========================================
    # 2026 授权码逻辑：日期（MMDD）或通用码
    current_code = datetime.datetime.now().strftime("%m%d")

    with st.sidebar:
        st.title("🔐 权限管理")
        code = st.text_input("输入授权码", type="password", key="doctor_auth_code")

        is_pro = False
        if code in [current_code, "8888"]:
            is_pro = True
            st.success("Pro 专业版已解锁")
        elif code != "":
            st.error("授权验证失败")

    # ==========================================
    # 2. 内部逻辑函数 (算法层)
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

    def timing_decision(p):
        """抗凝启动时机（ELAN 研究 + LVO 修正）"""
        nihss = p["nihss"]
        infarct = p["infarct"]
        ht = p["ht"]
        bleed_risk = p["hasbled"]
        lvo = p["lvo"]

        # 绝对延迟项
        if ht == "PH":
            return "❌ 延迟评估：实质性出血转化（PH），建议至少延迟 14 天再行影像评估"
        
        # 极早期启动条件 (0-2天)
        if nihss <= 4 and infarct == "小" and ht == "无" and bleed_risk < 3 and not lvo:
            return "🟢 极早期启动（0–2 天）：梗死负荷极小，安全性高"
        
        # 大血管闭塞逻辑
        if lvo:
            if nihss <= 15:
                return "🟡 慎重启动（3–5 天）：LVO 提示梗死负荷较高，需复查 MRI/CT"
            else:
                return "🔴 延迟启动（6–10 天）：LVO 结合中重型卒中，出血风险较高"

        # 基于 NIHSS 的标准分层
        if nihss <= 4:
            return "🟢 早期启动（0–3 天）"
        elif nihss <= 15:
            return "🟡 中期启动（3–5 天）"
        else:
            return "🔴 延迟启动（6–10 天）"

    def drug_decision(p):
        """基于肾功能分级的 NOAC 选择"""
        renal = p["renal_level"]
        if renal == "重度下降（<30）":
            return "推荐方案：华法林（目标 INR 2.0–3.0）或 咨询肾内科"
        elif renal == "中度下降（30-44）":
            return "推荐方案：NOAC 减量（如 利伐沙班 15mg qd 或 阿哌沙班 2.5mg bid）"
        else:
            return "推荐方案：标准剂量 NOAC（利伐沙班 20mg qd / 阿哌沙班 5mg bid）"

    # ==========================================
    # 3. UI 界面层
    # ==========================================
    st.title("卒中后抗凝决策系统 (NFC 2026 版)")
    
    

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 临床特征")
        age = st.number_input("患者年龄", 18, 100, 70, key="dr_age")
        sex = st.radio("生理性别", ["男", "女"], horizontal=True, key="dr_sex")
        nihss_val = st.slider("NIHSS 评分", 0, 42, 8, key="dr_nihss")

        st.subheader("🧠 神经影像评估")
        infarct = st.radio("梗死灶大小", ["小", "中", "大"], help="小: 腔隙性; 中: 非主干皮质灶; 大: 主干区域")
        ht = st.radio("出血转化类型 (HT)", ["无", "HI (点状)", "PH (血肿)"])
        lvo = st.checkbox("伴有大血管闭塞 (LVO)", key="dr_lvo")

    with col2:
        st.subheader("⚠️ 风险因素")
        htn = st.checkbox("高血压病史", key="dr_htn")
        dm = st.checkbox("糖尿病史", key="dr_dm")
        stroke_history = st.checkbox("既往卒中/TIA 史", key="dr_stroke")
        hf = st.checkbox("充血性心力衰竭", key="dr_hf")
        vascular = st.checkbox("外周血管病/心梗史", key="dr_vas")
        
        st.divider()
        st.subheader("🩸 肾功与出血风险")
        renal_level = st.select_slider(
            "肾功能分级 (eGFR)",
            options=["正常（≥60）", "轻度下降（45-59）", "中度下降（30-44）", "重度下降（<30）"]
        )
        bleeding = st.checkbox("既往重大出血史", key="dr_bleed")
        drug_use = st.checkbox("联用抗血小板或 NSAIDs", key="dr_drug")
        alcohol = st.checkbox("习惯性饮酒", key="dr_alc")

    # ==========================================
    # 4. 结果生成层
    # ==========================================
    st.divider()
    if st.button("🚀 生成决策报告", use_container_width=True, key="dr_report_btn"):
        p = {
            "age": age, "sex": sex, "htn": htn, "dm": dm, "stroke": stroke_history,
            "hf": hf, "vascular": vascular, "renal": renal_level != "正常（≥60）",
            "bleeding": bleeding, "drug": drug_use, "alcohol": alcohol,
            "nihss": nihss_val, "infarct": infarct, "ht": ht,
            "renal_level": renal_level, "lvo": lvo
        }

        cha_score = calc_cha(p)
        has_score = calc_bleed(p)
        p["hasbled"] = has_score

        # 展示基础评分
        c1, c2, c3 = st.columns(3)
        c1.metric("CHA₂DS₂-VASc 评分", cha_score)
        c2.metric("HAS-BLED 评分", has_score)
        c3.metric("出血风险分级", "高" if has_score >= 3 else "中低")

        if is_pro:
            st.success("### 🧬 指南建议启动时机")
            st.info(f"**建议时机：** {timing_decision(p)}")
            
            st.markdown("---")
            st.success("### 💊 药物选择与剂量调整")
            st.write(drug_decision(p))

            st.markdown("#### 🔍 临床预警与备注")
            if lvo:
                st.warning("患者存在大血管闭塞，提示脑血流储备可能受损，启动抗凝前务必复查头部 CT 以排除后期出血转化。")
            if has_score >= 3:
                st.error("HAS-BLED ≥ 3 分，属于高出血风险人群。抗凝期间需严格控制血压（<130/80 mmHg）并定期监测肾功。")
            
            st.caption("依据标准：2023 ELAN Trial / 2024 AHA/ASA Stroke Secondary Prevention Guidelines.")
        else:
            st.warning("🔒 **专业版内容已锁定**。输入正确的授权码后可查看具体启动时机与药物剂量建议。")

    st.markdown("---")
    st.markdown("<div style='text-align:center;color:gray;font-size:0.8em;'>© 2026 田慧军医生 | 神经功能整合中心 (NFC) 技术支持</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    st.set_page_config(page_title="NFC-Anticoagulation", layout="wide")
    show()