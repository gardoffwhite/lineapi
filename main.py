from fastapi import FastAPI, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import requests as req
import json

app = FastAPI()

# กำหนดเส้นทางของ template directory
templates = Jinja2Templates(directory="templates")

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
async def form_post(request: Request):
    return templates.TemplateResponse("request_form.html", {"request": request})


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
async def status_page(request: Request, request_id: int):
    if request_id < 0 or request_id >= len(request_data_store):
        return templates.TemplateResponse("error.html", {"request": request, "message": "ไม่พบคำขอนี้"})

    request = request_data_store[request_id]

    return templates.TemplateResponse("status_page.html", {"request": request})


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard_form(request: Request):
    if request.cookies.get("admin_logged") == "true":
        return await show_admin_dashboard(request)
    
    return templates.TemplateResponse("admin_login.html", {"request": request})


@app.post("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, response: Response, password: str = Form(...)):
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="ไม่อนุญาตให้เข้าถึง")

    response.set_cookie(key="admin_logged", value="true", httponly=True)

    return await show_admin_dashboard(request)


async def show_admin_dashboard(request: Request):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request, "requests": request_data_store})


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
