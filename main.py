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
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #121212;
            margin: 0;
            color: #ffffff;
        }
        .calculator-wrapper {
            display: flex;
            gap: 20px;
            align-items: stretch;
            height: 520px;
        }
        .calculator {
            background-color: #1e1e1e;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            width: 340px;
            overflow: hidden;
            border: 1px solid #333;
            display: flex;
            flex-direction: column;
        }
        .display-container {
            background-color: #1e1e1e;
            text-align: right;
            padding: 20px;
            border-bottom: 1px solid #333;
            min-height: 90px;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            word-wrap: break-word;
        }
        .previous-operand {
            color: #aaaaaa;
            font-size: 1.2em;
            min-height: 1.5em;
        }
        .display {
            color: #ffffff;
            font-size: 3em;
        }
        .buttons {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1px;
            background-color: #333;
            flex-grow: 1;
        }
        button {
            border: none;
            padding: 20px;
            font-size: 1.5em;
            cursor: pointer;
            background-color: #2b2b2b;
            color: #ffffff;
            transition: background-color 0.2s, filter 0.2s, transform 0.1s ease;
            position: relative;
            overflow: hidden;
        }
        button:hover {
            filter: brightness(1.3);
        }
        button:active {
            filter: brightness(0.85);
            transform: scale(0.93);
        }
        /* Ripple effect */
        button .ripple {
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.4);
            transform: scale(0);
            animation: ripple-animation 0.5s ease-out;
            pointer-events: none;
        }
        button.operator .ripple {
            background: rgba(255, 255, 255, 0.3);
        }
        button.action .ripple {
            background: rgba(255, 255, 255, 0.25);
        }
        @keyframes ripple-animation {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        .operator {
            background-color: #f39c12;
            color: #ffffff;
            font-weight: bold;
        }
        .action {
            background-color: #555555;
        }
        .double {
            grid-column: span 2;
        }
        .history {
            background-color: #1e1e1e;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            width: 250px;
            border: 1px solid #333;
            display: flex;
            flex-direction: column;
            color: #ffffff;
        }
        .history-title {
            padding: 20px;
            font-size: 1.2em;
            font-weight: bold;
            border-bottom: 1px solid #333;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .clear-history {
            font-size: 0.8em;
            color: #aaaaaa;
            cursor: pointer;
            font-weight: normal;
        }
        .clear-history:hover {
            color: #ffffff;
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
            color: #aaaaaa;
            font-size: 0.9em;
        }
        .history-item .result {
            font-size: 1.2em;
            font-weight: bold;
        }
        .history-item.empty {
            text-align: center;
            color: #555;
            font-style: italic;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="calculator-wrapper">
        <div class="calculator">
            <div class="display-container">
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

        // Ripple effect on button click
        document.querySelectorAll('button').forEach(btn => {
            btn.addEventListener('click', function(e) {
                const ripple = document.createElement('span');
                ripple.classList.add('ripple');
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
                ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
                this.appendChild(ripple);
                ripple.addEventListener('animationend', () => ripple.remove());
            });
        });

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