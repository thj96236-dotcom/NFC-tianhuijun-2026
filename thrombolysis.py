import streamlit as st
from datetime import datetime, timedelta
import hashlib
import uuid

# --- 1. 核心权限工具函数 ---
def get_machine_id():
    node = uuid.getnode()
    return hashlib.sha256(str(node).encode()).hexdigest()[:12].upper()

# --- 2. 主模块函数 ---
def show():
    if 'authenticated' not in st.session_state: 
        st.session_state['authenticated'] = False
    
    # 修正 DNT 逻辑：增加锁定状态，确保未给药前不计算固定 DNT
    if 'needle_time' not in st.session_state:
        st.session_state['needle_time'] = None

    VALID_CODES = ["NFC2026", "TIAN888", "STROKE2026"] 

    st.title("🧠 急性缺血性卒中 (AIS) 专家决策中心")
    
    # 侧边栏：授权管理
    with st.sidebar:
        st.header("🔐 授权验证")
        auth_code = st.text_input("🔑 输入专业版授权码", type="password", key="th_auth_key")
        if auth_code in VALID_CODES:
            st.session_state['authenticated'] = True
            st.success("✨ 专业版已解锁")
        
        st.divider()
        st.info(f"设备识别码: {get_machine_id()}")
        # 适配 2026 API: 使用 width="stretch" 彻底解决警告
        if st.button("🔄 重置/接诊新病人", width="stretch"):
            st.session_state['needle_time'] = None
            st.rerun()

    # 布局：左侧临床指标，右侧评分量表
    col_left, col_right = st.columns([2, 1])

    with col_left:
        # 1. 质控时间轴 (DNT 管理)
        with st.expander("⏱️ 1. 质控时间轴 (DNT 管理)", expanded=True):
            t1, t2 = st.columns(2)
            with t1:
                arrival_date = st.date_input("到院日期", datetime.now(), key="th_d")
                arrival_time = st.time_input("到院时刻", datetime.now() - timedelta(minutes=30), key="th_t")
                onset_dt = datetime.combine(st.date_input("发病时刻", datetime.now()), 
                                          st.time_input("发病具体时间", datetime.now() - timedelta(hours=2)))
            with t2:
                arrival_dt = datetime.combine(arrival_date, arrival_time)
                # DNT 锁定逻辑：只有手动锁定后才显示最终 DNT
                if st.session_state['needle_time'] is None:
                    st.write("**当前决策参考时刻**")
                    st.subheader(datetime.now().strftime("%H:%M:%S"))
                    if st.button("💉 确认开始用药 (锁定 DNT)", width="stretch"):
                        st.session_state['needle_time'] = datetime.now()
                        st.rerun()
                else:
                    st.success("**✅ 锁定 DNT 结果**")
                    final_dnt = int((st.session_state['needle_time'] - arrival_dt).total_seconds() / 60)
                    st.metric("最终 DNT", f"{final_dnt} min", delta="合格" if final_dnt <= 45 else "超时", delta_color="normal" if final_dnt <= 45 else "inverse")

            # 计算 ONT (发病至今的小时数)
            ont_val = (datetime.now() - onset_dt).total_seconds() / 3600

        # 2. 核心临床指标
        with st.expander("📋 2. 患者核心临床指标", expanded=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                weight = st.number_input("体重 (kg)", 30.0, 150.0, 65.0, step=0.5)
                is_lvo = st.checkbox("疑似大血管闭塞 (LVO)")
            with c2:
                nihss = st.slider("NIHSS 评分", 0, 42, 4)
                bp_sys = st.number_input("收缩压 (mmHg)", 80, 240, 140)
            with c3:
                blood_sugar = st.number_input("血糖 (mmol/L)", 1.0, 30.0, 6.0, step=0.1)
                # 保留完整的药物选项
                drug_choice = st.selectbox("拟选药物", ["rt-PA (爱通立)", "TNK (替奈普酶)"])

        # 3. 禁忌症筛查 (完整保留，不可删除)
        with st.expander("🚩 3. 核心禁忌症与警示 (一键核查)", expanded=True):
            st.markdown("##### **绝对禁忌症 (严禁溶栓)**")
            abs_1 = st.checkbox("CT发现颅内出血 / ASPECTS < 5")
            abs_2 = st.checkbox("既往所有颅内出血史 (ICH)")
            abs_3 = st.checkbox("近3个月重大颅脑外伤或卒中史")
            abs_4 = st.checkbox("活动性内出血 / 严重出血体质")
            
            st.markdown("##### **相对禁忌证 (临床权衡)**")
            rel_1 = st.checkbox("症状轻微且快速改善 (非致残性)")
            rel_2 = st.checkbox("妊娠期 / 近2周重大手术或创伤")

        # 4. 专业版扩展评估 (2026 影像错配逻辑)
        if st.session_state['authenticated']:
            with st.expander("🔬 4. 2026 影像不匹配 (Mismatch) 评估", expanded=True):
                m1 = st.toggle("CTP 错配 (半暗带体积/梗死核心体积 > 1.8)")
                m2 = st.toggle("MRI 错配 (DWI-FLAIR 不匹配 / 唤醒卒中)")
                is_mismatch = m1 or m2
        else:
            is_mismatch = False

    with col_right:
        # ASPECTS 评分系统 (免费版完整开放)
        st.subheader("🖼️ ASPECTS 评分")
        st.caption("勾选受损区域（每项减1分）")
        regions = ["C (尾状核)", "L (豆状核)", "IC (内囊)", "I (岛叶)", "M1", "M2", "M3", "M4", "M5", "M6"]
        deductions = sum([1 for r in regions if st.checkbox(f"受损: {r}", key=f"asp_{r}")])
        aspects_score = 10 - deductions
        st.metric("ASPECTS 总分", aspects_score, delta="高危" if aspects_score < 7 else "良好", delta_color="inverse" if aspects_score < 7 else "normal")

    st.divider()

    # --- 3. 决策逻辑输出端 (包含 2026 指南深度报告) ---
    if st.button("🚀 启动溶栓决策预案", width="stretch"):
        
        # A. 基础安全性拦截
        if any([abs_1, abs_2, abs_3, abs_4]):
            st.error("### ❌ 结论：存在绝对禁忌，禁止溶栓")
        elif bp_sys >= 185:
            st.warning("### ⚠️ 结论：当前血压过高 (≥185/110mmHg)，请先平稳降压。")
        elif blood_sugar < 2.7:
            st.warning("### ⚠️ 结论：低血糖表现，请纠正后再评估。")
        
        # B. 时间窗纠正逻辑：严格拦截 ONT > 4.5h 且无影像证据的情况
        elif ont_val > 4.5 and not (st.session_state['authenticated'] and is_mismatch):
            st.error(f"### ❌ 结论：超出标准时间窗 (ONT: {ont_val:.1f}h)")
            st.info("提示：发病已超过标准 4.5h 窗口。若无专业版授权或 Mismatch 影像错配证据，不可溶栓。")

        # C. 符合指征的决策产出
        else:
            if not st.session_state['authenticated']:
                # 免费版输出
                st.success(f"### ✅ 结论：符合标准溶栓指征 (ONT: {ont_val:.1f}h)")
                total = min(weight * 0.9, 90.0) if drug_choice == "rt-PA (爱通立)" else min(weight * 0.25, 25.0)
                st.write(f"**{drug_choice} 推荐剂量：** {total:.2f} mg")
            else:
                # 专业版深度报告 (2026 指南分层)
                st.subheader("🔬 2026 指南深度分层决策报告")
                
                # 建议 1: 时间窗与不匹配
                if 4.5 < ont_val <= 9.0:
                    st.success(f"【建议 1】ONT {ont_val:.1f}h。影像错配评估阳性，符合扩展窗溶栓指征。")
                else:
                    st.success(f"【建议 1】ONT {ont_val:.1f}h。处于黄金时间窗，支持标准溶栓治疗。")

                # 建议 2: LVO 与药物
                if is_lvo:
                    st.warning("【建议 2】疑似大血管闭塞 (LVO)。推荐首选 TNK 溶栓以提高再通率，并准备桥接介入。")
                
                # 建议 3: 轻型卒中
                if nihss < 4:
                    st.warning("【建议 3】NIHSS < 4 分。请确认为非致残性卒中，必要时考虑双抗替代方案。")

                # 建议 4: 预后分层
                if aspects_score < 7:
                    st.error(f"【建议 4】ASPECTS {aspects_score} 分。提示早期改变显著，溶栓后脑出血风险为高危分层。")
                else:
                    st.success("【建议 4】ASPECTS 评分理想，预期溶栓获益良好。")

                st.markdown("---")
                # 剂量与监测汇总
                c_a, c_b = st.columns(2)
                with c_a:
                    if drug_choice == "rt-PA (爱通立)":
                        total = min(weight * 0.9, 90.0)
                        st.metric("rt-PA 方案", f"{total:.1f} mg")
                        st.caption(f"用法：10% 推注 ({total*0.1:.1f}mg)，90% 泵入1h")
                    else:
                        tnk = min(weight * 0.25, 25.0)
                        st.metric("TNK 方案", f"{tnk:.2f} mg")
                        st.caption("用法：5-10s 内一次性静脉快速推注")
                with c_b:
                    st.write("**围溶栓期血压监测要点：**")
                    st.write("- 目标：≤ 180/105 mmHg")
                    st.write("- 频次：前2h (q15min), 随后6h (q30min), 至24h (q1h)")

    # 页脚
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: gray; font-size: 0.8em;'>© 2026 田慧军医生 | NFC Center (Stroke CDSS v13.0 Pro)</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    if "config_check" not in st.session_state:
        st.set_page_config(page_title="AIS 专家决策中心", layout="wide")
        st.session_state.config_check = True
    show()
