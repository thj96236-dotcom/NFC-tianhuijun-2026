import streamlit as st
from datetime import datetime

# 该文件由 main.py 调用，内部使用 show() 函数封装
def show():
    # ==========================================
    # 标题 + 合规提示
    # ==========================================
    st.title("🫀 房颤患者防中风自测工具")

    st.warning("⚠️ 本工具仅用于健康风险评估，不能替代医生诊断与治疗决策")

    st.markdown("👉 用1分钟评估：你是否属于脑梗（中风）高风险人群")

    # ==========================================
    # 输入
    # ==========================================
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👤 基本情况")

        age = st.number_input("年龄", 18, 100, 65)
        sex = st.radio("性别", ["男", "女"])

        st.markdown("### 🧠 既往病史")

        stroke = st.checkbox("是否得过脑梗/短暂性脑缺血")
        htn = st.checkbox("高血压")
        dm = st.checkbox("糖尿病")
        hf = st.checkbox("心衰")
        vascular = st.checkbox("冠心病/动脉硬化")

    with col2:
        st.subheader("⚠️ 出血与生活方式")

        bleeding = st.checkbox("有无严重出血史")
        alcohol = st.checkbox("经常饮酒")
        drug = st.checkbox("长期服用阿司匹林等药物")

        st.markdown("### 🚬 生活方式")
        smoking = st.checkbox("吸烟")

    # ==========================================
    # 评分函数 (放在 show 内部)
    # ==========================================
    def calc_cha():
        s = 0
        if age >= 75:
            s += 2
        elif age >= 65:
            s += 1
        if sex == "女":
            s += 1
        if htn:
            s += 1
        if dm:
            s += 1
        if stroke:
            s += 2
        if hf:
            s += 1
        if vascular:
            s += 1
        return s

    # ==========================================
    # 计算
    # ==========================================
    if st.button("🔍 开始评估"):

        cha = calc_cha()

        st.markdown("## 📊 你的评估结果")

        st.metric("中风风险评分（CHA₂DS₂-VASc）", cha)

        # =========================
        # 风险解释
        # =========================
        if cha >= 2:
            st.error("⚠️ 你属于脑梗（中风）高风险人群")
            st.write("👉 如果不进行抗凝治疗，发生脑梗的风险明显增加")
        else:
            st.success("✅ 当前风险相对较低，但仍建议定期评估")

        # =========================
        # 核心认知教育
        # =========================
        st.markdown("## ⚠️ 一个关键事实")

        st.error("很多房颤患者不是死于心慌，而是死于脑梗或瘫痪")

        st.write("👉 房颤会让心脏形成血栓")
        st.write("👉 血栓一旦进入大脑，就会导致脑梗")

        # =========================
        # 抗凝意义
        # =========================
        st.markdown("## 💊 为什么医生建议抗凝？")

        st.write("👉 抗凝药可以降低约60%–70%的脑梗风险")
        st.write("👉 是目前最有效的预防手段")

        # =========================
        # 停药风险（核心转化）
        # =========================
        st.markdown("## ❌ 为什么不能随便停药？")

        st.warning("很多患者在感觉好转后，会自行停药")

        st.write("👉 停药后，血栓风险会迅速上升")
        st.write("👉 很多严重脑梗发生在停药后的几天或几周内")

        # =========================
        # 行为建议
        # =========================
        st.markdown("## 📌 你现在应该做什么")

        if cha >= 2:
            st.write("👉 尽快咨询医生，评估是否需要长期抗凝")
        else:
            st.write("👉 定期随访，监测风险变化")

        if smoking:
            st.write("👉 戒烟：吸烟会明显增加脑梗风险")

        if alcohol:
            st.write("👉 减少饮酒：可降低出血风险")

        # =========================
        # 引流（关键模块）
        # =========================
        st.markdown("---")
        st.markdown("## 📲 获取更精准评估")

        st.info(
            """
    👉 当前为基础评估版本  

    👉 是否需要抗凝？什么时候开始？用什么药？  

    ⚠️ 需要医生综合判断（影像 + 卒中严重程度）

    👉 可咨询神经内科医生获取个体化方案
    """
        )

        st.markdown("👉 医生专业版工具：")
        st.code("（https://stroke-cdss-9q6hcwxvmccbevgpfxutst.streamlit.app/）")

    # ==========================================
    # 页脚版权
    # ==========================================
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align:center;color:gray;font-size:0.8em;'>
            © 2026 田慧军医生版权所有 | 房颤防卒中科普工具
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption("⚠️ 本工具仅用于健康教育，不能替代医生诊断")