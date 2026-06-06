#!/usr/bin/env python3
"""
Mock Sauce AI Insights Gateway Server.

Mimics the WebSocket behaviour captured in:
  NetworkCalls/TestInsightsApi.har

Run:
  python3 scripts/mock_ai_insights_server.py
Or with uvicorn directly:
  uvicorn scripts.mock_ai_insights_server:app --host 0.0.0.0 --port 8765
"""
import json
import asyncio
from datetime import datetime, timezone
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Mock Sauce AI Insights Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def _send_message(ws: WebSocket, msg: dict, delay: float = 0.5):
    """Send a JSON message with an optional artificial delay."""
    if delay:
        await asyncio.sleep(delay)
    await ws.send_text(json.dumps(msg))


@app.websocket("/ai-assistant-gateway/v1/chat/ws/{correlation_id}")
async def ai_chat_ws(ws: WebSocket, correlation_id: str):
    await ws.accept()
    print(f"[MOCK] WS connection accepted  correlation_id={correlation_id}")

    try:
        while True:
            raw = await ws.receive_text()
            data = json.loads(raw)
            print(f"[MOCK] RECEIVED: {json.dumps(data, indent=2)}")

            msg_type = data.get("type")
            msg_name = data.get("name")
            causation_id = data.get("message_id")
            payload = data.get("payload", {})
            prompt_text = payload.get("prompt", "")

            if msg_type == "prompt" and msg_name == "send_prompt":
                # Stream the canned response exactly as seen in the HAR
                await _send_message(ws, {
                    "message_id": "mock-msg-1",
                    "name": "answer_received",
                    "correlation_id": correlation_id,
                    "causation_id": causation_id,
                    "payload": {
                        "response_state": "PROCESSING",
                        "data": [
                            {
                                "widget_type": "text",
                                "value": "Here's the error rate trend over the past seven days:"
                            }
                        ]
                    }
                }, delay=0.3)

                await _send_message(ws, {
                    "message_id": "mock-msg-2",
                    "name": "answer_received",
                    "correlation_id": correlation_id,
                    "causation_id": causation_id,
                    "payload": {
                        "response_state": "PROCESSING",
                        "data": [
                            {
                                "widget_type": "chart",
                                "value": {
                                    "chart_type": "line",
                                    "dataKeys": ["errors"],
                                    "data": [
                                        {"name": "2026-05-15T00:00:00.000Z", "errors": 2.0},
                                        {"name": "2026-05-16T00:00:00.000Z", "errors": 2.0},
                                        {"name": "2026-05-17T00:00:00.000Z", "errors": 3.0},
                                        {"name": "2026-05-18T00:00:00.000Z", "errors": 1.0},
                                        {"name": "2026-05-19T00:00:00.000Z", "errors": 1.0},
                                        {"name": "2026-05-20T00:00:00.000Z", "errors": 4.0}
                                    ],
                                    "units": {
                                        "x_label": "Date",
                                        "y_label": "number"
                                    }
                                }
                            }
                        ]
                    }
                }, delay=0.3)

                await _send_message(ws, {
                    "message_id": "mock-msg-3",
                    "name": "answer_received",
                    "correlation_id": correlation_id,
                    "causation_id": causation_id,
                    "payload": {
                        "response_state": "PROCESSING",
                        "data": [
                            {
                                "widget_type": "text",
                                "value": (
                                    "The chart above shows the daily count of errors. "
                                    "There was a peak of 4 errors on May 20th, 2026.\n\n"
                                    "Here are the top five errors by count in the last seven days:\n\n"
                                    "| ERROR_TYPE                  | ERROR_COUNT |\n"
                                    "| :-------------------------- | :---------- |\n"
                                    "| Error starting appium session | 11          |"
                                )
                            }
                        ]
                    }
                }, delay=0.3)

                await _send_message(ws, {
                    "message_id": "mock-msg-4",
                    "name": "answer_received",
                    "correlation_id": correlation_id,
                    "causation_id": causation_id,
                    "payload": {
                        "response_state": "DONE",
                        "data": None
                    }
                }, delay=0.2)

                print("[MOCK] Full response stream delivered.")

            elif msg_type == "ping":
                await _send_message(ws, {"type": "pong"}, delay=0)

            else:
                print(f"[MOCK] Unhandled message type={msg_type} name={msg_name}")

    except WebSocketDisconnect:
        print(f"[MOCK] Client disconnected  correlation_id={correlation_id}")
    except Exception as exc:
        print(f"[MOCK] Error: {exc}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
