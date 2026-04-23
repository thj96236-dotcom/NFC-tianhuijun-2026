import streamlit as st
import streamlit.components.v1 as components

def show():
    # 局部页面标题
    st.markdown("### NIHSS 临床自动评分 system (NFC 2026 版)")

    # 完整 HTML/JS/CSS 逻辑
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
      *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
      :root {
        --bg: #ffffff; --bg2: #f5f5f2; --bg3: #efefeb;
        --text: #1a1a18; --text2: #6b6b67; --text3: #9a9a96;
        --border: rgba(0,0,0,0.12); --border2: rgba(0,0,0,0.22);
        --radius: 8px; --radius-lg: 12px;
        --primary: #185FA5;
        --warning: #c53030;
      }
      body { font-family: -apple-system, system-ui, sans-serif; background: var(--bg3); color: var(--text); font-size: 14px; padding: 10px; }
      .app { max-width: 900px; margin: 0 auto; padding-bottom: 50px; }
      
      .header { margin-bottom: 1.5rem; display: flex; align-items: flex-start; justify-content: space-between; flex-wrap: wrap; gap: 1rem; }
      .header h1 { font-size: 22px; font-weight: 600; margin-bottom: 4px; color: var(--primary); }
      .header p { font-size: 13px; color: var(--text2); }
      .badge { padding: 3px 10px; border-radius: var(--radius); font-size: 12px; font-weight: 500; }
      .badge-pro { background: #EEEDFE; color: #534AB7; }

      .card { background: var(--bg); border: 0.5px solid var(--border); border-radius: var(--radius-lg); padding: 20px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
      .card-title { font-size: 13px; font-weight: 700; color: var(--text2); text-transform: uppercase; border-bottom: 1px solid var(--bg3); padding-bottom: 8px; margin-bottom: 15px; }
      
      .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
      @media (max-width: 600px) { .grid-2 { grid-template-columns: 1fr; } }
      
      .item { margin-bottom: 12px; }
      .item label { display: block; font-weight: 500; margin-bottom: 5px; font-size: 14px; }
      .hint-text { font-size: 12px; color: var(--warning); margin-bottom: 5px; display: none; font-style: italic; }

      select, input { 
        width: 100%; height: 38px; border: 1px solid var(--border2); border-radius: var(--radius); 
        padding: 0 10px; font-size: 14px; outline: none; background: #fff;
      }
      select:focus { border-color: var(--primary); }

      .score-tag { float: right; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
      .score-0 { background: #EAF3DE; color: #3B6D11; }
      .score-1 { background: #FAEEDA; color: #854F0B; }
      .score-high { background: #FCEBEB; color: #A32D2D; }

      .result-panel { background: #1a1a1a; color: #fff; border-radius: var(--radius-lg); padding: 25px; margin-top: 20px; }
      .res-grid { display: flex; justify-content: space-around; text-align: center; margin-bottom: 20px; }
      .res-val { font-size: 42px; font-weight: bold; line-height: 1; }
      .res-label { font-size: 12px; opacity: 0.7; margin-top: 5px; }
      
      .disclaimer { 
        background: rgba(255,255,255,0.05); border-left: 3px solid var(--warning); padding: 15px; margin-top: 15px; font-size: 12px; line-height: 1.6; color: #ccc;
      }
      .copyright-tag { 
        text-align: center; font-size: 11px; color: var(--text3); margin-top: 20px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.1);
      }

      .btn-row { margin-top: 20px; display: flex; gap: 10px; }
      .btn { flex: 1; height: 40px; border-radius: var(--radius); border: none; cursor: pointer; font-weight: 600; transition: 0.2s; }
      .btn-primary { background: var(--primary); color: white; }
      .btn-outline { background: #fff; border: 1px solid var(--border2); }
      
      .coma-box { background: #fff5f5; border: 1px solid #feb2b2; padding: 15px; border-radius: 8px; margin-bottom: 15px; color: #c53030; font-size: 13px; }
      
      @media print {
        .header, .btn-row { display: none !important; }
        body { background: white; padding: 0; }
        .card, .result-panel { box-shadow: none; border: 1px solid #eee; color: black !important; background: white; }
        .res-val, .res-label, .disclaimer, .copyright-tag { color: black !important; }
      }
    </style>
    </head>
    <body>
    <div class="app">
      <div class="header">
        <div>
          <h1>NIHSS 自动评分工具</h1>
          <p>National Institutes of Health Stroke Scale</p>
        </div>
        <div>
          <span class="badge badge-pro">专业版 (已激活)</span>
        </div>
      </div>

      <div class="card">
        <div class="card-title">基础资料与设置</div>
        <div class="grid-2">
          <div class="item"><label>患者姓名</label><input type="text" id="p-name" placeholder="请输入姓名"></div>
          <div class="item"><label>评估时间</label><input type="datetime-local" id="p-time"></div>
        </div>
        <div class="grid-2" style="margin-top:10px;">
          <div class="item">
            <label>评估模式</label>
            <select id="p-type" onchange="toggleForm()">
                <option value="normal">常规 NIHSS 评估</option>
                <option value="coma">昏迷/无反应患者 (自动计分项)</option>
            </select>
          </div>
          <div class="item">
            <label>发病侧别</label>
            <select id="p-side">
                <option value="未知">未知/未说明</option>
                <option value="左侧">左侧</option>
                <option value="右侧">右侧</option>
                <option value="双侧">双侧</option>
            </select>
          </div>
        </div>
      </div>

      <div id="normal-form">
        <div class="card">
          <div class="card-title">1. 意识与定向</div>
          <div class="item"><label>1a. 意识水平 <span id="v1a" class="score-tag score-0">0</span></label><select id="s1a" onchange="calc()"><option value="0">0 - 清醒</option><option value="1">1 - 嗜睡</option><option value="2">2 - 昏睡</option><option value="3">3 - 昏迷</option></select></div>
          <div class="item"><label>1b. 意识提问 <span id="v1b" class="score-tag score-0">0</span></label><select id="s1b" onchange="calc()"><option value="0">0 - 两项正确</option><option value="1">1 - 一项正确</option><option value="2">2 - 均错/失语</option></select></div>
          <div class="item"><label>1c. 意识指令 <span id="v1c" class="score-tag score-0">0</span></label><select id="s1c" onchange="calc()"><option value="0">0 - 两项正确</option><option value="1">1 - 一项正确</option><option value="2">2 - 均错</option></select></div>
        </div>

        <div class="card">
          <div class="card-title">2-3. 眼动与视野</div>
          <div class="item"><label>2. 最佳凝视 <span id="v2" class="score-tag score-0">0</span></label><select id="s2" onchange="calc()"><option value="0">0 - 正常</option><option value="1">1 - 部分凝视麻痹： 一眼或双眼出现水平性眼球运动异常（如凝视麻痹），但通过主动性或反射性刺激可以克服</option><option value="2">2 - 完全麻痹 出现强迫性眼球偏斜，且不能通过反射性活动克服</option></select></div>
          <div class="item"><label>3. 视野 <span id="v3" class="score-tag score-0">0</span></label><select id="s3" onchange="calc()"><option value="0">0 - 无缺失</option><option value="1">1 - 部分偏盲</option><option value="2">2 - 完全偏盲</option><option value="3">3 - 双侧偏盲</option></select></div>
        </div>

        <div class="card">
          <div class="card-title">4-6. 运动功能</div>
          <div class="item"><label>4. 面瘫 <span id="v4" class="score-tag score-0">0</span></label><select id="s4" onchange="calc()"><option value="0">0 - 正常</option><option value="1">1 - 轻微</option><option value="2">2 - 部分</option><option value="3">3 - 完全</option></select></div>
          <div class="grid-2">
            <div class="item"><label>5a. 左上肢 <span id="v5a" class="score-tag score-0">0</span></label><select id="s5a" onchange="calc()"><option value="0">0 - 无漂移</option><option value="1">1 - 漂移</option><option value="2">2 - 抗重力下落</option><option value="3">3 - 不能抗重力</option><option value="4">4 - 无动作</option></select></div>
            <div class="item"><label>5b. 右上肢 <span id="v5b" class="score-tag score-0">0</span></label><select id="s5b" onchange="calc()"><option value="0">0 - 无漂移</option><option value="1">1 - 漂移</option><option value="2">2 - 抗重力下落</option><option value="3">3 - 不能抗重力</option><option value="4">4 - 无动作</option></select></div>
            <div class="item"><label>6a. 左下肢 <span id="v6a" class="score-tag score-0">0</span></label><select id="s6a" onchange="calc()"><option value="0">0 - 无漂移</option><option value="1">1 - 漂移</option><option value="2">2 - 抗重力下落</option><option value="3">3 - 不能抗重力</option><option value="4">4 - 无动作</option></select></div>
            <div class="item"><label>6b. 右下肢 <span id="v6b" class="score-tag score-0">0</span></label><select id="s6b" onchange="calc()"><option value="0">0 - 无漂移</option><option value="1">1 - 漂移</option><option value="2">2 - 抗重力下落</option><option value="3">3 - 不能抗重力</option><option value="4">4 - 无动作</option></select></div>
          </div>
        </div>

        <div class="card">
          <div class="card-title">7-11. 协调、感觉与语言</div>
          <div class="item">
            <label>7. 共济失调 <span id="v7" class="score-tag score-0">0</span></label>
            <div id="ataxia-hint" class="hint-text">⚠️ 提示：肢体瘫痪严重无法测试时记0分。</div>
            <select id="s7" onchange="calc()"><option value="0">0 - 无</option><option value="1">1 - 一个肢体有</option><option value="2">2 - 两个以上有</option></select>
          </div>
          <div class="item"><label>8. 感觉 <span id="v8" class="score-tag score-0">0</span></label><select id="s8" onchange="calc()"><option value="0">0 - 正常</option><option value="1">1 - 轻中度</option><option value="2">2 - 重度缺失</option></select></div>
          <div class="item"><label>9. 语言 <span id="v9" class="score-tag score-0">0</span></label><select id="s9" onchange="calc()"><option value="0">0 - 无失语</option><option value="1">1 - 轻中度失语</option><option value="2">2 - 重度失语</option><option value="3">3 - 全失语/哑</option></select></div>
          <div class="item"><label>10. 构音障碍 <span id="v10" class="score-tag score-0">0</span></label><select id="s10" onchange="calc()"><option value="0">0 - 正常</option><option value="1">1 - 轻中度</option><option value="2">2 - 重度/哑</option><option value="0">UN - 插管/物理障碍(0分)</option></select></div>
          <div class="item"><label>11. 忽视 <span id="v11" class="score-tag score-0">0</span></label><select id="s11" onchange="calc()"><option value="0">0 - 无忽视</option><option value="1">1 - 部分忽视</option><option value="2">2 - 严重忽视</option></select></div>
        </div>
      </div>

      <div id="coma-form" style="display:none">
        <div class="coma-box">
            <strong>昏迷/无反应患者自动计分：</strong><br>
            视野(3)、语言(9)、意识(7)、感觉/构音/忽视(6)已根据临床指南自动合计：19分。
        </div>
        <div class="card">
            <div class="card-title">昏迷必填项评估</div>
            <div class="item">
                <label>2. 凝视 (眼头反射) <span id="cv2" class="score-tag score-0">0</span></label>
                <select id="cs2" onchange="calc()"><option value="0">0 - 正常</option><option value="1">1 - 部分麻痹存在凝视异常，但可通过自主运动或反射性头眼运动纠正</option><option value="2">2 - 完全麻痹眼球偏向一侧，且不能被头眼反射纠正</option></select>
            </div>
            <div class="item">
                <label>4. 面部动作 (痛刺激) <span id="cv4" class="score-tag score-high">3</span></label>
                <select id="cs4" onchange="calc()"><option value="3">3 - 完全麻痹</option><option value="2">2 - 极微弱反应</option><option value="1">1 - 轻微不对称</option></select>
            </div>
            <div class="item">
                <label>5/6. 四肢运动 (痛刺激) <span id="cv56" class="score-tag score-high">16</span></label>
                <select id="cs56" onchange="calc()"><option value="16">16 - 四肢均无动作</option><option value="12">12 - 仅单侧有动作</option><option value="8">8 - 仅双下肢有动作</option><option value="4">4 - 三肢无动作</option></select>
            </div>
        </div>
      </div>

      <div class="result-panel">
        <div class="res-grid">
          <div><div class="res-val" id="total-score">0</div><div class="res-label">NIHSS 总分</div></div>
          <div><div class="res-val" style="font-size:24px; padding-top:10px" id="severity-label">正常</div><div class="res-label">严重程度划分</div></div>
        </div>
        <div class="disclaimer">
          <strong>风险告知：</strong> 本量表仅供临床辅助参考。最终结论由主治医师判定。
        </div>
        <div class="copyright-tag">版权所有 © 田慧军医生 | 2026 </div>
        <div class="btn-row">
            <button class="btn btn-primary" onclick="window.print()">打印报告</button>
            <button class="btn btn-outline" onclick="location.reload()">重新评估</button>
        </div>
      </div>
    </div>

    <script>
    function setCurrentTime() {
        const now = new Date();
        const offset = now.getTimezoneOffset() * 60000;
        const localISOTime = (new Date(now - offset)).toISOString().slice(0, 16);
        document.getElementById('p-time').value = localISOTime;
    }
    function toggleForm() {
        const type = document.getElementById('p-type').value;
        document.getElementById('normal-form').style.display = (type === 'normal') ? 'block' : 'none';
        document.getElementById('coma-form').style.display = (type === 'coma') ? 'block' : 'none';
        calc();
    }
    function calc() {
        const type = document.getElementById('p-type').value;
        let total = 0;
        if (type === 'normal') {
            const m5a = parseInt(document.getElementById('s5a').value) || 0;
            const m5b = parseInt(document.getElementById('s5b').value) || 0;
            const m6a = parseInt(document.getElementById('s6a').value) || 0;
            const m6b = parseInt(document.getElementById('s6b').value) || 0;
            const s7 = document.getElementById('s7');
            const hint = document.getElementById('ataxia-hint');

            // 核心修改逻辑：肢体评分 >= 3，共济失调强制为0
            if (m5a >= 3 || m5b >= 3 || m6a >= 3 || m6b >= 3) {
                s7.value = "0";
                s7.disabled = true;
                hint.style.display = 'block';
            } else {
                s7.disabled = false;
                hint.style.display = 'none';
            }

            const ids = ['1a','1b','1c','2','3','4','5a','5b','6a','6b','7','8','9','10','11'];
            ids.forEach(id => {
                const el = document.getElementById('s' + id);
                const val = parseInt(el ? el.value : 0) || 0;
                total += val;
                const tag = document.getElementById('v' + id);
                if(tag) tag.innerText = val;
            });
        } else {
            total = 19; 
            const cids = ['cs2', 'cs4', 'cs56'];
            cids.forEach(id => {
                const el = document.getElementById(id);
                const val = parseInt(el ? el.value : 0) || 0;
                total += val;
                const tag = document.getElementById('cv' + id.substring(2));
                if(tag) tag.innerText = val;
            });
        }
        document.getElementById('total-score').innerText = total;
        let sev = total >= 21 ? "重度卒中" : total >= 16 ? "中重度卒中" : total >= 5 ? "中度卒中" : total >= 1 ? "轻度卒中" : "正常";
        document.getElementById('severity-label').innerText = sev;
    }
    window.onload = function() { setCurrentTime(); calc(); };
    </script>
    </body>
    </html>
    """

    components.html(html_content, height=1800, scrolling=True)

if __name__ == "__main__":
    show()