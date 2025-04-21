import requests
from bs4 import BeautifulSoup

logout_url = "http://nage-warzone.com/admin/?logout=session_id()"
login_url = "http://nage-warzone.com/admin/index.php"
charedit_url = "http://nage-warzone.com/admin/charedit.php"

login_payload = {
    "username": "admin",  # ชื่อผู้ใช้งาน
    "password": "3770",    # รหัสผ่าน
    "submit": "Submit"     # ค่าจากปุ่ม submit
}

session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

timeout_time = 20

# ฟังก์ชันสำหรับเข้าสู่ระบบ
def login():
    try:
        login_page_resp = session.get(login_url, headers=headers, timeout=timeout_time)
        login_resp = session.post(login_url, data=login_payload, headers=headers, timeout=timeout_time)

        soup_login = BeautifulSoup(login_resp.text, "html.parser")
        login_form = soup_login.find("form", {"id": "form2"})
        if login_form:
            return False
        return True
    except requests.exceptions.RequestException:
        return False

# ฟังก์ชันค้นหาตัวละคร
def search_character(charname):
    if not login():
        return None

    char_payload = {
        "charname": charname,
        "searchname": "Submit"
    }

    try:
        char_resp = session.post(charedit_url, data=char_payload, headers=headers, timeout=timeout_time)
        soup_char = BeautifulSoup(char_resp.text, "html.parser")
        placeholders = soup_char.find_all('input', {'placeholder': True})

        data = {}
        for placeholder in placeholders:
            field_name = placeholder.get('name')
            placeholder_value = placeholder.get('placeholder')
            data[field_name] = int(placeholder_value) if placeholder_value.isdigit() else 0

        return data
    except requests.exceptions.RequestException:
        return None
