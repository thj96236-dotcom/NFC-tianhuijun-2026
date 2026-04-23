import streamlit as st
import streamlit.components.v1 as components

# 该文件由 main.py 调用
def show():
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

      .card { background: var(--bg); border: 0.5px solid var(--border); border-radius: var(--radius-lg); padding: 20px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
      .card-title { font-size: 13px; font-weight: 700; color: var(--text2); text-transform: uppercase; border-bottom: 1px solid var(--bg3); padding-bottom: 8px; margin-bottom: 15px; }
      
      .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
      @media (max-width: 600px) { .grid-2 { grid-template-columns: 1fr; } }
      
      .item { margin-bottom: 12px; }
      .item label { display: block; font-weight: 500; margin-bottom: 5px; font-size: 14px; }
      .hint-text { font-size: 12px; color: var(--warning); margin-bottom: 5px; display: none; font-style: italic; font-weight: bold; }

      select, input { 
        width: 100%; height: 38px; border: 1px solid var(--border2); border-radius: var(--radius); 
        padding: 0 10px; font-size: 14px; outline: none; background: #fff;
      }

      .score-tag { float: right; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
      .score-0 { background: #EAF3DE; color: #3B6D11; }
      .score-1 { background: #FAEEDA; color: #854F0B; }
      .score-high { background: #FCEBEB; color: #A32D2D; }

      .result-panel { background: #1a1a1a; color: #fff; border-radius: var(--radius-lg); padding: 25px; margin-top: 20px; }
      .res-grid { display: flex; justify-content: space-around; text-align: center; margin-bottom: 20px; }
      .res-val { font-size: 42px; font-weight: bold; line-height: 1; }
      .res-label { font-size: 12px; opacity: 0.7; margin-top: 5px; }
      
      .btn-row { margin-top: 20px; display: flex; gap: 10px; }
      .btn { flex: 1; height: 40px; border-radius: var(--radius); border: none; cursor: pointer; font-weight: 600; transition: 0.2s; }
      .btn-primary { background: var(--primary); color: white; }
      .btn-outline { background: #fff; border: 1px solid var(--border2); }
    </style>
    </head>
    <body>
    <div class="app">
      <div class="header">
        <div>
          <h1>NIHSS 自动评分工具 (V12.2)</h1>
          <p>National Institutes of Health Stroke Scale</p>
        </div>
      </div>

      <div class="card">
        <div class="card-title">1. 意识水平</div>
        <div class="item">
          <label>1a. 意识水平 <span id="v1a" class="score-tag score-0">0</span></label>
          <select id="s1a" onchange="calc()"><option value="0">0 - 清醒</option><option value="1">1 - 嗜睡</option><option value="2">2 - 昏睡</option><option value="3">3 - 昏迷</option></select>
        </div>
        <div class="grid-2">
            <div class="item"><label>1b. 意识提问 <span id="v1b" class="score-tag score-0">0</span></label><select id="s1b" onchange="calc()"><option value="0">0 - 两项正确</option><option value="1">1 - 一项正确</option><option value="2">2 - 均错/失语</option></select></div>
            <div class="item"><label>1c. 意识指令 <span id="v1c" class="score-tag score-0">0</span></label><select id="s1c" onchange="calc()"><option value="0">0 - 两项正确</option><option value="1">1 - 一项正确</option><option value="2">2 - 均错</option></select></div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">2-3. 眼动与视野</div>
        <div class="item">
            <label>2. 最佳凝视 (主动或反射性刺激) <span id="v2" class="score-tag score-0">0</span></label>
            <select id="s2" onchange="calc()">
                <option value="0">0 - 正常</option>
                <option value="1">1 - 部分凝视麻痹 (一眼或两眼异常，但无强迫性偏斜)</option>
                <option value="2">2 - 强迫性偏斜或完全凝视麻痹</option>
            </select>
        </div>
        <div class="item"><label>3. 视野 <span id="v3" class="score-tag score-0">0</span></label><select id="s3" onchange="calc()"><option value="0">0 - 无缺失</option><option value="1">1 - 部分偏盲</option><option value="2">2 - 完全偏盲</option><option value="3">3 - 双侧偏盲</option></select></div>
      </div>

      <div class="card">
        <div class="card-title">4-6. 运动功能 (左右对比)</div>
        <div class="item"><label>4. 面瘫 <span id="v4" class="score-tag score-0">0</span></label><select id="s4" onchange="calc()"><option value="0">0 - 正常</option><option value="1">1 - 轻微 (鼻唇沟变浅)</option><option value="2">2 - 部分 (下半部面瘫)</option><option value="3">3 - 完全 (上下部均瘫痪)</option></select></div>
        <div class="grid-2">
          <div class="item"><label>5a. 左上肢肌力 <span id="v5a" class="score-tag score-0">0</span></label><select id="s5a" onchange="calc()"><option value="0">0 - 无漂移</option><option value="1">1 - 漂移</option><option value="2">2 - 抗重力下落</option><option value="3">3 - 不能抗重力</option><option value="4">4 - 无动作</option></select></div>
          <div class="item"><label>5b. 右上肢肌力 <span id="v5b" class="score-tag score-0">0</span></label><select id="s5b" onchange="calc()"><option value="0">0 - 无漂移</option><option value="1">1 - 漂移</option><option value="2">2 - 抗重力下落</option><option value="3">3 - 不能抗重力</option><option value="4">4 - 无动作</option></select></div>
          <div class="item"><label>6a. 左下肢肌力 <span id="v6a" class="score-tag score-0">0</span></label><select id="s6a" onchange="calc()"><option value="0">0 - 无漂移</option><option value="1">1 - 漂移</option><option value="2">2 - 抗重力下落</option><option value="3">3 - 不能抗重力</option><option value="4">4 - 无动作</option></select></div>
          <div class="item"><label>6b. 右下肢肌力 <span id="v6b" class="score-tag score-0">0</span></label><select id="s6b" onchange="calc()"><option value="0">0 - 无漂移</option><option value="1">1 - 漂移</option><option value="2">2 - 抗重力下落</option><option value="3">3 - 不能抗重力</option><option value="4">4 - 无动作</option></select></div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">7. 共济失调</div>
        <div class="item">
          <label>7. 肢体共济失调 <span id="v7" class="score-tag score-0">0</span></label>
          <div id="ataxia-warning" class="hint-text">⚠️ 注意：肢体肌力严重受损 (≥3分)，此项记为 0 分（不可评）。</div>
          <select id="s7" onchange="calc()">
            <option value="0">0 - 无</option>
            <option value="1">1 - 一个肢体有</option>
            <option value="2">2 - 两个或以上肢体有</option>
          </select>
        </div>
      </div>

      <div class="card">
        <div class="card-title">8-11. 感觉与语言</div>
        <div class="grid-2">
            <div class="item"><label>8. 感觉 <span id="v8" class="score-tag score-0">0</span></label><select id="s8" onchange="calc()"><option value="0">0 - 正常</option><option value="1">1 - 轻中度缺失</option><option value="2">2 - 重度缺失</option></select></div>
            <div class="item"><label>9. 语言 <span id="v9" class="score-tag score-0">0</span></label><select id="s9" onchange="calc()"><option value="0">0 - 无失语</option><option value="1">1 - 轻中度失语</option><option value="2">2 - 重度失语</option><option value="3">3 - 全失语/昏迷</option></select></div>
            <div class="item"><label>10. 构音障碍 <span id="v10" class="score-tag score-0">0</span></label><select id="s10" onchange="calc()"><option value="0">0 - 正常</option><option value="1">1 - 轻中度</option><option value="2">2 - 重度/哑</option></select></div>
            <div class="item"><label>11. 忽视 <span id="v11" class="score-tag score-0">0</span></label><select id="s11" onchange="calc()"><option value="0">0 - 无忽视</option><option value="1">1 - 部分忽视</option><option value="2">2 - 严重忽视</option></select></div>
        </div>
      </div>

      <div class="result-panel">
        <div class="res-grid">
          <div><div class="res-val" id="total-score">0</div><div class="res-label">NIHSS 总分</div></div>
          <div><div class="res-val" style="font-size:24px; padding-top:10px" id="severity-label">正常</div><div class="res-label">严重程度划分</div></div>
        </div>
        <div class="btn-row">
            <button class="btn btn-primary" onclick="window.print()">打印报告</button>
            <button class="btn btn-outline" onclick="location.reload()">重新评估</button>
        </div>
      </div>
    </div>

    <script>
    function calc() {
        let total = 0;
        const ids = ['1a','1b','1c','2','3','4','5a','5b','6a','6b','7','8','9','10','11'];
        
        // 判断肌力是否严重受损 (≥3分)
        const isAtaxiaInvalid = [
            parseInt(document.getElementById('s5a').value),
            parseInt(document.getElementById('s5b').value),
            parseInt(document.getElementById('s6a').value),
            parseInt(document.getElementById('s6b').value)
        ].some(v => v >= 3);
        
        const ataxiaSelect = document.getElementById('s7');
        const ataxiaWarning = document.getElementById('ataxia-warning');

        ids.forEach(id => {
            let val = parseInt(document.getElementById('s' + id).value) || 0;
            
            if (id === '7') {
                if (isAtaxiaInvalid) {
                    val = 0;
                    ataxiaWarning.style.display = 'block';
                    ataxiaSelect.style.opacity = '0.5';
                } else {
                    ataxiaWarning.style.display = 'none';
                    ataxiaSelect.style.opacity = '1';
                }
            }

            total += val;
            const tag = document.getElementById('v' + id);
            if(tag) {
                tag.innerText = val;
                tag.className = 'score-tag ' + (val === 0 ? 'score-0' : (val < 2 ? 'score-1' : 'score-high'));
            }
        });
        document.getElementById('total-score').innerText = total;
        let sev = "正常";
        if (total >= 21) sev = "重度卒中";
        else if (total >= 16) sev = "中重度卒中";
        else if (total >= 5) sev = "中度卒中";
        else if (total >= 1) sev = "轻度卒中";
        document.getElementById('severity-label').innerText = sev;
    }
    window.onload = calc;
    </script>
    </body>
    </html>
    """
    components.html(html_content, height=1800, scrolling=True)