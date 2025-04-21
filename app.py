from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

login_url = "http://nage-warzone.com/admin/index.php"
charedit_url = "http://nage-warzone.com/admin/charedit.php"
login_payload = {"username": "admin", "password": "3770", "submit": "Submit"}
session = requests.Session()
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

@app.route('/get-char', methods=['POST'])
def get_char_api():
    charname = request.form.get("charname", "")
    try:
        session.post(login_url, data=login_payload, headers=headers)
        char_resp = session.post(charedit_url, data={"charname": charname, "searchname": "Submit"}, headers=headers)
        soup = BeautifulSoup(char_resp.text, "html.parser")
        placeholders = soup.find_all('input', {'placeholder': True})
        data = {p.get('name'): int(p.get('placeholder')) if p.get('placeholder').isdigit() else 0 for p in placeholders}
        lvpoint = int(data.get("lvpoint", 0))
        str_dex = ['str', 'dex']
        existing_values = [data.get("str", 0), data.get("dex", 0)]
        distributed = distribute_lvpoint(lvpoint, str_dex, existing_values)
        data.update(distributed)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

def distribute_lvpoint(lvpoint, stats_group, existing_values):
    total_existing = sum(existing_values)
    total_points = lvpoint + total_existing
    points_per_stat = total_points // len(stats_group)
    remainder = total_points % len(stats_group)
    result = {stat: points_per_stat for stat in stats_group}
    for i, stat in enumerate(stats_group):
        if i < remainder:
            result[stat] += 1
    return result

if __name__ == '__main__':
    app.run(debug=True, port=5000)
