from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    '/Users/colinh/Repositories/mp/src/config/chrendin_sheets_key.json', scopes)

service = build('sheets', 'v4', credentials=credentials)

spreadsheetId = '1lz4g3-WvT8EjVc2hogalhnGQmkMb1d1fIvatpLUsano'
rangeName = 'Twitter Featured!A2:E'
result = service.spreadsheets().values().get(
    spreadsheetId=spreadsheetId, range=rangeName).execute()
values = result.get('values', [])
if not values:
    print('No data found.')
else:
    print('Name, Major:')
    for row in values:
        row = [x.encode('ascii', 'ignore') for x in row]
        # Print columns A and E, which correspond to indices 0 and 4.
        print row