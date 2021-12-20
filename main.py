import time
import keyboard
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from gpiozero import CPUTemperature, LED
from threading import Timer

# Constants
LED_KEY = "1"
ESC = "esc"
RESPONSE_KEYS = ["1", "2", "3", "4", "5"]
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '12U7PVLhj6NCvA50kiwy1HLujdZZyL5KNrnKMR3BdblU'
SHEET_NAME = 'Device Responses'
RANGE_NAME = SHEET_NAME + '!A1:B1'

# Global Objects
cpu = CPUTemperature()
led = LED(17)
enabled = True
key_state = {
    "1": False,
    "2": False,
    "3": False,
    "4": False,
    "5": False,
}


def record_response(response):
    """Shows basic usage of the Sheets API.
        Prints values from a sample spreadsheet.
        """
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

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        values = [[time.time(), response]]
        body = {'values': values}
        result = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID, range=SHEET_NAME + '!A:B',
            valueInputOption="RAW", body=body).execute()
        print('{0} cells updated.'.format(result.get('updates').get('updatedCells')))
    except HttpError as err:
        print(err)


def handle_key_state_change(key, new_state):
    # Only handle state changes based on RESPONSE_KEYS that have been released.
    if key in RESPONSE_KEYS and not new_state:
        print("Released " + key)
        led.on()
        record_response(key)
        t = Timer(1.0, led.off)
        t.start()
        # TODO: Handle cases where a key was pressed too quickly after another/simultaneously with another.
        # TODO: Handle cases where the response might take too long.


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
    # TODO: Don't do this. Record every n ms instead of looping continuously for the sake of energy/heat.
    # TODO: Record CPU temperature in a sheet as well.
    while enabled:
        handle_key_presses()


if __name__ == "__main__":
    main()
