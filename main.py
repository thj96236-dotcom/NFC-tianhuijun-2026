import streamlit as st
from openai import OpenAI
import json
from datetime import datetime, timedelta
import hashlib
import uuid

# --- 1. 核心权限与 AI 配置 ---
def get_machine_id():
    node = uuid.getnode()
    return hashlib.sha256(str(node).encode()).hexdigest()[:12].upper()

# 从 Secrets 获取 DeepSeek API Key
try:
    client = OpenAI(
        api_key = st.secrets["DEEPSEEK_API_KEY"], 
        base_url = "https://api.deepseek.com"
    )
except Exception:
    client = None

# --- 2. 导入子模块 ---
try:
    import nihss
    import thrombolysis
    import bont_manager
    import anticoag_patient
    import anticoag_doctor
except ImportError as e:
    st.error(f"缺少模块文件: {e}")

# --- 3. AI 解析函数 ---
def ai_parser(text):
    if not client:
        st.error("API Key 未配置，请在 Streamlit Secrets 中设置 DEEPSEEK_API_KEY")
        return None
    prompt = f"你是一名资深的神经内科助手。请从以下病历中提取关键决策指标。要求：只输出 JSON 格式。字段：age, gender, onset_hours, imaging_finding, nihss, can_thrombolysis。内容：{text}"
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的医疗数据提取助手。"},
                {"role": "user", "content": prompt}
            ],
            response_format={'type': 'json_object'}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"AI 解析失败: {e}")
        return None

# --- 4. 页面全局配置 ---
st.set_page_config(page_title="NFC 专家决策系统", layout="wide")

def main():
    # 初始化 session_state
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    with st.sidebar:
        st.title("🧠 NFC 专家导航")
        choice = st.radio("功能模块切换", [
            "🏠 系统首页", 
            "🪄 AI 智能解析 (新)",
            "⚖️ NIHSS 自动评分", 
            "⚡ 急诊溶栓决策", 
            "💉 肉毒毒素管理", 
            "🫀 患者抗凝自测", 
            "👨‍⚕️ 医生抗凝决策"
        ])
        st.divider()
        # 授权验证逻辑
        st.subheader("🔐 专业版授权")
        auth_code = st.text_input("输入授权码", type="password")
        if auth_code in ["NFC2026", "TIAN888"]:
            st.session_state['authenticated'] = True
            st.success("专业版已解锁")
        
        st.caption(f"设备识别码: {get_machine_id()}")
        # 更新版本号至 v14.1，以匹配实时 DNT 更新
        st.caption("版本：v14.1 Pro | 田慧军医生作品")

    # --- 逻辑分发 ---
    if choice == "🏠 系统首页":
        st.title("NFC 神经功能整合中心")
        st.info("欢迎使用临床决策辅助系统。请从左侧选择功能模块。")
        st.image("https://img.freepik.com/free-vector/brain-with-digital-circuit-lines_1017-30022.jpg")

    elif choice == "🪄 AI 智能解析 (新)":
        st.title("🪄 AI 病历智能解析")
        raw_text = st.text_area("请粘贴病历文本：", height=250)
        if st.button("开始解析", type="primary"):
            if raw_text:
                with st.spinner("AI 正在解析..."):
                    data = ai_parser(raw_text)
                    if data:
                        st.success("解析成功！")
                        st.json(data)
            else:
                st.warning("请输入文本。")

    elif choice == "⚡ 急诊溶栓决策":
        # 此处调用已包含“实时跳动时间逻辑”的 thrombolysis.show()
        thrombolysis.show()

    elif choice == "⚖️ NIHSS 自动评分": 
        nihss.show()
    elif choice == "💉 肉毒毒素管理": 
        bont_manager.show()
    elif choice == "🫀 患者抗凝自测": 
        anticoag_patient.show()
    elif choice == "👨‍⚕️ 医生抗凝决策": 
        anticoag_doctor.show()

if __name__ == "__main__":
    main()