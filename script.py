from PIL import Image
import subprocess
from config import tokeen
import requests
import time
import cv2
from pyzbar.pyzbar import decode
import json

TELEGRAM_API_URL = "https://api.telegram.org/bot6411496327:AAH2Xs84lg1OYqioAFYJWv2WZPKJfdFgf_E"
def get_updates(offset=None):
    params = {"offset": offset} if offset else {}
    response = requests.get(f"{TELEGRAM_API_URL}/getUpdates", params=params)
    return response.json().get("result", [])

def download_file(file_id, file_path):
    response = requests.get(f"{TELEGRAM_API_URL}/getFile", params={"file_id": file_id})
    file_url = response.json().get("result", {}).get("file_path")
    file_data = requests.get(f"https://api.telegram.org/file/bot6411496327:AAH2Xs84lg1OYqioAFYJWv2WZPKJfdFgf_E/{file_url}")
    with open(file_path, "wb") as f:
        f.write(file_data.content)

def send_message(chat_id, text):
    params = {"chat_id": chat_id, "text": text}
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", params=params)

def extract_colors_from_image(image_path, coordinates):
    img = Image.open(image_path)
    img = img.resize((590, 1280))
    colors = []
    for coord in coordinates:
        color = img.getpixel(coord)
        colors.append('#{:02x}{:02x}{:02x}'.format(*color))
    return colors[:4]

def update_css_file(css_path, colors):
    text_to_write = f''':root {{
        --first: {colors[0]};
        --stripone: {colors[1]};
        --striptwo: {colors[2]};
        --stripthree: {colors[3]};
    }}
    /* {time.time()} */
    '''

    with open(css_path, 'w') as file:
        file.write(text_to_write)

def scan_qr_code(image_path):
    img = Image.open(image_path)
    box = (336, 59, 533, 256)
    cropped_img = img.crop(box)
    cropped_img.save(f"qr.jpg")
    img = cv2.imread(f"qr.jpg")
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    qr_codes = decode(gray_img)
    for qr_code in qr_codes:
        data = qr_code.data.decode('utf-8')
        return data

def update_qrtemp(image_path):
    kk = scan_qr_code(image_path)
    reflst = [14,19,24,32,35,41,48,56]
    if len(kk)!=191:
        kklst = list(kk)
        tmplst = reflst[len(kk)-191:]
        for i in tmplst:
            kklst.insert(i," ")
        kk = "".join(kklst)
    template = [kk[0:14], kk[15:19], kk[20:24], kk[25:32], kk[33:35], kk[36:41], kk[42:48], kk[49:56], kk[57:192]]
    with open('../qrcode.json', 'w') as qr_file:
        qr_file.write(json.dumps(template))

def git_push_changes():
    subprocess.run(["cd", r"D:\ticketsystem"], check=True, shell=True)
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Updated_colors"], check=True)
    remote_url = f"https://dummytummy123:{tokeen}@github.com/dummytummy123/ticketsystem.git"
    subprocess.run(["git", "push", remote_url, "main"], check=True)

offset = None
while True:
    try:
        updates = get_updates(offset)
    except:
        time.sleep(30)
        continue
    if len(updates) > 0:
        update = updates[-1]
        offset = update["update_id"] + 1
        message = update.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        file_id = message.get("photo", [{}])[-1].get("file_id")
        if file_id is None:
            file_id = message.get("document", {}).get("file_id")
        if file_id:
            download_file(file_id, "image.jpg")
            image_path = 'image.jpg'
            # update_qrtemp(image_path)
            css_path = 'color.css'
            colors = extract_colors_from_image(image_path, [(305, 406), (108, 1070), (300, 1070), (480, 1070)])
            # colors = extract_colors_from_image(image_path, [(500, 842), (215, 2400), (585, 2400), (950, 2400)])
            if colors[2]=="#ffffff":
                # colors = extract_colors_from_image(image_path, [(600, 802), (215, 2125), (585, 2125), (950, 2125)])
                colors = extract_colors_from_image(image_path, [(105, 389), (110, 1090), (300, 1090), (475, 1090)])
            update_css_file(css_path, colors)
            git_push_changes()
            send_message(chat_id, "ok")
            get_updates(offset)
    
    print("Sleeping for 30")
    time.sleep(30)
