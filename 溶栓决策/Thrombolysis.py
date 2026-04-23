import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def thrombolysis_module():
    """
    急性缺血性卒中 (AIS) 专家决策中心模块
    """
    # --- 1. 内部权限逻辑 ---
    VALID_CODES = ["NFC2026", "TIAN888", "STROKE2026"] 

    # 使用特定前缀的 session_state 以防干扰其他模块
    if 'th_authenticated' not in st.session_state:
        st.session_state['th_authenticated'] = False

    with st.sidebar:
        st.title("🛡️ NFC 决策中心")
        st.markdown("---")
        # 增加唯一的 key="th_auth_input"
        auth_code = st.text_input("🔑 输入专业版授权码", type="password", key="th_auth_input", help="输入正确授权码后按回车解锁")
        
        if auth_code:
            if auth_code in VALID_CODES:
                st.session_state['th_authenticated'] = True
                st.success("✅ 专家功能已解锁")
            else:
                st.session_state['th_authenticated'] = False
                st.error("❌ 授权码错误")
        
        st.markdown("---")
        if st.session_state['th_authenticated']:
            st.markdown("### 状态：<span style='color:gold'>💎 专业进阶版</span>", unsafe_allow_html=True)
        else:
            st.markdown("### 状态：<span style='color:gray'>⚪ 标准免费版</span>", unsafe_allow_html=True)

    # --- 2. 界面主体 ---
    st.title("🧠 急性缺血性卒中 (AIS) 专家决策中心")
    st.caption("2026 专家共识版 | DNT 自动监测 | 专家避坑指南")
    st.markdown("---")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        # A. 时间质控模块
        with st.expander("⏱️ 1. 质控时间轴 (Time Management)", expanded=True):
            t1, t2 = st.columns(2)
            with t1:
                onset_date = st.date_input("发病日期 (Onset)", datetime.now(), key="th_onset_date")
                onset_time = st.time_input("发病时刻", datetime.now() - timedelta(hours=2), key="th_onset_time")
                arrival_date = st.date_input("到院日期 (Door)", datetime.now(), key="th_arrival_date")
                arrival_time = st.time_input("到院时刻", datetime.now() - timedelta(minutes=30), key="th_arrival_time")
            
            with t2:
                current_now = datetime.now()
                st.metric("决策/给药时刻 (Needle)", current_now.strftime("%H:%M:%S"))
                
                onset_dt = datetime.combine(onset_date, onset_time)
                arrival_dt = datetime.combine(arrival_date, arrival_time)
                
                dnt_val = (current_now - arrival_dt).total_seconds() / 60
                ont_val = (current_now - onset_dt).total_seconds() / 60

                st.write(f"📊 **实时质控数据：**")
                st.warning(f"**DNT (到院-给药): {int(dnt_val)} 分钟**")
                st.info(f"**ONT (发病-给药): {int(ont_val)} 分钟**")
                
                if dnt_val > 60:
                    st.error("🚨 DNT 预警：已超过 60 分钟！")

        # B. 患者核心指标
        with st.expander("📋 2. 患者临床指标", expanded=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                weight = st.number_input("体重 (kg)", 30.0, 150.0, 65.0, key="th_pt_weight")
            with c2:
                nihss = st.slider("NIHSS 评分", 0, 42, 4, key="th_pt_nihss")
                bp_sys = st.number_input("收缩压 (mmHg)", 80, 240, 140, key="th_pt_bp")
            with c3:
                blood_sugar = st.number_input("血糖 (mmol/L)", 1.0, 30.0, 6.0, key="th_pt_bs")
                drug_choice = st.selectbox("拟选药物", ["rt-PA (爱通立)", "TNK (替奈普酶)"], key="th_pt_drug")

        # C. 禁忌症分层核查
        with st.expander("🚩 3. 核心禁忌症核查表", expanded=True):
            st.markdown("**绝对禁忌症**")
            abs_1 = st.checkbox("CT已见出血 / ASPECTS < 5", key="th_check_abs1")
            abs_2 = st.checkbox("既往颅内出血史 (ICH)", key="th_check_abs2")
            abs_3 = st.checkbox("近3个月严重头外伤或卒中史", key="th_check_abs3")
            abs_4 = st.checkbox("已知颅内肿瘤/动静脉畸形", key="th_check_abs4")
            
            st.markdown("**相对禁忌/警示**")
            rel_1 = st.checkbox("近期(14天内)大手术或严重创伤", key="th_check_rel1")
            rel_2 = st.checkbox("正在服用抗凝药(NOACs)且凝血异常", key="th_check_rel2")

    with col_right:
        # D. ASPECTS 评分辅助
        st.subheader("🧠 ASPECTS 评分辅助")
        regions = ["C", "L", "IC", "I", "M1", "M2", "M3", "M4", "M5", "M6"]
        selected_regions = [r for r in regions if st.checkbox(f"{r} 区早期改变", key=f"th_asp_{r}")]
        current_aspects = 10 - len(selected_regions)
        
        asp_color = "green" if current_aspects >= 6 else "red"
        st.markdown(f"#### ASPECTS 得分: <span style='color:{asp_color}'>{current_aspects} 分</span>", unsafe_allow_html=True)
        
        # E. 影像学判定
        st.subheader("🧪 影像学多模态")
        mismatch = st.selectbox("错配判定类型", ["4.5h内", "DWI/FLAIR 错配", "PWI/DWI 错配", "无明显错配"], key="th_img_mismatch")

    st.markdown("---")

    # --- 3. 核心决策引擎 ---
    if st.button("🚀 启动溶栓决策预案", key="th_main_run_btn"):
        final_now = datetime.now()
        final_dnt = (final_now - arrival_dt).total_seconds() / 60
        
        is_safe = True
        error_list = []
        if any([abs_1, abs_2, abs_3, abs_4]): 
            is_safe = False
            error_list.append("存在绝对禁忌症")
        if bp_sys > 185: 
            is_safe = False
            error_list.append("收缩压高于 185mmHg")
        if blood_sugar < 2.8 or blood_sugar > 22.2: 
            is_safe = False
            error_list.append("血糖不在安全范围")

        if not is_safe:
            st.error(f"### ❌ 结论：禁止溶栓\n**原因**：{', '.join(error_list)}")
        else:
            if nihss >= 21:
                st.warning(f"### ⚠️ 结论：重度卒中高风险决策 (NIHSS {nihss}分)")
                if current_aspects < 6:
                    st.error("🚨 **核心预警**：建议立即转为 EVT (血管内取栓) 评估。")
                else:
                    st.info(f"💡 **专家建议**：执行 Drip-and-Ship (边溶边取) 模式。")
            else:
                st.success(f"### ✅ 结论：符合标准溶栓指征")
            
            # 剂量方案
            if drug_choice == "rt-PA (爱通立)":
                total_dose = min(weight * 0.9, 90.0)
                st.info(f"**给药方案**：rt-PA 总量 {total_dose:.2f}mg。10%推注，90%静脉泵入(1h)。")
            else:
                total_dose = min(weight * 0.25, 25.0)
                st.info(f"**给药方案**：TNK 总量 {total_dose:.2f}mg。单次静脉推注。")

            # --- 4. 授权内容展示 ---
            if st.session_state['th_authenticated']:
                st.markdown("---")
                st.markdown("## 💎 [已解锁] 专家避坑指南 (2026 版)")
                st.error("1. 【突发呕吐】：立即停药，直送复查 CT。 2. 【禁忌操作】：24小时内严禁动脉穿刺或肌注。")
            else:
                st.warning("🔒 专家深度建议已锁定，请输入授权码解锁。")

    st.markdown("---")
    st.markdown("<div style='text-align:center;color:gray;font-size:0.8em;'>© 2026 田慧军医生版权所有 | 技术支持：NFC Center</div>", unsafe_allow_html=True)

# 如需单独测试，取消下方注释
# if __name__ == "__main__":
#     thrombolysis_module()