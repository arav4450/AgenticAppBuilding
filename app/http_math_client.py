"""
http_math_client.py
A simple client to test and interact with `http_math_server.py`.

Sends standard MCP-formatted JSON POST requests to:
    http://localhost:8001/mcp
"""

import json
import requests

SERVER_URL = "http://localhost:8001/mcp"


def call_math_mcp(expression: str, request_id: str = "req-1") -> dict:
    """Send an arithmetic calculation request to the Math MCP HTTP server."""
    # 1. Build standard MCP Request envelope
    request_envelope = {
        "context": {
            "request_id": request_id,
        },
        "payload": {
            "inputs": [
                {
                    "role": "user",
                    "content": expression,
                }
            ]
        },
    }

    print(f"\n[CLIENT] Sending Request for: '{expression}' (ID: {request_id})")
    print("-" * 50)
    print("Request JSON Payload:")
    print(json.dumps(request_envelope, indent=2))

    try:
        # 2. Make HTTP POST request to server
        response = requests.post(
            SERVER_URL,
            json=request_envelope,
            headers={"Content-Type": "application/json"},
            timeout=5.0,
        )

        response_data = response.json()
        print("\nResponse Received:")
        print(json.dumps(response_data, indent=2))

        # 3. Extract result
        status = response_data.get("context", {}).get("status")
        if status == "ok":
            result_text = response_data["payload"]["choices"][0]["text"]
            print(f"--> [SUCCESS] Result = {result_text}")
        else:
            error_text = response_data.get("context", {}).get("error", "Unknown error")
            print(f"--> [ERROR] Server reported error: {error_text}")

        return response_data

    except requests.exceptions.ConnectionError:
        print("\n[CLIENT ERROR] Could not connect to http_math_server!")
        print("Make sure you start the server first in another terminal:")
        print("    python my_pgms/http_math_server.py")
        return {}


def main():
    print("=" * 60)
    print("      Testing Math MCP HTTP Server")
    print("=" * 60)

    # Test Case 1: Standard arithmetic with parentheses and multiplication
    call_math_mcp("(15 + 35) * 4", request_id="math-001")

    # Test Case 2: Exponentiation using caret (^)
    call_math_mcp("2^8 - 56", request_id="math-002")

    # Test Case 3: Natural language wrapping around a math expression
    call_math_mcp("What is (200 / 4) + 25?", request_id="math-003")

    # Test Case 4: Testing error handling (division by zero)
    call_math_mcp("100 / 0", request_id="math-004")


if __name__ == "__main__":
    main()
