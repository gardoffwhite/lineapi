from fastapi import FastAPI, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import requests as req
import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")

LINE_ACCESS_TOKEN = 'YOUR_LINE_ACCESS_TOKEN'
LINE_API_URL = 'https://api.line.me/v2/bot/message/push'
ADMIN_USER_ID = 'YOUR_ADMIN_USERID'
ADMIN_PASSWORD = "admin123"
request_data_store = []

def send_line_message(user_id: str, message: str):
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {LINE_ACCESS_TOKEN}'}
    data = {"to": user_id, "messages": [{"type": "text", "text": message}]}
    response = req.post(LINE_API_URL, headers=headers, data=json.dumps(data))
    if response.status_code != 200:
        print(f"Error sending message: {response.status_code}")

@app.get("/", response_class=HTMLResponse)
async def form_post(request: Request):
    return templates.TemplateResponse("request_form.html", {"request": request})

@app.post("/submit")
async def handle_request(userid: str = Form(...), charname: str = Form(...), str: str = Form(None), dex: str = Form(None), esp: str = Form(None), spt: str = Form(None)):
    if not userid or not charname:
        raise HTTPException(status_code=400, detail="กรุณากรอก UserID และ ชื่อตัวละคร")
    request_data = {"userid": userid, "charname": charname, "str": str or "ไม่ระบุ", "dex": dex or "ไม่ระบุ", "status": "กำลังส่ง GM แก้ไข"}
    request_data_store.append(request_data)
    request_id = len(request_data_store) - 1
    message = f"มีคำขอแก้สเตตัสในเกม\nUserID: {userid}\nตัวละคร: {charname}\nSTR: {str}\nDEX: {dex}"
    send_line_message(ADMIN_USER_ID, message)
    return RedirectResponse(url=f"/status/{request_id}", status_code=303)

@app.get("/status/{request_id}", response_class=HTMLResponse)
async def status_page(request: Request, request_id: int):
    if request_id < 0 or request_id >= len(request_data_store):
        return templates.TemplateResponse("error.html", {"request": request, "message": "ไม่พบคำขอนี้"})
    req_data = request_data_store[request_id]
    return templates.TemplateResponse("status_page.html", {"request": request, "request_data": req_data})

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
    req_data = request_data_store[request_id]
    message = f"คำขอของ {req_data['charname']} ({req_data['userid']}) ถูกอัปเดตสถานะเป็น: {status}"
    send_line_message(ADMIN_USER_ID, message)
    return RedirectResponse(url="/admin", status_code=303)

@app.get("/logout")
async def logout(response: Response):
    response.delete_cookie(key="admin_logged")
    return RedirectResponse(url="/admin", status_code=303)
