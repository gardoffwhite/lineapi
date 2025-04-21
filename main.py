from fastapi import FastAPI, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
import requests as req
import json

app = FastAPI()

LINE_ACCESS_TOKEN = '0iM/gg2Fj9sfdfw9pgEa9bSqLquHGZTgXyVub75iHO3TngYJKrMRrKy15BgCdlrAaBmicPz8c/5dkwce2ebL28zVKpV/6SSdnOnSFzX92jyakeBbPZOKjkzT8duPa8kB+km4j49TPnB5TdpDM29G7AdB04t89/1O/w1cDnyilFU='
LINE_API_URL = 'https://api.line.me/v2/bot/message/push'
ADMIN_USER_ID = 'U85e0052a3176ddd793470a41b02b69fe'
ADMIN_PASSWORD = "admin123"  # สามารถเปลี่ยนรหัสผ่านได้ที่นี่

request_data_store = []

def send_line_message(user_id: str, message: str):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_ACCESS_TOKEN}'
    }
    data = {
        "to": user_id,
        "messages": [{
            "type": "text",
            "text": message
        }]
    }
    response = req.post(LINE_API_URL, headers=headers, data=json.dumps(data))
    if response.status_code != 200:
        print(f"Error sending message: {response.status_code}")
        print(response.text)


@app.get("/", response_class=HTMLResponse)
async def form_post():
    return """
    <html>
        <body>
            <h2>ขออัปเดตสเตตัส</h2>
            <form method="post" action="/submit">
                User ID: <input type="text" name="userid" required><br><br>
                ชื่อตัวละคร: <input type="text" name="charname" required><br><br>
                STR: <select name="str">
                    <option value="">-- เลือก --</option>
                    <option value="1000">1000</option>
                    <option value="1500">1500</option>
                    <option value="2000">2000</option>
                    <option value="2500">2500</option>
                    <option value="3000">3000</option>
                    <option value="3500">3500</option>
                    <option value="4000">4000</option>
                </select><br><br>
                DEX: <select name="dex">
                    <option value="">-- เลือก --</option>
                    <option value="1000">1000</option>
                    <option value="1500">1500</option>
                    <option value="2000">2000</option>
                    <option value="2500">2500</option>
                    <option value="3000">3000</option>
                    <option value="3500">3500</option>
                    <option value="4000">4000</option>
                </select><br><br>
                ESP: <select name="esp">
                    <option value="">-- เลือก --</option>
                    <option value="1000">1000</option>
                    <option value="1500">1500</option>
                    <option value="2000">2000</option>
                    <option value="2500">2500</option>
                    <option value="3000">3000</option>
                    <option value="3500">3500</option>
                    <option value="4000">4000</option>
                </select><br><br>
                SPT: <select name="spt">
                    <option value="">-- เลือก --</option>
                    <option value="1000">1000</option>
                    <option value="1500">1500</option>
                    <option value="2000">2000</option>
                    <option value="2500">2500</option>
                    <option value="3000">3000</option>
                    <option value="3500">3500</option>
                    <option value="4000">4000</option>
                </select><br><br>
                <input type="submit" value="ส่งคำขอ">
            </form>
        </body>
    </html>
    """


@app.post("/submit")
async def handle_request(
        userid: str = Form(...), charname: str = Form(...),
        str: str = Form(...), dex: str = Form(...),
        esp: str = Form(...), spt: str = Form(...)):

    request_data = {
        "userid": userid,
        "charname": charname,
        "str": str,
        "dex": dex,
        "esp": esp,
        "spt": spt,
        "status": "กำลังส่ง GM แก้ไข"
    }

    request_data_store.append(request_data)
    request_id = len(request_data_store) - 1

    message = f"มีคำขอแก้สเตตัสในเกม\n\nUserID: {userid}\nตัวละคร: {charname}\nSTR: {str}\nDEX: {dex}\nESP: {esp}\nSPT: {spt}"
    send_line_message(ADMIN_USER_ID, message)

    return RedirectResponse(url=f"/status/{request_id}", status_code=303)


@app.get("/status/{request_id}", response_class=HTMLResponse)
async def status_page(request_id: int):
    if request_id < 0 or request_id >= len(request_data_store):
        return "<h2>ไม่พบคำขอนี้</h2>"

    request = request_data_store[request_id]

    return f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="5">
        </head>
        <body>
            <h2>สถานะคำขอของ {request['charname']}</h2>
            <p>UserID: {request['userid']}</p>
            <p>STR: {request['str']} | DEX: {request['dex']} | ESP: {request['esp']} | SPT: {request['spt']}</p>
            <h3>สถานะล่าสุด: {request['status']}</h3>
            <p>หน้าจะรีเฟรชทุก 5 วินาที</p>
            <a href="/">กลับไปส่งคำขอใหม่</a>
        </body>
    </html>
    """


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard_form(request: Request):
    if request.cookies.get("admin_logged") == "true":
        return await show_admin_dashboard()
    
    return """
    <html>
        <body>
            <h2>กรอกรหัสผ่านแอดมิน</h2>
            <form method="post" action="/admin">
                รหัสผ่าน: <input type="password" name="password" required><br><br>
                <input type="submit" value="เข้าสู่แผงควบคุม">
            </form>
        </body>
    </html>
    """


@app.post("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, response: Response, password: str = Form(...)):

    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="ไม่อนุญาตให้เข้าถึง")

    response.set_cookie(key="admin_logged", value="true", httponly=True)

    return await show_admin_dashboard()


async def show_admin_dashboard():
    return f"""
    <html>
        <body>
            <h2>แผงควบคุมแอดมิน</h2>
            <h3>คำขอที่รออัปเดต:</h3>
            <ul>
                {''.join([f"<li>{i}: {req['charname']} ({req['userid']}) - สถานะ: {req['status']}</li>" for i, req in enumerate(request_data_store)])}
            </ul>
            <form action="/update_status" method="post">
                เลือกคำขอ (Request ID):
                <select name="request_id">
                    {''.join([f'<option value="{index}">{req["charname"]} - {req["userid"]}</option>' for index, req in enumerate(request_data_store)])}
                </select><br><br>

                สถานะใหม่:
                <select name="status">
                    <option value="กำลังส่ง GM แก้ไข">กำลังส่ง GM แก้ไข</option>
                    <option value="อยู่ระหว่างแก้ไข กรุณาออกจากเกม">อยู่ระหว่างแก้ไข กรุณาออกจากเกม</option>
                    <option value="แก้ไขสำเร็จ">แก้ไขสำเร็จ</option>
                </select><br><br>
                <input type="submit" value="อัปเดตสถานะ">
            </form>
        </body>
    </html>
    """


@app.post("/update_status")
async def update_status(request_id: int = Form(...), status: str = Form(...)):
    if request_id < 0 or request_id >= len(request_data_store):
        raise HTTPException(status_code=400, detail="ไม่พบคำขอนี้")

    request_data_store[request_id]["status"] = status
    request = request_data_store[request_id]

    message = f"คำขอของ {request['charname']} ({request['userid']}) ถูกอัปเดตสถานะเป็น: {status}"
    send_line_message(ADMIN_USER_ID, message)

    return RedirectResponse(url="/admin", status_code=303)


@app.get("/logout")
async def logout(response: Response):
    response.delete_cookie(key="admin_logged")
    return RedirectResponse(url="/admin", status_code=303)
