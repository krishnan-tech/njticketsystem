from flask import Flask, request, send_from_directory, send_file, render_template
import qrcode
from io import BytesIO
import os, json, time
from datetime import datetime
import pytz
import pandas as pd
from flask_cors import CORS
import requests
import time
import fcntl
import uuid

log_filename = 'countss.csv'
whitelist_file = 'whitelist.json'
replace_list_file = 'replace_list.json'
est_timezone = pytz.timezone('America/New_York')

TELEGRAM_API_URL = "https://api.telegram.org/bot6411496327:AAH2Xs84lg1OYqioAFYJWv2WZPKJfdFgf_E"

def send_message(chat_id, text):
    params = {"chat_id": chat_id, "text": text}
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", params=params)

app = Flask(__name__)
CORS(app)

def read_fileee(filenameee):
    with open(filenameee, 'r') as fn_file:
        fcntl.flock(fn_file, fcntl.LOCK_SH)
        filedata = json.load(fn_file)
        fcntl.flock(fn_file, fcntl.LOCK_UN)
    return filedata

def write_fileee(filenameee, dattaa):
    with open(filenameee, 'r+') as wl_file:
        fcntl.flock(wl_file, fcntl.LOCK_EX)
        wl_file.seek(0)
        json.dump(dattaa, wl_file)
        wl_file.truncate()
        fcntl.flock(wl_file, fcntl.LOCK_UN)



def read_whitelist():
    return read_fileee(whitelist_file)

def add_to_whitelist(new_user):
    whitelist = read_whitelist()
    whitelist.append(new_user)
    write_fileee(whitelist_file, whitelist)



def read_replacelist():
    return read_fileee(replace_list_file)

def add_to_replacelist(key, value):
    replace_list = read_replacelist()
    replace_list[key] = value
    write_fileee(replace_list_file, replace_list)

def remove_from_replacelist(key):
    replace_list = read_replacelist()
    if key in replace_list:
        del replace_list[key]
        write_fileee(replace_list_file, replace_list)


def log_request(device_identifier,client_ip, device_type, user_agent):
    if os.path.exists(log_filename):
        with open(log_filename, 'r') as log_file:
            log_data = log_file.read()
    else:
        log_data = ""
    dtn = datetime.now(est_timezone)
    log_data += f"{device_identifier}\t{dtn.strftime('%Y-%m-%d')}\t{dtn.strftime('%H:%M:%S')}\t{client_ip}\t{user_agent}\n"
    if device_identifier != "HS":
        send_message("-4149600501", device_identifier)
    with open(log_filename, 'w') as log_file:
        log_file.write(log_data)

@app.route('/')
def home():
    return f'Running'

@app.route('/api/addDevice', methods=["POST"])
def addDevice():
    whitelist = read_whitelist()
    dev_id = request.get_json().get('deviceIdentifier')
    if dev_id == "":
        return "Not possible"
    if dev_id not in whitelist:
        add_to_replacelist(str(uuid.uuid4()).upper().split("-")[-1], dev_id)
        return "Added"
    else:
        return "Already in List"

@app.route('/api/listDeviceIdentifiers', methods=["GET"])
def listDeviceIdentifiers():
    return read_whitelist()

@app.route('/api/listScratchCodes', methods=["GET"])
def listScratchCodes():
    return read_replacelist()

@app.route('/api/getRegisteredDevices', methods=['GET'])
def get_registered_devices():
    data = pd.read_csv(log_filename, sep="\t")
    data= data[data['a'] != "HS"]
    data["e"] = data["e"].apply(lambda x: x[x.index("(")+1:x.index(")")])
    data = data.to_dict('records')
    return data[::-1]

@app.route('/verifydi', methods=["GET"])
def VerifyDeviceIdentifiers():
    device_identifier = request.args.get('device_identifier')
    replace_list = read_replacelist()
    if device_identifier in replace_list:
        return_val = replace_list[device_identifier]
        remove_from_replacelist(device_identifier)
        add_to_whitelist(return_val)
        return {"devide": return_val, "isValid": True}, 200
    elif device_identifier in read_whitelist():
        return {"devide": device_identifier, "isValid": True}, 200
    else:
        return {"isValid": False}, 400

@app.route('/get_css')
def get_css():
    client_ip = request.headers.get('X-Real-IP') or request.remote_addr
    device_type = request.user_agent.platform
    user_agent = request.user_agent.string
    device_identifier = request.args.get('device_identifier')
    if not device_identifier:
        return "Identifier required", 400
    if device_identifier not in read_whitelist():
        return "Identifier required", 400
    print(client_ip, device_type, user_agent)
    log_request(device_identifier,client_ip, device_type, user_agent)
    css_filename = f"color.css"
    return send_from_directory('ticketsystem', css_filename)

@app.route('/generate_qr', methods=['GET'])
def generate_qr():
    device_identifier = request.args.get('device_identifier')
    print(device_identifier,flush=True)
    if not device_identifier:
        return "Identifier required", 400
    if device_identifier not in read_whitelist():
        return "Identifier required", 400
    offset = int(est_timezone.localize(datetime(datetime.now().year, 1, 1, 0, 0, 0)).timestamp())
    tss = str((int(time.time())-offset))+"        "
    fil_nam = 'qrcode.json'
    with open(fil_nam, 'r') as qr_file:
        qrtemp = json.load(qr_file)
    data = (qrtemp[0]+tss[0]+qrtemp[1]+tss[1]+qrtemp[2]+tss[2]+qrtemp[3]+tss[3]+qrtemp[4]+tss[4]+qrtemp[5]+tss[5]+qrtemp[6]+tss[6]+qrtemp[7]+tss[7]+qrtemp[8]).replace(" ","")
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=0,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_stream = BytesIO()
    img.save(img_stream, format='PNG')
    img_stream.seek(0)
    return send_file(img_stream, mimetype='image/png', as_attachment=True, download_name='qrcode.png')

if __name__ == '__main__':
    app.run(host="0.0.0.0")
