import asyncio
import json
import re
import time
from datetime import datetime, timedelta
import pytz
import threading
import requests
import websockets
import socketio  # python-socketio client

# Telegram & IVASMS tokens / IDs

main_otp_bots = ["7080545849:AAEUiijbe1FKI_3AdiHkLutVV63wMKZU0xI"]

CHAT_ID1 = "-1002601589640"

token = "eyJpdiI6ImFtaFc4eXlHcHR5THV4VzlRbTNhNnc9PSIsInZhbHVlIjoiT1RkdERMOEVHUTJjVmJQVUVlRmhVUXpGV0Q2WFJ3T29KVHVrOE56MUlNMVNrY3Y1Zm5yMEw3OTFQMFQ3Ni91clhGbUNvMG5va01RVGU3Sm1BS1JlcG9GcEM2WGI0eDlQclFPT2J1Mlo1NGcyeWdEUy9zcm8rTkJSK0QrSzBQQi9tOHltV2RjRng4a3RsakhHeFhRNzFMam9sTkUwSFJkUEJCNFB1bkhhMjZKVGlxM2ZlK05aSFJpNFIxS25DTFVWdHRxRngxSFQ0UEJtaUNKUEoxdjRRSXB4SitrTXJUekh4ZEtzOWRIMzhLcHUzUU1JdVhGMnEwSFRBV0YwWnpqMFNxMlV2aERacXdHTHVDNEl3NEZ3eXo4dlBRa2hlYVdCWS9kdWwzVmpjZUtCZU9hV21LVCtlazVZR2VYamFFWlhsQzFaaVZyUG1Ic3oxMlVPUU1qeStjS29ueEZ0cDFjMGhlYWg5a1N2WmNnajhhNnBRS251eGlJenVST290S2NYSFc0aEsrTU13OGgzWmo4SVBMbWh3UDFBMjI1SHhuOUNLQmtxL1FublNyNFVZOHBISEp3SFp6WnRFWitLVWtYNC9xNUc1dGpFTzUvVEZtbEp3Z3owbTlMc0hVUEFHTlUyTUFhSDRSVWhkUkNGRWdudEluTTJMa3F2RzBUYlZVR0d3WmdxbG5QUDNDd3ZxWGxDanY1NHZ3PT0iLCJtYWMiOiJlOWE0NGFjNzQ0OGJkZTRiZTAwNjNhYzc0MDJhMjc1NmJiMmU5MjdiMzMxNjY4NWIyOGYyZGIwZDAxMTBkOWFjIiwidGFnIjoiIn0="  # তোমার টোকেন এখানে দাও

ws_url = f"wss://ivasms.com:2087/socket.io/?token={requests.utils.quote(token)}&EIO=4&transport=websocket"

# bot index trackers
bot_index = {
    "otp": 0
}


def escape_html(unsafe: str) -> str:
    return (unsafe.replace("&", "&amp;")
                  .replace("<", "&lt;")
                  .replace(">", "&gt;")
                  .replace('"', "&quot;")
                  .replace("'", "&#039;"))

def send_to_telegram(bot_type, chat_id, text):
    bots = main_otp_bots
    index = bot_index[bot_type]
    total = len(bots)
    tried = 0

    while tried < total:
        token = bots[index]
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}

        try:
            resp = requests.post(url, json=payload, timeout=10)
            resp.raise_for_status()
            print(f"✔️ Message sent to Telegram 📩 — via {bot_type.upper()} Bot {index + 1}")
            bot_index[bot_type] = index
            return
        except requests.exceptions.HTTPError as e:
            if resp.status_code == 429:
                print(f"⚠️ Bot {index + 1} rate-limited. Trying next...")
                index = (index + 1) % total
                tried += 1
                time.sleep(1.5)
            else:
                print("⚠️ HTTP error:", e)
                break
        except Exception as e:
            print("⚠️ Telegram error:", e)
            break

    print(f"🚫 All {bot_type.upper()} bots failed.")

async def connect_ws():
    while True:
        try:
            async with websockets.connect(ws_url) as ws:
                print("🖥️ Panel connected successfully ✅")
                while True:
                    data = await ws.recv()
                    if data.startswith("0"):
                        await ws.send("40/livesms,")
                        continue
                    if data == "2":
                        await ws.send("3")
                        continue
                    if "/livesms" in data:
                        try:
                            payload = json.loads(data[data.index('['):])
                            msg = payload[1]
                            bd_time = datetime.utcnow().astimezone(pytz.timezone('Asia/Dhaka')) \
                                               .strftime("%d/%m/%Y, %H:%M:%S")
                            m = re.search(r"\b\d{4,}\b|\b\d{2,}-\d{2,}\b|\d{2,} \d{2,}\b", msg['message'])
                            otp = m.group(0) if m else "N/A"
                            text = (
                                f"✨ <b> ROBIUL OTP Received</b> ✨\n\n"
                                f"⏰ <b>Time:</b> {bd_time}\n"
                                f"📞 <b>Number:</b> {msg['recipient']}\n"
                                f"🔧 <b>Service:</b> {msg['originator']}\n\n"
                                f"🔑 <b>OTP Code:</b> <code>{otp}</code>\n\n"
                                f"<blockquote>{escape_html(msg['message'])}</blockquote>"
                            )
                            send_to_telegram("otp", CHAT_ID1, text)
                        except Exception as e:
                            print("📥 Receiving OTPs from panel ✅")
        except Exception as e:
            print("🔴 Connection closed or ⚠️ error:", e)
            print("🔁 Reconnecting in 5s...")
            time.sleep(5)

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tasks = [
        loop.create_task(connect_ws()),
    ]
    loop.run_until_complete(asyncio.wait(tasks))

if __name__ == "__main__":
    main()
