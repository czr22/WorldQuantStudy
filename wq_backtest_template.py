""""
WorldQuant Brain Backtest Template
"""
import time
from concurrent.futures.thread import ThreadPoolExecutor
from requests.auth import HTTPBasicAuth
import requests
import pandas as pd

class WorldQuantBrainBacktest:
    def __init__(self,username:str,password:str) -> None:
        self.sess = requests.Session()
        self.sess.auth = HTTPBasicAuth(username, password)
        self.response = self.sess.post('https://api.worldquantbrain.com/authentication')
        if self.response.status_code != 201:
            print(f'Login failed {self.response.status_code}')
        else:
            print('Login successful')
    def backtest(self,par:dict,alpha:str):
        """
        parms
        UNIVERSE : ['TOP3000','TOP1000','TOP500','TOP200','TOPSP500']
        DELAY : [0,1]
        DECAY : Interger Numer
        NEUTRALIZATION : ['INDUSTRY','SECTOR','MARKET','SUBINDUSTRY','NONE']
        TRUNCATION : [0.01,0.05,0.1]
        PASTEURIZATION : ['ON','OFF']
        NANHANDLING : ['OFF','ON']
        parameter_grid = itertools.product(UNIVERSE,DELAY,DECAY,NEUTRALIZATION,TRUNCATION,PASTEURIZATION,NANHANDLING)
        """
        simulation_data = {
            'type': 'REGULAR',
            'settings': {
                'instrumentType': 'EQUITY',
                'region': 'USA',
                'universe': par.get('universe', 'TOP3000'),
                'delay': par.get('delay', 1),
                'decay': par.get('decay', 0),
                'neutralization': par.get('neutralization', 'INDUSTRY'),
                'truncation': par.get('truncation', 0.01),
                'pasteurization': par.get('pasteurization', 'ON'),
                'unitHandling': 'VERIFY',
                'nanHandling': par.get('nanHandling', 'ON'),
                'language': "FASTEXPR",
                'visualization': False,
            },
            'regular': alpha
        }
        response = self.sess.post(
            'https://api.worldquantbrain.com/simulations', json=simulation_data)
        if response.status_code != 201:
            print(f'Simulation failed {response.status_code}')
            return
        sim_progress_url = response.headers.get('Location','')
        sim_response = self.sess.get(sim_progress_url)
        retry_after = float(sim_response.headers.get('Retry-After', 0))
        while retry_after != 0:
            sim_response = self.sess.get(sim_progress_url)
            retry_after = float(sim_response.headers.get('Retry-After', 0))
            time.sleep(retry_after)
        alphaid = sim_response.json().get('alpha', None)
        if alphaid is not None:
            print(f'Parameters: {par}, Alpha ID: {alphaid}')
        else:
            print(f'Simulation Failed: {sim_response.json()["message"]}')

if __name__ == '__main__':
    USERNAME = ''
    PASSWORD = ''
    wb = WorldQuantBrainBacktest(USERNAME, PASSWORD)
    parm = {
        'universe': 'TOP1000',
        'delay': 1,
        'decay': 10,
        'neutralization': 'INDUSTRY',
        'truncation': 0.03,
        'pasteurization': 'ON',
        'nanHandling': 'ON'
        }
    alpha_data_fields = pd.read_csv('Replace with your path to data field CSV file')
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for fields in alpha_data_fields['id']:
            ALPHA = ""
            futures.append(executor.submit(wb.backtest, parm, ALPHA))
        for future in futures:
            future.result()