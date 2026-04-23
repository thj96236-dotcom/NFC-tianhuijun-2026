import streamlit as st
import pandas as pd
import hashlib
import uuid

# --- 1. 商业授权与管理配置 (保持核心逻辑不动) ---
SECRET_SALT = "PSS_PRO_2026_THJ"
ADMIN_SUPER_PASS = "ADMIN999"

def get_machine_id():
    node = uuid.getnode()
    return hashlib.sha256(str(node).encode()).hexdigest()[:12].upper()

def generate_license(machine_id):
    return hashlib.sha256((machine_id.strip().upper() + SECRET_SALT).encode()).hexdigest()[:8].upper()

def verify_license(user_input, machine_id):
    return user_input.strip().upper() == generate_license(machine_id)

# --- 2. 核心数据库 (严格保留) ---
PSS_DB = {
    "上肢近端 (Proximal Upper Limb)": [
        {"肌肉名称": "胸大肌 (Pectoralis Major)", "范围": "50-150", "标准点数": 4},
        {"肌肉名称": "肩胛下肌 (Subscapularis)", "范围": "50-100", "标准点数": 2},
        {"肌肉名称": "肱二头肌 (Biceps Brachii)", "范围": "50-200", "标准点数": 4},
        {"肌肉名称": "肱肌 (Brachialis)", "范围": "50-100", "标准点数": 2},
        {"肌肉名称": "肱桡肌 (Brachioradialis)", "范围": "25-100", "标准点数": 2},
        {"肌肉名称": "背阔肌 (Latissimus Dorsi)", "范围": "50-100", "标准点数": 3},
        {"肌肉名称": "大圆肌 (Teres Major)", "范围": "25-75", "标准点数": 2}
    ],
    "上肢远端与手部 (Distal UL & Hand)": [
        {"肌肉名称": "旋前圆肌 (Pronator Teres)", "范围": "25-75", "标准点数": 2},
        {"肌肉名称": "旋前方肌 (Pronator Quadratus)", "范围": "10-25", "标准点数": 1},
        {"肌肉名称": "桡侧腕屈肌 (FCR)", "范围": "50-100", "标准点数": 2},
        {"肌肉名称": "尺侧腕屈肌 (FCU)", "范围": "50-100", "标准点数": 2},
        {"肌肉名称": "指浅屈肌 (FDS)", "范围": "50-150", "标准点数": 4},
        {"肌肉名称": "指深屈肌 (FDP)", "范围": "50-150", "标准点数": 4},
        {"肌肉名称": "拇收肌 (Adductor Pollicis)", "范围": "5-15", "标准点数": 1},
        {"肌肉名称": "拇对掌肌 (Opponens Pollicis)", "范围": "5-20", "标准点数": 1},
        {"肌肉名称": "拇短屈肌 (FPB)", "范围": "5-20", "标准点数": 1}
    ],
    "下肢近端 (Proximal Lower Limb)": [
        {"肌肉名称": "股四头肌 (Quadriceps)", "范围": "100-300", "标准点数": 6},
        {"肌肉名称": "股二头肌 (Biceps Femoris)", "范围": "50-150", "标准点数": 3},
        {"肌肉名称": "半腱肌 (Semitendinosus)", "范围": "50-150", "标准点数": 2},
        {"肌肉名称": "半膜肌 (Semimembranosus)", "范围": "50-150", "标准点数": 2},
        {"肌肉名称": "长收肌 (Adductor Longus)", "范围": "50-100", "标准点数": 2},
        {"肌肉名称": "大收肌 (Adductor Magnus)", "范围": "50-150", "标准点数": 4},
        {"肌肉名称": "髂腰肌 (Iliopsoas)", "范围": "50-150", "标准点数": 2}
    ],
    "下肢远端与足部 (Distal LL & Foot)": [
        {"肌肉名称": "腓肠肌 (内/外侧头)", "范围": "100-300", "标准点数": 4},
        {"肌肉名称": "比目鱼肌 (Soleus)", "范围": "50-150", "标准点数": 3},
        {"肌肉名称": "胫骨后肌 (Tibialis Posterior)", "范围": "50-100", "标准点数": 2},
        {"肌肉名称": "胫骨前肌 (Tibialis Anterior)", "范围": "20-50", "标准点数": 2},
        {"肌肉名称": "趾长屈肌 (FDL)", "范围": "25-75", "标准点数": 2},
        {"肌肉名称": "踇长屈肌 (FHL)", "范围": "25-75", "标准点数": 2},
        {"肌肉名称": "踇展肌 (Abductor Hallucis)", "范围": "10-30", "标准点数": 1},
        {"肌肉名称": "踇短屈肌 (FHB)", "范围": "10-25", "标准点数": 1}
    ]
}

SPASTICITY_PATTERNS = {
    "上肢-内收内旋型": ["胸大肌", "肩胛下肌", "背阔肌"],
    "上肢-屈肘型": ["肱二头肌", "肱肌", "肱桡肌"],
    "上肢-前臂旋前型": ["旋前圆肌", "旋前方肌"],
    "上肢-屈腕握拳型": ["桡侧腕屈肌", "指浅屈肌", "指深屈肌", "拇收肌"],
    "下肢-屈髋型": ["髂腰肌", "股直肌"],
    "下肢-剪刀步/内收型": ["长收肌", "大收肌", "股薄肌"],
    "下肢-膝过伸/屈膝型": ["股四头肌", "腘绳肌(半腱/半膜/股二头)"],
    "下肢-马蹄内翻足": ["腓肠肌", "比目鱼肌", "胫骨后肌", "踇长屈肌"]
}

# --- 4. 模块封装函数 ---
def bont_manager_module():
    st.title("卒中后痉挛 (PSS) 全流程标准化注射管理系统")
    
    mid = get_machine_id()
    if 'is_pro' not in st.session_state: 
        st.session_state['is_pro'] = False

    with st.sidebar:
        st.header("🛡️ 授权与激活")
        st.info(f"本机识别码: **{mid}**")
        
        lic_input = st.text_input("输入授权码解锁专业版", type="password", key="pss_lic_input")
        
        if lic_input == ADMIN_SUPER_PASS:
            st.divider()
            st.warning("🛠️ 管理员模式已开启")
            customer_mid = st.text_input("在此输入客户的【识别码】", key="admin_cust_mid")
            if customer_mid:
                new_code = generate_license(customer_mid)
                st.code(f"生成的授权码: {new_code}", language="text")
                st.success("请将上方代码发给对应用户。")
        elif lic_input:
            if verify_license(lic_input, mid):
                st.session_state['is_pro'] = True
                st.success("✅ 专业版已激活")
            else:
                st.error("❌ 授权码无效")

        st.divider()
        brand = st.selectbox("肉毒毒素品牌", ["保妥适 (Botox)", "衡力 (Hengli)"], key="pss_brand")

    all_regs = list(PSS_DB.keys())
    available_regs = all_regs if st.session_state['is_pro'] else [r for r in all_regs if "上肢" in r]

    col_s, col_r = st.columns(2)
    with col_s: 
        side = st.radio("注射侧别", ["左侧 (Left)", "右侧 (Right)"], horizontal=True, key="pss_side")
    with col_r: 
        scope = st.multiselect("评估区域", available_regs, default=available_regs[0] if available_regs else None, key="pss_scope")

    with st.expander("📖 常见痉挛模式参考"):
        for pat, mus in SPASTICITY_PATTERNS.items():
            if not st.session_state['is_pro'] and "下肢" in pat: 
                continue
            st.info(f"**{pat}**：{', '.join(mus)}")

    st.divider()

    current_final_list = []
    for region in scope:
        st.subheader(f"📍 {side} - {region}")
        m_data = PSS_DB[region]
        h_cols = st.columns([3, 2, 2, 1.5])
        h_cols[0].write("**靶肌肉**")
        h_cols[1].write("**指南范围**")
        h_cols[2].write("**拟注剂量**")
        h_cols[3].write("**点数**")
        
        for m in m_data:
            r_cols = st.columns([3, 2, 2, 1.5])
            # 使用 side + region + 肌肉名 组合 key，确保唯一性
            unique_key = f"{side}_{region}_{m['肌肉名称']}"
            with r_cols[0]: 
                active = st.checkbox(m["肌肉名称"], key=f"check_{unique_key}")
            with r_cols[1]: 
                st.caption(f"{m['范围']} U")
            with r_cols[2]: 
                dose = st.number_input("剂量", step=5.0, key=f"dose_{unique_key}", label_visibility="collapsed", disabled=not active)
            with r_cols[3]: 
                st.markdown(f"**{m['标准点数']}**")
            
            if active:
                current_final_list.append({
                    "侧别": side, "区域": region, "肌肉名称": m["肌肉名称"],
                    "总剂量(U)": dose, "注射点数": m["标准点数"],
                    "单点剂量": round(dose/m['标准点数'], 1) if dose > 0 else 0
                })

    if current_final_list:
        st.divider()
        st.header("📊 本次注射方案最终汇总")
        df = pd.DataFrame(current_final_list)
        total_u = df["总剂量(U)"].sum()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("累计总剂量", f"{total_u} U")
        m2.metric("勾选肌肉数", f"{len(df)} 块")
        with m3:
            if total_u > 600: st.error("🚨 警告：超过 600U 安全剂量")
            else: st.success("✅ 安全剂量范围内")

        st.dataframe(df, use_container_width=True, hide_index=True)
        if st.session_state['is_pro']:
            st.download_button("📥 导出方案 (CSV)", df.to_csv(index=False).encode('utf-8-sig'), f"Summary_{side}.csv", key="pss_download")
    else:
        st.info("请在上方勾选肌肉并录入剂量，汇总表将在此处自动生成。")

    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 0.8em;'>
            © 2026 田慧军医生版权所有 | 技术支持：NFC Center
        </div>
        """, 
        unsafe_allow_html=True
    )

# --- 5. 独立执行逻辑 (用于单独测试此模块) ---
if __name__ == "__main__":
    st.set_page_config(page_title="PSS BoNT-Manager", layout="wide")
    bont_manager_module()