import streamlit as st
import datetime

# ==========================================
# 1. 核心算法逻辑层 (2026 最新指南整合)
# ==========================================

def calc_cha(p):
    """CHA₂DS₂-VASc 评分计算"""
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
    """HAS-BLED 评分计算"""
    s = 0
    if p["htn"]: s += 1
    if p["renal"]: s += 1
    if p["stroke"]: s += 1
    if p["bleeding"]: s += 1
    if p["age"] > 65: s += 1
    if p["drug_alcohol"]: s += 1
    return s

def timing_decision(p):
    """抗凝启动时机（2023 ELAN 研究 + 2026 AHA/ASA 修正）"""
    nihss = p["nihss"]
    infarct = p["infarct"]
    ht = p["ht"]
    lvo = p["lvo"]

    if ht == "PH (血肿)":
        return "❌ **强制延迟**：实质性出血转化（PH），建议至少延迟 14 天，复查影像确认血肿吸收后再评估。"
    
    # 极早期启动 (1–2 天)
    if nihss <= 4 and infarct == "小" and ht == "无" and not lvo:
        return "🟢 **极早期启动（1–2 天）**：梗死负荷极小，安全性高，早期启动获益明确。"
    
    # 大血管闭塞 (LVO) 逻辑
    if lvo:
        if nihss <= 15:
            return "🟡 **策略性启动（3–5 天）**：LVO 提示梗死演变较复杂，需影像确认无隐匿性出血。"
        else:
            return "🔴 **延迟启动（7–10 天）**：重症 LVO 结合中重型卒中，出血风险较高，不建议过早抗凝。"

    # 标准 NIHSS 分层
    if nihss <= 4: return "🟢 **早期启动（0–3 天）**"
    elif nihss <= 15: return "🟡 **中期启动（3–6 天）**"
    else: return "🔴 **延迟启动（7–14 天）**"

def drug_decision(p):
    """基于 2026 最新证据的药物选择建议"""
    renal = p["renal_level"]
    age = p["age"]
    
    # 1. 重度肾功能下降 (eGFR < 30)
    if renal == "重度下降（<30）":
        return (
            "推荐方案：**华法林 (Warfarin)**（目标 INR 2.0–3.0）。\n\n"
            "**注意：** 若必须使用 NOAC，仅艾多沙班 (30mg qd) 或阿哌沙班 (2.5mg bid) 在特定条件下有数据支持，"
            "利伐沙班与达比加群在 CrCl < 15ml/min 时应绝对禁用。"
        )
    
    # 2. 中度肾功能下降 (eGFR 30–59)
    elif renal == "中度下降（30-44）" or renal == "轻度下降（45-59）":
        return (
            "推荐方案：**NOAC 减量方案**\n"
            "- **利伐沙班 (Rivaroxaban)**: 15mg qd (需随餐服用)\n"
            "- **阿哌沙班 (Apixaban)**: 2.5mg bid (若合并年龄≥80岁或体重≤60kg)\n"
            "- **艾多沙班 (Edoxaban)**: 30mg qd\n"
            "- **达比加群 (Dabigatran)**: 110mg bid"
        )
    
    # 3. 正常或轻度下降
    else:
        return (
            "推荐方案：**标准剂量 NOAC (首选)**\n"
            "- **利伐沙班 (Rivaroxaban)**: 20mg qd\n"
            "- **阿哌沙班 (Apixaban)**: 5mg bid\n"
            "- **达比加群 (Dabigatran)**: 150mg bid (注：75岁以上建议用110mg bid)"
        )

# ==========================================
# 2. UI 界面展示层
# ==========================================

def show():
    # 页面标题与配置
    st.title("🧠 卒中后抗凝决策系统 (NFC 2026 版)")
    st.markdown("---")
    
    # 第一部分：核心输入区
    with st.container(border=True):
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("📋 临床特征")
            age = st.number_input("患者年龄", 18, 100, 70, key="dr_age")
            sex = st.radio("生理性别", ["男", "女"], horizontal=True, key="dr_sex")
            nihss_val = st.slider("NIHSS 评分", 0, 42, 8, key="dr_nihss")
            lvo = st.checkbox("伴有大血管闭塞 (LVO)", help="颈内动脉、大脑中动脉 M1/M2 段闭塞或基底动脉闭塞")

        with col2:
            st.subheader("⚠️ 影像与风险因素")
            infarct = st.selectbox("梗死灶大小", ["小", "中", "大"], help="小: 腔隙性; 中: 非主干皮质灶; 大: 主干区域")
            ht = st.selectbox("出血转化类型 (HT)", ["无", "HI (点状)", "PH (血肿)"])
            renal_level = st.select_slider(
                "肾功能分级 (eGFR)",
                options=["正常（≥60）", "轻度下降（45-59）", "中度下降（30-44）", "重度下降（<30）"]
            )

    # 第二部分：合并症选项（折叠以保持界面整洁）
    with st.expander("更多合并症选项 (用于 CHA₂DS₂/HAS-BLED 自动计算)"):
        c1, c2 = st.columns(2)
        with c1:
            htn = st.checkbox("高血压病史", value=True, key="dr_htn")
            dm = st.checkbox("糖尿病史", key="dr_dm")
            stroke_history = st.checkbox("既往卒中/TIA 史", value=True, key="dr_stroke")
        with c2:
            hf = st.checkbox("充血性心力衰竭", key="dr_hf")
            vascular = st.checkbox("外周血管/心梗史", key="dr_vas")
            bleeding = st.checkbox("既往重大出血史", key="dr_bleed")
            drug_alcohol = st.checkbox("联用抗血小板/习惯性饮酒", key="dr_da")

    # 第三部分：生成结果
    st.divider()
    if st.button("🚀 生成 2026 临床决策报告", use_container_width=True, type="primary"):
        # 数据打包
        p = {
            "age": age, "sex": sex, "htn": htn, "dm": dm, "stroke": stroke_history,
            "hf": hf, "vascular": vascular, "renal": renal_level != "正常（≥60）",
            "bleeding": bleeding, "drug_alcohol": drug_alcohol,
            "nihss": nihss_val, "infarct": infarct, "ht": ht,
            "renal_level": renal_level, "lvo": lvo
        }

        # 评分计算
        cha_score = calc_cha(p)
        has_score = calc_bleed(p)

        # 1. 指标看板
        res1, res2, res3 = st.columns(3)
        res1.metric("CHA₂DS₂-VASc 评分", f"{cha_score} 分")
        res2.metric("HAS-BLED 评分", f"{has_score} 分")
        res3.metric("出血风险分级", "高风险" if has_score >= 3 else "中低风险")

        # 2. 详细辅助决策内容（全功能开放）
        st.markdown("---")
        st.subheader("💡 专业辅助决策建议")
        
        # 启动时机
        st.info(f"**建议启动时机：**\n\n{timing_decision(p)}")
        
        # 药物选择
        st.success(f"**药物选择及剂量参考：**\n\n{drug_decision(p)}")

        # 临床警示
        if lvo and ht == "无":
            st.warning("🔍 **临床预警：** 患者存在大血管闭塞。2026 指南强调，此类患者即使目前无出血，抗凝前建议复查头颅 CT 以排除迟发性渗血风险。")
        if has_score >= 3:
            st.error("🚨 **高出血风险：** HAS-BLED ≥ 3，需严格控制血压（<130/80），并在抗凝后 1 个月内复查血红蛋白与肾功。")

    # 页脚
    st.markdown("---")
    st.markdown("<div style='text-align:center;color:gray;font-size:0.8em;'>格式说明：宋体 | 无冗余符号 | 适用于医疗文书<br>© 2026 田慧军医生 | 神经功能整合中心 (NFC) 技术支持</div>", unsafe_allow_html=True)

# ==========================================
# 3. 程序入口
# ==========================================
if __name__ == "__main__":
    st.set_page_config(
        page_title="NFC-Anticoagulation", 
        page_icon="🧠", 
        layout="wide"
    )
    show()