from __future__ import print_function
import os.path
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


class GoogleSheet:
    SPREADSHEET_ID = ''
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    service = None
    range = ''

    def __init__(self, SPREADSHEET_ID, range):
        self.SPREADSHEET_ID = SPREADSHEET_ID
        self.range = f'{range}!%s:%s'
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print('flow')
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('sheets', 'v4', credentials=creds)

    def update_range_values(self, range, values):
        data = [{
            'range': range,
            'values': values
        }]
        body = {
            'valueInputOption': 'USER_ENTERED',
            'data': data
        }
        result = self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.SPREADSHEET_ID,
                                                                  body=body).execute()
        print('{0} cells updated.'.format(result.get('totalUpdatedCells')))

    def set_values(self, r1, r2, val):
        data = [{
            'range': self.range % (r1, r2),
            'values': val
        }]
        body = {
            'valueInputOption': 'USER_ENTERED',
            'data': data
        }
        self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.SPREADSHEET_ID, body=body).execute()
        # print('{0} cells updated.'.format(result.get('totalUpdatedCells')))

    def get_values(self, r1, r2):
        values = self.service.spreadsheets() \
            .values() \
            .get(spreadsheetId=self.SPREADSHEET_ID, range=self.range % (r1, r2)) \
            .execute() \
            .get('values', [])
        if values:
            return values
        else:
            return None

    def end_file(self):
        r = 'A%d'
        i = 1
        while True:
            if self.get_values(r % i, r % i):
                i += 1
            else:
                return i


class GoogleSheetAccounting(GoogleSheet):
    def __init__(self):
        super().__init__('1JGY5rMLUvQkHQXyotVoxXx2Rfg1As_pSjrZGinOBdG4', 'Accounting')
        self.current_end_of_file = self.end_file()

    def enter_values_to_end(self, category, date, cost, info, user, time):
        list_val = [[self.current_end_of_file - 1, category, date, cost, info, user, time]]
        self.set_values(f'A{self.current_end_of_file}', f'G{self.current_end_of_file}', list_val)
        self.current_end_of_file += 1

    def update_end_of_file(self):
        self.current_end_of_file = self.end_file()


class GoogleSheetEating(GoogleSheet):
    def __init__(self):
        super().__init__('14u5PTQqWKkcUnFwDcnO8LL6Z7Inxz3wo5XwHK6JtZ9Y', 'Eating')
        self.current_end_of_file = self.end_file()

    def enter_values_to_end(self, date, char, food, info, user, time):
        list_val = [[self.current_end_of_file - 1, date, char, food, info, user, time]]
        self.set_values(f'A{self.current_end_of_file}', f'G{self.current_end_of_file}', list_val)
        self.current_end_of_file += 1

    def update_end_of_file(self):
        self.current_end_of_file = self.end_file()
