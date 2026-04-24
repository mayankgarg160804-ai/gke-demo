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
    <style>
        :root {
            --bg-body: #121212;
            --bg-panel: #1e1e1e;
            --bg-btn: #2b2b2b;
            --bg-action: #555555;
            --bg-operator: #f39c12;
            --border: #333;
            --text: #ffffff;
            --text-dim: #aaaaaa;
            --text-muted: #555;
            --shadow: rgba(0,0,0,0.5);
        }
        body.light {
            --bg-body: #e8e8e8;
            --bg-panel: #ffffff;
            --bg-btn: #f0f0f0;
            --bg-action: #d5d5d5;
            --bg-operator: #f39c12;
            --border: #cccccc;
            --text: #1a1a1a;
            --text-dim: #666666;
            --text-muted: #aaaaaa;
            --shadow: rgba(0,0,0,0.12);
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: var(--bg-body);
            margin: 0;
            color: var(--text);
            transition: background-color 0.3s, color 0.3s;
        }
        .calculator-wrapper {
            display: flex;
            gap: 20px;
            align-items: stretch;
            height: 520px;
        }
        .calculator {
            background-color: var(--bg-panel);
            border-radius: 12px;
            box-shadow: 0 10px 30px var(--shadow);
            width: 340px;
            overflow: hidden;
            border: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            transition: background-color 0.3s, box-shadow 0.3s, border-color 0.3s;
        }
        .display-container {
            background-color: var(--bg-panel);
            text-align: right;
            padding: 20px;
            border-bottom: 1px solid var(--border);
            min-height: 90px;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            word-wrap: break-word;
            position: relative;
            transition: background-color 0.3s, border-color 0.3s;
        }
        .theme-btn {
            position: absolute;
            top: 12px;
            left: 12px;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            border: 1px solid var(--border);
            background: var(--bg-btn);
            color: var(--text);
            font-size: 1.1em;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background-color 0.3s, border-color 0.3s, transform 0.3s;
            padding: 0;
            line-height: 1;
        }
        .theme-btn:hover {
            transform: rotate(30deg) scale(1.15);
        }
        .previous-operand {
            color: var(--text-dim);
            font-size: 1.2em;
            min-height: 1.5em;
            transition: color 0.3s;
        }
        .display {
            color: var(--text);
            font-size: 3em;
            transition: color 0.3s;
        }
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
            font-size: 1.5em;
            cursor: pointer;
            background-color: var(--bg-btn);
            color: var(--text);
            transition: background-color 0.3s, color 0.3s, filter 0.2s;
        }
        button:hover {
            filter: brightness(1.2);
        }
        button:active {
            filter: brightness(0.8);
            transform: scale(0.92);
        }
        .operator {
            background-color: var(--bg-operator);
            color: #ffffff;
            font-weight: bold;
        }
        .action {
            background-color: var(--bg-action);
            transition: background-color 0.3s;
        }
        .double {
            grid-column: span 2;
        }
        .history {
            background-color: var(--bg-panel);
            border-radius: 12px;
            box-shadow: 0 10px 30px var(--shadow);
            width: 250px;
            border: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            color: var(--text);
            transition: background-color 0.3s, box-shadow 0.3s, border-color 0.3s, color 0.3s;
        }
        .history-title {
            padding: 20px;
            font-size: 1.2em;
            font-weight: bold;
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
            font-weight: normal;
            transition: color 0.3s;
        }
        .clear-history:hover {
            color: var(--text);
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
            font-size: 0.9em;
            transition: color 0.3s;
        }
        .history-item .result {
            font-size: 1.2em;
            font-weight: bold;
        }
        .history-item.empty {
            text-align: center;
            color: var(--text-muted);
            font-style: italic;
            margin-top: 20px;
            transition: color 0.3s;
        }
    </style>
</head>
<body>
    <div class="calculator-wrapper">
        <div class="calculator">
            <div class="display-container">
                <button class="theme-btn" id="theme-btn" onclick="toggleTheme()" title="Toggle theme">&#9790;</button>
                <div class="previous-operand" id="previous-operand"></div>
                <div class="display" id="display">0</div>
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
                <button onclick="appendNumber('0')" class="double">0</button>
                <button onclick="appendNumber('.')">.</button>
                <button onclick="calculate()" class="operator">=</button>
            </div>
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

        function updateDisplay() {
            display.innerText = currentInput;
            if (operator !== null && previousInput !== null) {
                let opSymbol = operator;
                if (operator === '/') opSymbol = '÷';
                else if (operator === '*') opSymbol = '×';
                else if (operator === '-') opSymbol = '−';
                previousOperandElement.innerText = previousInput + ' ' + opSymbol;
            } else {
                previousOperandElement.innerText = '';
            }
        }

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
                case '%': result = a % b; break;
            }
            
            let opSymbol = operator;
            if (operator === '/') opSymbol = '÷';
            else if (operator === '*') opSymbol = '×';
            else if (operator === '-') opSymbol = '−';
            
            let equation = previousInput + ' ' + opSymbol + ' ' + currentInput;

            if (result !== 'Error') {
                result = Math.round(result * 10000000000) / 10000000000;
            }
            
            addHistory(equation, String(result));

            currentInput = String(result);
            operator = null;
            previousInput = null;
            shouldResetDisplay = true;
            updateDisplay();
        }

        function addHistory(equation, result) {
            if (emptyHistory) {
                emptyHistory.remove();
                emptyHistory = null;
            }
            let div = document.createElement('div');
            div.className = 'history-item';
            div.innerHTML = `<div class="equation">${equation} =</div><div class="result">${result}</div>`;
            historyList.prepend(div);
        }

        function clearHistory() {
            historyList.innerHTML = '<div class="history-item empty" id="empty-history">No history yet</div>';
            emptyHistory = document.getElementById('empty-history');
        }

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

        // Add keyboard support
        document.addEventListener('keydown', (e) => {
            if (e.key >= '0' && e.key <= '9') appendNumber(e.key);
            if (e.key === '.') appendNumber('.');
            if (e.key === '=' || e.key === 'Enter') { e.preventDefault(); calculate(); }
            if (e.key === 'Backspace') deleteDigit();
            if (e.key === 'Escape') clearDisplay();
            if (e.key === '+' || e.key === '-' || e.key === '*' || e.key === '/' || e.key === '%') {
                appendOperator(e.key);
            }
        });

        // Theme toggle
        const themeBtn = document.getElementById('theme-btn');
        function toggleTheme() {
            document.body.classList.toggle('light');
            const isLight = document.body.classList.contains('light');
            themeBtn.innerHTML = isLight ? '&#9728;' : '&#9790;';
            localStorage.setItem('calc-theme', isLight ? 'light' : 'dark');
        }
        // Restore saved theme
        if (localStorage.getItem('calc-theme') === 'light') {
            document.body.classList.add('light');
            themeBtn.innerHTML = '&#9728;';
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