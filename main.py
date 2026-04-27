import streamlit as st
from openai import OpenAI
import json

# 导入您的各版块文件 (确保这些文件在同一目录下)
try:
    import nihss
    import thrombolysis
    import bont_manager
    import anticoag_patient
    import anticoag_doctor
except ImportError as e:
    st.error(f"缺少模块文件: {e}. 请确保 nihss.py 等文件与 main.py 在同一文件夹。")

# --- DeepSeek API 配置 ---
# 修改前：api_key="sk-8c4d..."
# 修改后：从 Streamlit 的云端配置里读取
client = OpenAI(
    api_key = st.secrets["DEEPSEEK_API_KEY"], 
    base_url = "https://api.deepseek.com"
)

# --- AI 解析函数 ---
def ai_parser(text):
    prompt = f"""
    你是一名资深的神经内科助手。请从以下病历中提取关键决策指标。
    要求：只输出 JSON 格式。
    字段：
    - age: 年龄(数字)
    - gender: 性别
    - onset_hours: 发病时间(数字，如果是2小时就写2)
    - imaging_finding: 影像学发现(如：大面积脑梗死)
    - nihss: NIHSS评分(如果没有提到，设为null)
    - can_thrombolysis: 是否符合溶栓时间窗(true/false)

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
        # 这里会捕获余额不足(402)等错误
        st.error(f"AI 连接失败或余额不足: {e}")
        return None

# 全局页面配置
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
        # 修复了截图中的警告，使用了 use_container_width
        st.image("https://img.freepik.com/free-vector/brain-with-digital-circuit-lines_1017-30022.jpg", use_container_width=True)

    elif choice == "🪄 AI 智能解析 (新)":
        st.title("🪄 AI 病历智能解析")
        st.write("通过粘贴病历，自动提取关键临床数据（基于 DeepSeek 引擎）。")
        
        raw_text = st.text_area("请粘贴病历或检查报告文本：", height=250, placeholder="例如：姓名张三，女，80岁，因言语不利2小时入院，查脑CT提示大面积脑梗死。")
        
        if st.button("开始解析", type="primary"):
            if raw_text:
                with st.spinner("AI 正在深度阅读病历..."):
                    data = ai_parser(raw_text)
                    if data:
                        st.success("解析成功！请核对以下临床数据：")
                        # 更加美观的数据展示
                        c1, c2, c3 = st.columns(3)
                        c1.metric("年龄", f"{data.get('age')} 岁")
                        c2.metric("性别", data.get('gender'))
                        c3.metric("发病时间", f"{data.get('onset_hours')} h")
                        
                        c4, c5, c6 = st.columns(3)
                        c4.metric("NIHSS评分", data.get('nihss') if data.get('nihss') else "未提及")
                        c5.write("**影像学发现：**")
                        st.warning(data.get('imaging_finding'))
                        
                        thrombo_status = "✅ 窗口期内" if data.get('can_thrombolysis') else "❌ 超出窗口期"
                        c6.metric("溶栓时间窗状态", thrombo_status)
                        
                        with st.expander("点击查看原始 JSON 报文"):
                            st.json(data)
            else:
                st.warning("请输入病历文本。")

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