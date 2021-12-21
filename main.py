import keyboard
import os
import threading
import time
# Fix for dev environment.
if os.environ.get('dev'):
    os.environ['GPIOZERO_PIN_FACTORY'] = os.environ.get('GPIOZERO_PIN_FACTORY', 'mock')
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from gpiozero import CPUTemperature, LED
from threading import Timer

# Constants
ESC = "esc"
RESPONSE_KEYS = ["1", "2", "3", "4", "5"]
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '12U7PVLhj6NCvA50kiwy1HLujdZZyL5KNrnKMR3BdblU'
RESPONSES_SHEET_NAME = 'Device Responses'
TEMP_SHEET_NAME = 'Device Temperature'
RANGE_NAME = RESPONSES_SHEET_NAME + '!A1:B1'
TIME_LOG_CPU_TEMP_SECS = 10

# Global Objects
cpu = None
led = None
red_led = None
last_cpu_log_time = 0
enabled = True
key_state = {
    "1": False,
    "2": False,
    "3": False,
    "4": False,
    "5": False,
}


def init_gpio():
    global cpu, led, red_led
    if os.environ.get('dev'):
        return
    cpu = CPUTemperature()
    led = LED(17)
    red_led = LED(27)


def maybe_log_cpu_temp():
    global last_cpu_log_time, cpu
    if cpu is None:
        return
    if time.time() - last_cpu_log_time < TIME_LOG_CPU_TEMP_SECS:
        return
    last_cpu_log_time = time.time()
    thr = threading.Thread(target=record_cpu_temp, args=(cpu.temperature))
    thr.start()


def get_sheets_creds():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def record_cpu_temp(temp):
    if red_led is not None:
        red_led.on()
    creds = get_sheets_creds()
    try:
        service = build('sheets', 'v4', credentials=creds)
        # Call the Sheets API
        sheet = service.spreadsheets()
        values = [[time.time(), temp]]
        body = {'values': values}
        result = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID, range=TEMP_SHEET_NAME + '!A:B',
            valueInputOption="RAW", body=body).execute()
        print('{0} cells updated.'.format(result.get('updates').get('updatedCells')))
    except HttpError as err:
        print(err)
    if red_led is not None:
        red_led.off()


def record_response(response):
    if led is not None:
        led.on()
    creds = get_sheets_creds()
    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        values = [[time.time(), response]]
        body = {'values': values}
        result = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID, range=RESPONSES_SHEET_NAME + '!A:B',
            valueInputOption="RAW", body=body).execute()
        print('{0} cells updated.'.format(result.get('updates').get('updatedCells')))
    except HttpError as err:
        print(err)
    if led is not None:
        led.off()


def handle_key_state_change(key, new_state):
    # Only handle state changes based on RESPONSE_KEYS that have been released.
    if key in RESPONSE_KEYS and not new_state:
        thr = threading.Thread(target=record_response, args=(key))
        thr.start()
        # TODO: Handle cases where a key was pressed too quickly after another/simultaneously with another.


def handle_key_presses():
    global enabled, key_state
    if keyboard.is_pressed(ESC):
        enabled = False
        return
    for key in key_state:
        current_state = keyboard.is_pressed(key)
        if key_state[key] != current_state:
            key_state[key] = current_state
            handle_key_state_change(key, current_state)


def main():
    global enabled
    init_gpio()
    # TODO: Start up service when system starts.
    while enabled:
        keyboard.read_event()
        handle_key_presses()
        maybe_log_cpu_temp()


if __name__ == "__main__":
    main()
