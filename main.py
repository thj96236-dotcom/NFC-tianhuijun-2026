import streamlit as st
# 导入您的各版块文件
import nihss
import thrombolysis
import bont_manager
import anticoag_patient
import anticoag_doctor

# 全局页面配置
st.set_page_config(page_title="NFC 专家决策系统", layout="wide")

def main():
    with st.sidebar:
        st.title("🧠 NFC 专家导航")
        choice = st.radio("功能模块切换", [
            "🏠 系统首页", 
            "⚖️ NIHSS 自动评分", 
            "⚡ 急诊溶栓决策", 
            "💉 肉毒毒素管理", 
            "🫀 患者抗凝自测", 
            "👨‍⚕️ 医生抗凝决策"
        ])
        st.divider()
        st.caption("版本：v12.0 | 田慧军医生作品")

    # 根据选择，调用对应文件的 show() 函数
    if choice == "🏠 系统首页":
        st.title("NFC 神经功能整合中心")
        st.info("欢迎使用临床决策辅助系统。")
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