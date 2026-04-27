from http.server import BaseHTTPRequestHandler, HTTPServer
import os

PORT = int(os.environ.get("PORT", "8080"))

HTML_CONTENT = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calculator Demo</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-body: #0f0f13;
            --bg-panel: #1a1a24;
            --bg-btn: #252535;
            --bg-action: #3a3a50;
            --bg-operator: #e67e22;
            --bg-operator-hover: #f39c12;
            --bg-sci: #2a2a40;
            --bg-sci-hover: #3a3a55;
            --border: #2a2a3a;
            --text: #f0f0f5;
            --text-dim: #8888aa;
            --text-muted: #555570;
            --shadow: rgba(0,0,0,0.6);
            --accent: #e67e22;
            --accent-glow: rgba(230, 126, 34, 0.25);
            --toggle-bg: #2a2a40;
            --toggle-active: #e67e22;
        }
        body.light {
            --bg-body: #f0f0f5;
            --bg-panel: #ffffff;
            --bg-btn: #f5f5fa;
            --bg-action: #e0e0ea;
            --bg-operator: #e67e22;
            --bg-operator-hover: #f39c12;
            --bg-sci: #eaeaf0;
            --bg-sci-hover: #dddde8;
            --border: #d0d0da;
            --text: #1a1a2e;
            --text-dim: #6666880;
            --text-muted: #aaaacc;
            --shadow: rgba(0,0,0,0.1);
            --accent: #e67e22;
            --accent-glow: rgba(230, 126, 34, 0.15);
            --toggle-bg: #e0e0ea;
            --toggle-active: #e67e22;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background-color: var(--bg-body);
            color: var(--text);
            transition: background-color 0.4s ease, color 0.4s ease;
        }

        /* ── Dark Mode Toggle (top-right corner) ── */
        .theme-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .theme-toggle-label {
            font-size: 0.8em;
            color: var(--text-dim);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .theme-toggle-track {
            width: 52px;
            height: 28px;
            border-radius: 14px;
            background: var(--toggle-bg);
            border: 1px solid var(--border);
            cursor: pointer;
            position: relative;
            transition: background 0.3s, border-color 0.3s;
        }
        .theme-toggle-track::after {
            content: '';
            position: absolute;
            top: 3px;
            left: 3px;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: var(--accent);
            box-shadow: 0 2px 6px var(--accent-glow);
            transition: transform 0.3s ease;
        }
        body.light .theme-toggle-track::after {
            transform: translateX(24px);
        }
        .theme-icon {
            font-size: 1.2em;
            transition: opacity 0.3s;
        }

        /* ── Main Wrapper ── */
        .calculator-wrapper {
            display: flex;
            gap: 20px;
            align-items: stretch;
            padding: 20px;
        }

        /* ── Scientific + Calculator Container ── */
        .calc-container {
            display: flex;
            flex-direction: column;
            gap: 0;
        }

        /* ── Mode Toggle ── */
        .mode-toggle-bar {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 10px 16px;
            background: var(--bg-panel);
            border: 1px solid var(--border);
            border-bottom: none;
            border-radius: 12px 12px 0 0;
            transition: background 0.3s, border-color 0.3s;
        }
        .mode-toggle-text {
            font-size: 0.75em;
            font-weight: 600;
            color: var(--text-dim);
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .mode-toggle-text.active {
            color: var(--accent);
        }
        .mode-switch {
            width: 44px;
            height: 24px;
            border-radius: 12px;
            background: var(--toggle-bg);
            border: 1px solid var(--border);
            cursor: pointer;
            position: relative;
            transition: background 0.3s, border-color 0.3s;
        }
        .mode-switch::after {
            content: '';
            position: absolute;
            top: 2px;
            left: 2px;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: var(--text-dim);
            transition: transform 0.3s ease, background 0.3s;
        }
        .mode-switch.scientific::after {
            transform: translateX(20px);
            background: var(--accent);
        }

        /* ── Calculator ── */
        .calculator {
            background-color: var(--bg-panel);
            border-radius: 0 0 12px 12px;
            box-shadow: 0 12px 40px var(--shadow);
            width: 360px;
            overflow: hidden;
            border: 1px solid var(--border);
            border-top: none;
            display: flex;
            flex-direction: column;
            transition: background-color 0.3s, box-shadow 0.3s, border-color 0.3s;
        }
        .calculator.with-sci {
            border-radius: 0;
        }

        /* ── Display ── */
        .display-container {
            background: linear-gradient(135deg, var(--bg-panel) 0%, var(--bg-btn) 100%);
            text-align: right;
            padding: 24px 20px 20px 20px;
            border-bottom: 1px solid var(--border);
            min-height: 100px;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            word-wrap: break-word;
            position: relative;
            transition: background 0.3s, border-color 0.3s;
        }
        .previous-operand {
            color: var(--text-dim);
            font-size: 1.1em;
            font-weight: 300;
            min-height: 1.5em;
            transition: color 0.3s;
        }
        .display {
            color: var(--text);
            font-size: 2.8em;
            font-weight: 300;
            letter-spacing: -0.02em;
            transition: color 0.3s;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        /* ── Standard Buttons ── */
        .buttons {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1px;
            background-color: var(--border);
            flex-grow: 1;
            transition: background-color 0.3s;
        }
        button {
            border: none;
            padding: 20px;
            font-size: 1.35em;
            font-family: 'Inter', sans-serif;
            font-weight: 400;
            cursor: pointer;
            background-color: var(--bg-btn);
            color: var(--text);
            transition: background-color 0.2s, color 0.2s, transform 0.15s, filter 0.2s;
            position: relative;
            overflow: hidden;
        }
        button:hover {
            filter: brightness(1.25);
        }
        button:active {
            transform: scale(0.93);
            filter: brightness(0.85);
        }
        .operator {
            background-color: var(--bg-operator);
            color: #ffffff;
            font-weight: 600;
        }
        .operator:hover {
            background-color: var(--bg-operator-hover);
        }
        .action {
            background-color: var(--bg-action);
            font-weight: 500;
            transition: background-color 0.3s;
        }
        .double {
            grid-column: span 2;
        }

        /* ── Scientific Panel ── */
        .scientific-panel {
            background-color: var(--bg-panel);
            border: 1px solid var(--border);
            border-top: none;
            overflow: hidden;
            max-height: 0;
            opacity: 0;
            transition: max-height 0.4s ease, opacity 0.3s ease, border-color 0.3s;
        }
        .scientific-panel.open {
            max-height: 400px;
            opacity: 1;
        }
        .sci-buttons {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 1px;
            background-color: var(--border);
        }
        .sci-btn {
            background-color: var(--bg-sci);
            color: var(--text-dim);
            font-size: 0.95em;
            padding: 14px 8px;
            font-weight: 500;
            border: none;
            cursor: pointer;
            font-family: 'Inter', sans-serif;
            transition: background-color 0.2s, color 0.2s, transform 0.15s;
        }
        .sci-btn:hover {
            background-color: var(--bg-sci-hover);
            color: var(--text);
        }
        .sci-btn:active {
            transform: scale(0.93);
        }
        .sci-btn.const-btn {
            color: var(--accent);
            font-weight: 600;
        }

        /* ── History Panel ── */
        .history {
            background-color: var(--bg-panel);
            border-radius: 12px;
            box-shadow: 0 12px 40px var(--shadow);
            width: 250px;
            border: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            color: var(--text);
            transition: background-color 0.3s, box-shadow 0.3s, border-color 0.3s, color 0.3s;
        }
        .history-title {
            padding: 20px;
            font-size: 1.1em;
            font-weight: 600;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: border-color 0.3s;
        }
        .clear-history {
            font-size: 0.8em;
            color: var(--text-dim);
            cursor: pointer;
            font-weight: 400;
            transition: color 0.3s;
        }
        .clear-history:hover {
            color: var(--accent);
        }
        .history-list {
            padding: 10px;
            overflow-y: auto;
            flex-grow: 1;
        }
        .history-item {
            margin-bottom: 15px;
            text-align: right;
            padding-right: 10px;
        }
        .history-item .equation {
            color: var(--text-dim);
            font-size: 0.85em;
            font-weight: 300;
            transition: color 0.3s;
        }
        .history-item .result {
            font-size: 1.15em;
            font-weight: 600;
        }
        .history-item.empty {
            text-align: center;
            color: var(--text-muted);
            font-style: italic;
            font-weight: 300;
            margin-top: 20px;
            transition: color 0.3s;
        }

        /* ── Responsive ── */
        @media (max-width: 700px) {
            .calculator-wrapper {
                flex-direction: column;
                align-items: center;
            }
            .history {
                width: 360px;
                max-height: 200px;
            }
        }
    </style>
</head>
<body>
    <!-- Dark/Light Mode Toggle (top-right) -->
    <div class="theme-toggle">
        <span class="theme-icon" id="theme-icon">&#9790;</span>
        <div class="theme-toggle-track" id="theme-track" onclick="toggleTheme()" title="Toggle dark/light mode"></div>
    </div>

    <div class="calculator-wrapper">
        <div class="calc-container">
            <!-- Mode Toggle Bar -->
            <div class="mode-toggle-bar">
                <span class="mode-toggle-text active" id="mode-label-std">Standard</span>
                <div class="mode-switch" id="mode-switch" onclick="toggleMode()" title="Toggle scientific mode"></div>
                <span class="mode-toggle-text" id="mode-label-sci">Scientific</span>
            </div>

            <div class="calculator" id="calculator">
                <div class="display-container">
                    <div class="previous-operand" id="previous-operand"></div>
                    <div class="display" id="display">0</div>
                </div>

                <!-- Scientific Panel (hidden by default) -->
                <div class="scientific-panel" id="scientific-panel">
                    <div class="sci-buttons">
                        <button class="sci-btn" onclick="sciFunction('sin')">sin</button>
                        <button class="sci-btn" onclick="sciFunction('cos')">cos</button>
                        <button class="sci-btn" onclick="sciFunction('tan')">tan</button>
                        <button class="sci-btn" onclick="sciFunction('asin')">sin⁻¹</button>
                        <button class="sci-btn" onclick="sciFunction('acos')">cos⁻¹</button>
                        <button class="sci-btn" onclick="sciFunction('atan')">tan⁻¹</button>
                        <button class="sci-btn" onclick="sciFunction('log')">log</button>
                        <button class="sci-btn" onclick="sciFunction('ln')">ln</button>
                        <button class="sci-btn" onclick="sciFunction('sqrt')">√x</button>
                        <button class="sci-btn" onclick="sciFunction('cbrt')">³√x</button>
                        <button class="sci-btn" onclick="sciFunction('square')">x²</button>
                        <button class="sci-btn" onclick="sciFunction('cube')">x³</button>
                        <button class="sci-btn" onclick="sciFunction('inv')">1/x</button>
                        <button class="sci-btn" onclick="sciFunction('fact')">x!</button>
                        <button class="sci-btn" onclick="sciFunction('abs')">|x|</button>
                        <button class="sci-btn" onclick="sciFunction('exp')">eˣ</button>
                        <button class="sci-btn" onclick="sciFunction('pow10')">10ˣ</button>
                        <button class="sci-btn const-btn" onclick="insertConstant('pi')">π</button>
                        <button class="sci-btn const-btn" onclick="insertConstant('e')">e</button>
                        <button class="sci-btn" onclick="appendOperator('^')">xʸ</button>
                    </div>
                </div>

                <div class="buttons">
                    <button onclick="clearDisplay()" class="action">C</button>
                    <button onclick="deleteDigit()" class="action">DEL</button>
                    <button onclick="appendOperator('%')" class="action">%</button>
                    <button onclick="appendOperator('/')" class="operator">&divide;</button>
                    <button onclick="appendNumber('7')">7</button>
                    <button onclick="appendNumber('8')">8</button>
                    <button onclick="appendNumber('9')">9</button>
                    <button onclick="appendOperator('*')" class="operator">&times;</button>
                    <button onclick="appendNumber('4')">4</button>
                    <button onclick="appendNumber('5')">5</button>
                    <button onclick="appendNumber('6')">6</button>
                    <button onclick="appendOperator('-')" class="operator">&minus;</button>
                    <button onclick="appendNumber('1')">1</button>
                    <button onclick="appendNumber('2')">2</button>
                    <button onclick="appendNumber('3')">3</button>
                    <button onclick="appendOperator('+')" class="operator">+</button>
                    <button onclick="toggleSign()" class="action">±</button>
                    <button onclick="appendNumber('0')">0</button>
                    <button onclick="appendNumber('.')">.</button>
                    <button onclick="calculate()" class="operator">=</button>
                </div>
            </div>

            <!-- Scientific bottom border fix -->
            <div class="scientific-bottom" id="scientific-bottom" style="display:none;
                background: var(--bg-panel); border: 1px solid var(--border); border-top: none;
                border-radius: 0 0 12px 12px; height: 0;"></div>
        </div>

        <div class="history">
            <div class="history-title">
                History
                <span class="clear-history" onclick="clearHistory()">Clear</span>
            </div>
            <div class="history-list" id="history-list">
                <div class="history-item empty" id="empty-history">No history yet</div>
            </div>
        </div>
    </div>

    <script>
        let display = document.getElementById('display');
        let previousOperandElement = document.getElementById('previous-operand');
        let historyList = document.getElementById('history-list');
        let emptyHistory = document.getElementById('empty-history');

        let currentInput = '0';
        let previousInput = null;
        let operator = null;
        let shouldResetDisplay = false;

        // ── Display Update ──
        function getOpSymbol(op) {
            const symbols = { '/': '÷', '*': '×', '-': '−', '^': '^' };
            return symbols[op] || op;
        }

        function updateDisplay() {
            display.innerText = currentInput;
            if (operator !== null && previousInput !== null) {
                previousOperandElement.innerText = previousInput + ' ' + getOpSymbol(operator);
            } else {
                previousOperandElement.innerText = '';
            }
        }

        // ── Number Input ──
        function appendNumber(num) {
            if (currentInput === '0' || shouldResetDisplay) {
                currentInput = String(num);
                shouldResetDisplay = false;
            } else {
                if (num === '.' && currentInput.includes('.')) return;
                currentInput += String(num);
            }
            updateDisplay();
        }

        // ── Operator Input ──
        function appendOperator(op) {
            if (operator !== null && !shouldResetDisplay) {
                calculate();
            }
            operator = op;
            previousInput = currentInput;
            currentInput = '0';
            shouldResetDisplay = true;
            updateDisplay();
        }

        // ── Toggle Sign (±) ──
        function toggleSign() {
            if (currentInput === '0') return;
            if (currentInput.startsWith('-')) {
                currentInput = currentInput.substring(1);
            } else {
                currentInput = '-' + currentInput;
            }
            updateDisplay();
        }

        // ── Calculate ──
        function calculate() {
            if (operator === null || shouldResetDisplay) return;
            let a = parseFloat(previousInput);
            let b = parseFloat(currentInput);
            let result = 0;
            switch(operator) {
                case '+': result = a + b; break;
                case '-': result = a - b; break;
                case '*': result = a * b; break;
                case '/': result = b !== 0 ? a / b : 'Error'; break;
                case '%': result = (a / 100) * b; break;
                case '^': result = Math.pow(a, b); break;
            }

            let equation = previousInput + ' ' + getOpSymbol(operator) + ' ' + currentInput;

            if (result !== 'Error' && isFinite(result)) {
                result = Math.round(result * 1e10) / 1e10;
            } else if (!isFinite(result)) {
                result = 'Error';
            }

            addHistory(equation, String(result));

            currentInput = String(result);
            operator = null;
            previousInput = null;
            shouldResetDisplay = true;
            updateDisplay();
        }

        // ── Scientific Functions ──
        function sciFunction(fn) {
            let val = parseFloat(currentInput);
            let label = '';
            let result = 0;
            switch(fn) {
                case 'sin':    label = 'sin(' + val + ')';   result = Math.sin(val * Math.PI / 180); break;
                case 'cos':    label = 'cos(' + val + ')';   result = Math.cos(val * Math.PI / 180); break;
                case 'tan':    label = 'tan(' + val + ')';   result = Math.tan(val * Math.PI / 180); break;
                case 'asin':
                    if (val < -1 || val > 1) { currentInput = 'Error'; updateDisplay(); return; }
                    label = 'sin⁻¹(' + val + ')'; result = Math.asin(val) * 180 / Math.PI; break;
                case 'acos':
                    if (val < -1 || val > 1) { currentInput = 'Error'; updateDisplay(); return; }
                    label = 'cos⁻¹(' + val + ')'; result = Math.acos(val) * 180 / Math.PI; break;
                case 'atan':   label = 'tan⁻¹(' + val + ')'; result = Math.atan(val) * 180 / Math.PI; break;
                case 'log':
                    if (val <= 0) { currentInput = 'Error'; updateDisplay(); return; }
                    label = 'log(' + val + ')';    result = Math.log10(val); break;
                case 'ln':
                    if (val <= 0) { currentInput = 'Error'; updateDisplay(); return; }
                    label = 'ln(' + val + ')';     result = Math.log(val); break;
                case 'sqrt':
                    if (val < 0) { currentInput = 'Error'; updateDisplay(); return; }
                    label = '√(' + val + ')';      result = Math.sqrt(val); break;
                case 'cbrt':   label = '³√(' + val + ')';   result = Math.cbrt(val); break;
                case 'square': label = val + '²';           result = val * val; break;
                case 'cube':   label = val + '³';           result = val * val * val; break;
                case 'inv':
                    if (val === 0) { currentInput = 'Error'; updateDisplay(); return; }
                    label = '1/(' + val + ')';     result = 1 / val; break;
                case 'fact':
                    if (val < 0 || val !== Math.floor(val) || val > 170) { currentInput = 'Error'; updateDisplay(); return; }
                    label = val + '!';             result = factorial(val); break;
                case 'abs':    label = '|' + val + '|';     result = Math.abs(val); break;
                case 'exp':    label = 'e^(' + val + ')';   result = Math.exp(val); break;
                case 'pow10':  label = '10^(' + val + ')';  result = Math.pow(10, val); break;
            }

            if (!isFinite(result)) {
                result = 'Error';
            } else {
                result = Math.round(result * 1e10) / 1e10;
            }

            addHistory(label, String(result));
            currentInput = String(result);
            shouldResetDisplay = true;
            updateDisplay();
        }

        function factorial(n) {
            if (n === 0 || n === 1) return 1;
            let res = 1;
            for (let i = 2; i <= n; i++) res *= i;
            return res;
        }

        // ── Constants ──
        function insertConstant(c) {
            if (c === 'pi') currentInput = String(Math.PI);
            if (c === 'e') currentInput = String(Math.E);
            shouldResetDisplay = true;
            updateDisplay();
        }

        // ── History ──
        function addHistory(equation, result) {
            if (emptyHistory) {
                emptyHistory.remove();
                emptyHistory = null;
            }
            let div = document.createElement('div');
            div.className = 'history-item';
            div.innerHTML = '<div class="equation">' + equation + ' =</div><div class="result">' + result + '</div>';
            historyList.prepend(div);
        }

        function clearHistory() {
            historyList.innerHTML = '<div class="history-item empty" id="empty-history">No history yet</div>';
            emptyHistory = document.getElementById('empty-history');
        }

        // ── Clear / Delete ──
        function clearDisplay() {
            currentInput = '0';
            operator = null;
            previousInput = null;
            shouldResetDisplay = false;
            updateDisplay();
        }

        function deleteDigit() {
            if (shouldResetDisplay) return;
            if (currentInput.length > 1) {
                currentInput = currentInput.slice(0, -1);
            } else {
                currentInput = '0';
            }
            updateDisplay();
        }

        // ── Keyboard Support ──
        document.addEventListener('keydown', (e) => {
            if (e.key >= '0' && e.key <= '9') appendNumber(e.key);
            if (e.key === '.') appendNumber('.');
            if (e.key === '=' || e.key === 'Enter') { e.preventDefault(); calculate(); }
            if (e.key === 'Backspace') deleteDigit();
            if (e.key === 'Escape') clearDisplay();
            if (['+', '-', '*', '/', '%', '^'].includes(e.key)) {
                appendOperator(e.key);
            }
        });

        // ── Theme Toggle ──
        const themeIcon = document.getElementById('theme-icon');
        function toggleTheme() {
            document.body.classList.toggle('light');
            const isLight = document.body.classList.contains('light');
            themeIcon.innerHTML = isLight ? '&#9728;' : '&#9790;';
            localStorage.setItem('calc-theme', isLight ? 'light' : 'dark');
        }
        // Restore saved theme
        if (localStorage.getItem('calc-theme') === 'light') {
            document.body.classList.add('light');
            themeIcon.innerHTML = '&#9728;';
        }

        // ── Scientific / Standard Mode Toggle ──
        const modeSwitch = document.getElementById('mode-switch');
        const sciPanel = document.getElementById('scientific-panel');
        const calculator = document.getElementById('calculator');
        const sciBottom = document.getElementById('scientific-bottom');
        const modeLabelStd = document.getElementById('mode-label-std');
        const modeLabelSci = document.getElementById('mode-label-sci');
        let scientificMode = false;

        function toggleMode() {
            scientificMode = !scientificMode;
            modeSwitch.classList.toggle('scientific', scientificMode);
            sciPanel.classList.toggle('open', scientificMode);
            modeLabelStd.classList.toggle('active', !scientificMode);
            modeLabelSci.classList.toggle('active', scientificMode);

            if (scientificMode) {
                calculator.style.borderRadius = '0';
                sciBottom.style.display = 'block';
            } else {
                calculator.style.borderRadius = '0 0 12px 12px';
                sciBottom.style.display = 'none';
            }

            localStorage.setItem('calc-mode', scientificMode ? 'scientific' : 'standard');
        }

        // Restore saved mode
        if (localStorage.getItem('calc-mode') === 'scientific') {
            toggleMode();
        }
    </script>
</body>
</html>
"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = HTML_CONTENT.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Listening on port {PORT}")
    server.serve_forever()