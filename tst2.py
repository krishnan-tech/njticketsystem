import requests
import time

TELEGRAM_API_URL = "https://api.telegram.org/bot6411496327:AAH2Xs84lg1OYqioAFYJWv2WZPKJfdFgf_E"

def send_message(chat_id, text):
    params = {"chat_id": chat_id, "text": text}
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", params=params)

def make_api_request():
    url = "https://telegov.njportal.com/njmvc/CustomerCreateAppointments/GetAvailableDatesForMonth?duration=20&locationId=187&appointmentId=15&date=2024-04-01T04:00:00.000Z"
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    assert response.status_code == 200
    kk = response.json()
    return kk


def main():
    last = []
    while True:
        response = make_api_request()
        if response != []:
            if response != last:
                last = response
                send_message("-1002076086429", "Got Dates for "+", ".join([_[:10] for _ in response[:5]]))
            print("Response is not a blank list:", response)
        else:
            last = []
            print("Response is either blank or not a list.")
        
        time.sleep(60)

if __name__ == "__main__":
    main()