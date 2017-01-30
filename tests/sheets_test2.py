from oauth2client import client

flow = client.flow_from_clientsecrets(
    'sheets_key.json',
    scope='https://www.googleapis.com/auth/spreadsheets.readonly')