from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# URL ที่ใช้ในการ login และดึงข้อมูลตัวละคร
login_url = "http://nage-warzone.com/admin/index.php"
charedit_url = "http://nage-warzone.com/admin/charedit.php"
logout_url = "http://nage-warzone.com/admin/?logout=session_id()"

# ข้อมูลสำหรับการ login
login_payload = {"username": "admin", "password": "3770", "submit": "Submit"}
session = requests.Session()
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# ตัวแปรสำหรับเก็บคำขอที่เข้ามา
request_data_store = []

LINE_ACCESS_TOKEN = '0iM/gg2Fj9sfdfw9pgEa9bSqLquHGZTgXyVub75iHO3TngYJKrMRrKy15BgCdlrAaBmicPz8c/5dkwce2ebL28zVKpV/6SSdnOnSFzX92jyakeBbPZOKjkzT8duPa8kB+km4j49TPnB5TdpDM29G7AdB04t89/1O/w1cDnyilFU='  # ใช้ Channel Access Token ของคุณ
LINE_API_URL = 'https://api.line.me/v2/bot/message/push'  # URL สำหรับส่งข้อความ
ADMIN_USER_ID = 'U85e0052a3176ddd793470a41b02b69fe'  # ใช้ User ID ของแอดมินที่ต้องการให้แชทบอทส่งข้อความไปหา

# ฟังก์ชันในการดึงข้อมูลตัวละคร
def get_character_data(charname=""):
    try:
        session.post(login_url, data=login_payload, headers=headers, timeout=20)
        char_resp = session.post(charedit_url, data={"charname": charname, "searchname": "Submit"}, headers=headers, timeout=20)
        soup = BeautifulSoup(char_resp.text, "html.parser")
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

    placeholders = soup.find_all('input', {'placeholder': True})
    data = {}
    for placeholder in placeholders:
        field_name = placeholder.get('name')
        placeholder_value = placeholder.get('placeholder')
        data[field_name] = int(placeholder_value) if placeholder_value.isdigit() else 0

    lvpoint = int(data.get("lvpoint", 0))
    stats_str_dex = ['str', 'dex']
    existing_str_dex = [data.get("str", 0), data.get("dex", 0)]
    distributed_str_dex = distribute_lvpoint(lvpoint, stats_str_dex, existing_str_dex)

    data.update(distributed_str_dex)
    return data

def distribute_lvpoint(lvpoint, stats_group, existing_values):
    total_existing = sum(existing_values)
    total_points = lvpoint + total_existing
    points_per_stat = total_points // len(stats_group)
    remainder = total_points % len(stats_group)

    distributed_points = {stat: points_per_stat for stat in stats_group}
    for i, stat in enumerate(stats_group):
        if i < remainder:
            distributed_points[stat] += 1
    return distributed_points

# ฟังก์ชันการส่งข้อความแจ้งเตือนผ่าน LINE
def send_line_message(user_id: str, message: str):
    line_api_url = 'https://api.line.me/v2/bot/message/push'
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
    response = requests.post(line_api_url, headers=headers, json=data)
    if response.status_code != 200:
        print(f"Error sending message: {response.status_code}")
        print(response.text)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
        <html>
            <head>
                <title>FastAPI + Flask</title>
            </head>
            <body>
                <h1>Welcome to FastAPI and Flask App!</h1>
            </body>
        </html>
    """

@app.get("/admin")
async def admin_dashboard():
    return {"message": "Admin Dashboard"}

@app.post("/admin")
async def submit_charname(request: Request):
    form = await request.form()
    charname = form.get('charname')
    if charname:
        char_data = get_character_data(charname)
        request_data_store.append({
            'charname': charname,
            'data': char_data,
            'status': 'กำลังส่ง GM แก้ไข'
        })
        message = f"มีคำขอแก้ไขข้อมูลตัวละคร: {charname}"
        send_line_message(ADMIN_USER_ID, message)
    return {"message": "Request submitted successfully"}

@app.post("/update_status/{request_id}")
async def update_status(request_id: int, request: Request):
    form = await request.form()
    new_status = form.get('status')
    if request_id < len(request_data_store):
        request_data_store[request_id]['status'] = new_status
        message = f"คำขอ {request_data_store[request_id]['charname']} เปลี่ยนสถานะเป็น: {new_status}"
        send_line_message(ADMIN_USER_ID, message)
    return {"message": "Status updated successfully"}
