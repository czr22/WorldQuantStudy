"""
Get data fields from WorldQuant Brain API and save to CSV files.
"""
from requests.auth import HTTPBasicAuth
import requests
import pandas as pd

USERNAME = ''
PASSWORD = ''

sess = requests.Session()
sess.auth = HTTPBasicAuth(USERNAME, PASSWORD)
response = sess.post('https://api.worldquantbrain.com/authentication')


for universe in ['TOP3000', 'TOP1000', 'TOP500', 'TOP200', 'TOPSP500']:
    for delay in [0, 1]:
        data_set_url = f'https://api.worldquantbrain.com/data-sets?instrumentType=EQUITY&region=USA&delay={delay}&universe={universe}&limit=50'
        data_set_response = sess.get(data_set_url)
        payload = data_set_response.json()
        totalFieldCount = 0
        for result in payload['results']:
            totalFieldCount += result['fieldCount']
        print(f'{universe} delay {delay} total field count: {totalFieldCount}')
        alpha_data_fields = pd.DataFrame()
        for offset in range(0, totalFieldCount+1, 50):
            data_field_url = f'https://api.worldquantbrain.com/data-fields?instrumentType=EQUITY&region=USA&delay={delay}&universe={universe}&limit=50&offset={offset}'
            data_field_response = sess.get(data_field_url)
            payload = data_field_response.json()
            alpha_data_fields = pd.concat([alpha_data_fields, pd.DataFrame(
                payload.get('results', []))], ignore_index=True)
        print(alpha_data_fields.head())
        alpha_data_fields.to_csv(f'{universe}_delay{delay}.csv', index=False)
