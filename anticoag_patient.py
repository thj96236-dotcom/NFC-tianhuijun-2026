import streamlit as st
from datetime import datetime

# 该文件由 main.py 调用，内部使用 show() 函数封装
def show():
    # ==========================================
    # 1. 标题与合规提示
    # ==========================================
    st.title("🫀 房颤患者防中风自测工具")

    st.warning("⚠️ 本工具仅用于健康风险评估，不能替代医生诊断与治疗决策")
    st.markdown("👉 **用 1 分钟评估：您是否属于脑梗（中风）高风险人群**")

    # ==========================================
    # 2. 输入模块
    # ==========================================
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👤 基本情况")
        age = st.number_input("您的年龄", 18, 100, 65, key="pat_age")
        sex = st.radio("您的性别", ["男", "女"], horizontal=True, key="pat_sex")

        st.markdown("### 🧠 既往病史")
        stroke = st.checkbox("是否得过脑梗/短暂性脑缺血 (TIA)")
        htn = st.checkbox("高血压")
        dm = st.checkbox("糖尿病")
        hf = st.checkbox("心衰")
        vascular = st.checkbox("冠心病/动脉硬化")

    with col2:
        st.subheader("⚠️ 生活方式与药物")
        bleeding = st.checkbox("有严重出血史")
        alcohol = st.checkbox("经常饮酒")
        drug = st.checkbox("长期服用阿司匹林/氯吡格雷等")
        smoking = st.checkbox("目前仍吸烟")
        
        st.divider()
        st.info("💡 提示：如果您不确定，请参考出院小结上的诊断。")

    # ==========================================
    # 3. 评分逻辑 (CHA₂DS₂-VASc)
    # ==========================================
    def calc_cha():
        s = 0
        if age >= 75: s += 2
        elif age >= 65: s += 1
        if sex == "女": s += 1
        if htn: s += 1
        if dm: s += 1
        if stroke: s += 2
        if hf: s += 1
        if vascular: s += 1
        return s

    # ==========================================
    # 4. 计算与结果展示
    # ==========================================
    if st.button("🔍 开始评估", use_container_width=True):
        cha_score = calc_cha()

        st.markdown("## 📊 评估结果报告")
        st.metric("中风风险评分 (CHA₂DS₂-VASc)", f"{cha_score} 分")

        if cha_score >= 2:
            st.error("### ⚠️ 您属于脑梗（中风）高风险人群")
            st.write("👉 房颤会导致心脏内形成血栓。如果不进行规范抗凝，发生瘫痪性脑梗的风险极高。")
        else:
            st.success("### ✅ 当前评分风险相对较低")
            st.write("目前风险可控，但仍建议每年定期复评，并严格控制血压。")

        # --- 核心宣教模块 ---
        st.markdown("---")
        st.markdown("## ⚠️ 一个关键事实")
        st.error("**很多房颤患者不是死于心慌，而是死于脑梗引发的瘫痪。**")
        
        

        c1, c2 = st.columns(2)
        with c1:
            st.info("💊 **抗凝的意义**\n规范抗凝治疗可降低约 60%–70% 的脑梗风险，是目前最有效的预防手段。")
        with c2:
            st.warning("❌ **停药的危险**\n很多严重脑梗发生在患者‘感觉良好’自行停药后。停药后血栓风险会迅速反弹。")

        # --- 行为建议 ---
        st.markdown("## 📌 您现在应该做什么")
        if cha_score >= 2:
            st.markdown("- **尽快咨询：** 咨询神经内科医生，评估是否需要开启长期抗凝治疗。")
        
        if smoking:
            st.markdown("- **必须戒烟：** 吸烟会直接加速血管硬化，增加中风概率。")
        if alcohol:
            st.markdown("- **限制饮酒：** 过量饮酒会显著增加脑出血的风险。")

        # ==========================================
        # 5. 引流与闭环 (修复此处潜在的语法错误)
        # ==========================================
        st.divider()
        st.markdown("### 📲 获取更精准的临床决策")
        
        st.info(
            """
            👉 **当前为基础评估版** 真实的临床决策需要结合您的脑部影像（CT/MRI）、梗死面积大小以及是否有出血倾向来综合判断。
            
            ⚠️ **专业建议：** 请咨询医生获取“什么时候开始吃药”和“具体吃多少量”的个体化方案。
            """
        )

        st.markdown("👉 **医生专用临床决策系统 (CDSS) 入口：**")
        st.code("https://stroke-cdss-9q6hcwxvmccbevgpfxutst.streamlit.app/")

    # ==========================================
    # 6. 页脚 (宋体适配)
    # ==========================================
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align:center;color:gray;font-size:0.8em;font-family:SimSun;'>
            © 2026 田慧军医生版权所有 | 神经功能整合中心 (NFC) | 房颤防卒中科普工具
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    st.set_page_config(page_title="房颤中风风险自测", layout="centered")
    show()