import streamlit as st
from openai import OpenAI
import json

# 导入您的各版块文件
try:
    import nihss
    import thrombolysis
    import bont_manager
    import anticoag_patient
    import anticoag_doctor
except ImportError as e:
    st.error(f"缺少模块文件: {e}。")

# --- DeepSeek API 配置 ---
client = OpenAI(
    api_key = st.secrets["DEEPSEEK_API_KEY"], 
    base_url = "https://api.deepseek.com"
)

# --- AI 解析函数 ---
def ai_parser(text):
    prompt = f"""
    你是一名资深的神经内科助手。请从以下病历中提取关键决策指标。
    要求：只输出 JSON 格式。
    字段：age, gender, onset_hours, imaging_finding, nihss, can_thrombolysis
    病历内容：{text}
    """
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
        st.error(f"AI 连接失败: {e}")
        return None

# 全局页面配置 (确保此处没有任何旧的参数)
st.set_page_config(page_title="NFC 专家决策系统", layout="wide")

def main():
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
        st.caption("版本：v13.0 | 田慧军医生作品")

    # --- 逻辑分发 ---
    
    if choice == "🏠 系统首页":
        st.title("NFC 神经功能整合中心")
        st.info("欢迎使用临床决策辅助系统。请从左侧选择功能模块。")
        # 使用 2026 标准宽度参数
        st.image("https://img.freepik.com/free-vector/brain-with-digital-circuit-lines_1017-30022.jpg", width="stretch")

    elif choice == "🪄 AI 智能解析 (新)":
        st.title("🪄 AI 病历智能解析")
        raw_text = st.text_area("请粘贴病历或检查报告文本：", height=250)
        if st.button("开始解析", type="primary", width="stretch"):
            if raw_text:
                with st.spinner("AI 正在解析..."):
                    data = ai_parser(raw_text)
                    if data:
                        st.success("解析成功！")
                        c1, c2, c3 = st.columns(3)
                        c1.metric("年龄", f"{data.get('age')} 岁")
                        c2.metric("性别", data.get('gender'))
                        c3.metric("发病时间", f"{data.get('onset_hours')} h")
                        # 结果展示...
            else:
                st.warning("请输入文本。")

    # 调用子模块
    elif choice == "⚖️ NIHSS 自动评分": 
        nihss.show()
    elif choice == "⚡ 急诊溶栓决策": 
        thrombolysis.show()
    elif choice == "💉 肉毒毒素管理": 
        bont_manager.show()
    elif choice == "🫀 患者抗凝自测": 
        anticoag_patient.show()
    elif choice == "👨‍⚕️ 医生抗凝决策": 
        anticoag_doctor.show()

if __name__ == "__main__":
    main()