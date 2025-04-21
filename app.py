from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

logout_url = "http://nage-warzone.com/admin/?logout=session_id()"
login_url = "http://nage-warzone.com/admin/index.php"
charedit_url = "http://nage-warzone.com/admin/charedit.php"

login_payload = {
    "username": "admin",
    "password": "3770",
    "submit": "Submit"
}

session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

def get_character_data(charname=""):
    try:
        session.post(login_url, data=login_payload, headers=headers, timeout=20)
        char_resp = session.post(
            charedit_url,
            data={"charname": charname, "searchname": "Submit"},
            headers=headers, timeout=20
        )
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

@app.route('/', methods=['GET', 'POST'])
def index():
    char_data = None
    charname = ""

    if request.method == 'POST':
        charname = request.form.get('charname', '').strip()
        char_data = get_character_data(charname)

    return render_template('admin_dashboard.html', char_data=char_data, charname=charname)

if __name__ == '__main__':
    app.run(debug=True)
