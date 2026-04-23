import streamlit as st
from datetime import datetime, timedelta
import hashlib
import uuid

# --- 1. 核心权限工具函数 (保持在函数外作为工具) ---
def get_machine_id():
    node = uuid.getnode()
    return hashlib.sha256(str(node).encode()).hexdigest()[:12].upper()

def verify_license(user_input, machine_id):
    SECRET_SALT = "PSS_PRO_2026_THJ"
    correct_lic = hashlib.sha256((machine_id.strip().upper() + SECRET_SALT).encode()).hexdigest()[:8].upper()
    return user_input.strip().upper() == correct_lic

# --- 2. 主模块函数 (由 main.py 调用) ---
def show():
    # 注意：子模块内部不调用 st.set_page_config

    VALID_CODES = ["NFC2026", "TIAN888", "STROKE2026"] 
    
    if 'authenticated' not in st.session_state: 
        st.session_state['authenticated'] = False

    st.title("🧠 急性缺血性卒中 (AIS) 专家决策中心")
    
    # 侧边栏：授权管理
    with st.sidebar:
        st.header("🔐 授权验证")
        auth_code = st.text_input("🔑 输入专业版授权码", type="password", key="th_auth_key")
        if auth_code in VALID_CODES:
            st.session_state['authenticated'] = True
            st.success("专业版已解锁")
        
        st.divider()
        st.info(f"设备识别码: {get_machine_id()}")

    # 布局：左侧临床指标，右侧评分量表
    col_left, col_right = st.columns([2, 1])

    with col_left:
        # 1. DNT 管理
        with st.expander("⏱️ 1. 质控时间轴 (DNT 管理)", expanded=True):
            t1, t2 = st.columns(2)
            with t1:
                arrival_date = st.date_input("到院日期", datetime.now(), key="th_d")
                arrival_time = st.time_input("到院时刻", datetime.now() - timedelta(minutes=30), key="th_t")
            with t2:
                current_now = datetime.now()
                st.write("**当前决策时刻 (Needle)**")
                st.subheader(current_now.strftime("%H:%M:%S"))
                
                arrival_dt = datetime.combine(arrival_date, arrival_time)
                dnt_val = (current_now - arrival_dt).total_seconds() / 60
                
                if dnt_val > 45:
                    st.error(f"DNT: {int(dnt_val)} min (已超标，请加速！)")
                else:
                    st.success(f"DNT: {int(dnt_val)} min (质控达标)")

        # 2. 核心临床指标
        with st.expander("📋 2. 患者核心临床指标", expanded=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                weight = st.number_input("体重 (kg)", 30.0, 150.0, 65.0, step=0.5)
            with c2:
                nihss = st.slider("NIHSS 评分", 0, 42, 4)
                bp_sys = st.number_input("收缩压 (mmHg)", 80, 240, 140)
            with c3:
                blood_sugar = st.number_input("血糖 (mmol/L)", 1.0, 30.0, 6.0, step=0.1)
                drug_choice = st.selectbox("拟选药物", ["rt-PA (爱通立)", "TNK (替奈普酶)"])

        # 3. 禁忌症筛查
        with st.expander("🚩 3. 核心禁忌症与警示 (一键核查)", expanded=True):
            st.markdown("##### **绝对禁忌症 (任一选中即不可溶栓)**")
            abs_1 = st.checkbox("CT发现颅内出血 / ASPECTS < 5")
            abs_2 = st.checkbox("既往所有颅内出血史 (ICH)")
            abs_3 = st.checkbox("近3个月重大颅脑外伤或卒中史")
            abs_4 = st.checkbox("活动性内出血 / 已知的严重出血体质")
            
            st.markdown("##### **相对禁忌证 (临床综合权衡风险)**")
            rel_1 = st.checkbox("症状轻微且快速改善 (LVO除外)")
            rel_2 = st.checkbox("妊娠期 / 近2周内重大手术或创伤")

    with col_right:
        # ASPECTS 评分系统
        st.subheader("🖼️ ASPECTS 评分")
        st.caption("勾选缺血受损区域（每选一项减1分）")
        regions = ["C (尾状核)", "L (豆状核)", "IC (内囊)", "I (岛叶)", "M1", "M2", "M3", "M4", "M5", "M6"]
        
        deductions = 0
        for r in regions:
            if st.checkbox(f"受损: {r}", key=f"asp_{r}"):
                deductions += 1
        
        aspects_score = 10 - deductions
        
        if aspects_score >= 7:
            st.metric("ASPECTS 总分", aspects_score, delta="预后良好")
        else:
            st.metric("ASPECTS 总分", aspects_score, delta="- 预后风险高", delta_color="inverse")

    st.divider()

    # --- 决策逻辑输出 ---
    if st.button("🚀 启动溶栓决策预案", use_container_width=True):
        if any([abs_1, abs_2, abs_3, abs_4]):
            st.error("### ❌ 结论：绝对禁忌，禁止溶栓")
            st.info("建议：立即评估血管内治疗（取栓）指征。")
        elif bp_sys >= 185:
            st.warning("### ⚠️ 结论：当前血压过高")
            st.write("请先降压至 185/110 mmHg 以下，平稳后再行溶栓。")
        elif blood_sugar < 2.7:
            st.warning("### ⚠️ 结论：低血糖表现")
            st.write("请纠正低血糖后再重新评估神经功能缺损情况。")
        else:
            st.success("### ✅ 结论：符合溶栓指征")
            
            # 剂量计算逻辑
            st.markdown("---")
            if drug_choice == "rt-PA (爱通立)":
                total_dose = min(weight * 0.9, 90.0)
                bolus = total_dose * 0.1
                infusion = total_dose * 0.9
                st.subheader(f"💊 方案：rt-PA 总量 {total_dose:.1f} mg")
                st.write(f"1. **推注：** {bolus:.1f} mg (1分钟内静脉推注)")
                st.write(f"2. **泵入：** {infusion:.1f} mg (60分钟内连续静脉泵入)")
            else:
                tnk_dose = min(weight * 0.25, 25.0)
                st.subheader(f"💊 方案：TNK 总量 {tnk_dose:.1f} mg")
                st.write(f"1. **推注：** {tnk_dose:.1f} mg (5-10秒内一次性快速推注)")

            if rel_1 or rel_2:
                st.warning("注意：患者存在相对禁忌症，请与家属充分沟通风险收益。")

    # 页脚
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray; font-size: 0.8em;'>"
        "© 2026 田慧军医生版权所有 | 技术支持：NFC Center (Stroke CDSS v12.0)"
        "</div>", 
        unsafe_allow_html=True
    )

# --- 3. 独立运行调试 ---
if __name__ == "__main__":
    # 仅在直接运行此文件时配置页面
    st.set_page_config(page_title="AIS 调试模式", layout="wide")
    show()
