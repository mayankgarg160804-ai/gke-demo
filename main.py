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
        .calculator {
            background-color: #1e1e1e;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            width: 340px;
            overflow: hidden;
            border: 1px solid #333;
        }
        .display {
            background-color: #1e1e1e;
            color: #ffffff;
            text-align: right;
            padding: 30px 20px 20px;
            font-size: 3em;
            word-wrap: break-word;
            border-bottom: 1px solid #333;
        }
        .buttons {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1px;
            background-color: #333;
        }
        button {
            border: none;
            padding: 20px;
            font-size: 1.5em;
            cursor: pointer;
            background-color: #2b2b2b;
            color: #ffffff;
            transition: background-color 0.2s, filter 0.2s;
        }
        button:hover {
            filter: brightness(1.2);
        }
        button:active {
            filter: brightness(0.8);
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
    </style>
</head>
<body>
    <div class="calculator">
        <div class="display" id="display">0</div>
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
    <script>
        let display = document.getElementById('display');
        let currentInput = '0';
        let previousInput = null;
        let operator = null;
        let shouldResetDisplay = false;

        function updateDisplay() {
            display.innerText = currentInput;
        }

        function appendNumber(num) {
            if (currentInput === '0' || shouldResetDisplay) {
                currentInput = num;
                shouldResetDisplay = false;
            } else {
                if (num === '.' && currentInput.includes('.')) return;
                currentInput += num;
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
            if (result !== 'Error') {
                result = Math.round(result * 10000000000) / 10000000000;
            }
            currentInput = String(result);
            operator = null;
            previousInput = null;
            shouldResetDisplay = true;
            updateDisplay();
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