# app/voice_agent/api.py

import time
import uuid
from flask import Flask, request, jsonify
from app.voice_agent.crewai_logic import run_crewai_response

app = Flask(__name__)

@app.route('/llm/chat/completions', methods=['POST'])
def vapi_compatible_endpoint():
    return jsonify({
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "gpt-3.5-turbo",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Hello, this is a test. If you hear this, TTS is working!"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
    })


if __name__ == '__main__':
    app.run(debug=True)
