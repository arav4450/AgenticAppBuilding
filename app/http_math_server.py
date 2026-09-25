"""
http_math_server.py
A simple, easy-to-understand replica of MCP_math_server.py using an HTTP endpoint.

Uses Python's built-in `http.server` (zero extra dependencies required).
Runs an HTTP server listening for POST requests at:
    http://localhost:8001/mcp
"""

import ast
import json
import operator
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict

# ─── 1. Safe AST-based Math Evaluation ──────────────────────────────────────────
# Restrict operations to only safe arithmetic (+, -, *, /, **, negation).
# This prevents malicious code execution (e.g. eval("import os; ...")).

ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def eval_expr(node: ast.AST) -> float:
    """Recursively evaluate an AST node containing math."""

    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)

    if isinstance(node, ast.Num):
        return float(node.n)
    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPERATORS:
        left = eval_expr(node.left)
        right = eval_expr(node.right)
        return ALLOWED_OPERATORS[type(node.op)](left, right)

    if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_OPERATORS:
        operand = eval_expr(node.operand)
        return ALLOWED_OPERATORS[type(node.op)](operand)

    raise ValueError(f"Unsupported syntax or expression: {ast.dump(node)}")


def compute_math(expression: str) -> float:
    """Sanitize and safely compute a math expression."""

    cleaned = "".join(ch for ch in expression if ch.isdigit() or ch in "+-*/()^ .*")
    cleaned = cleaned.replace("^", "**")

    if not cleaned.strip():
        raise ValueError(f"No valid math expression found in '{expression}'.")

    expr_ast = ast.parse(cleaned, mode="eval").body
    return eval_expr(expr_ast)


# ─── 2. HTTP Request Handler ──────────────────────────────────────────────────
class MathMCPHandler(BaseHTTPRequestHandler):
    """Handles incoming HTTP POST requests containing MCP JSON envelopes."""

    def do_POST(self):
        # Only accept requests at /mcp
        if self.path != "/mcp":
            self.send_error(404, "Endpoint not found. Send requests to /mcp")
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length)

        context: Dict[str, Any] = {}
        try:
            request_data = json.loads(body_bytes.decode("utf-8"))
            context = request_data.get("context", {})
            payload = request_data.get("payload", {})

            inputs = payload.get("inputs", [])
            user_expression = None
            for msg in inputs:
                if msg.get("role") == "user":
                    user_expression = msg.get("content")
                    break

            if not user_expression:
                raise ValueError("Missing 'user' role message in payload.inputs.")

            print(f"[SERVER] Received expression to calculate: {user_expression}")

            result_value = compute_math(user_expression)
            print(f"[SERVER] Computed result: {result_value}")

            response = {
                "context": {
                    **context,
                    "request_id": context.get("request_id", "math-req-1"),
                    "status": "ok",
                },
                "payload": {"choices": [{"text": str(result_value)}]},
            }
            status_code = 200

        except Exception as err:
            print(f"[SERVER] Error processing request: {err}")

            response = {
                "context": {
                    **context,
                    "request_id": context.get("request_id", "math-req-err"),
                    "status": "error",
                    "error": str(err),
                },
                "payload": {"choices": [{"text": f"Error: {err}"}]},
            }
            status_code = 400

        # Send HTTP headers and JSON response
        response_json = json.dumps(response, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_json)))
        self.end_headers()
        self.wfile.write(response_json)

    def log_message(self, format, *args):

        print(f"[HTTP {self.command}] {self.path} -> Status {args[1]}")


# ─── 3. Server Runner ─────────────────────────────────────────────────────────
def run_server(host: str = "localhost", port: int = 8001):
    server = HTTPServer((host, port), MathMCPHandler)
    print("=" * 60)
    print(f"  Math MCP HTTP Server running at http://{host}:{port}/mcp")
    print("  Ready to receive POST requests!")
    print("  Press Ctrl+C to stop.")
    print("=" * 60)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[SERVER] Server shutting down.")
        server.server_close()


if __name__ == "__main__":
    run_server()
