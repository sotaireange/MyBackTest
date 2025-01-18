import os
import csv
import logging
import asyncio
import concurrent.futures
import json
import pandas as pd
import numpy as np
import time
logging.basicConfig(level=logging.INFO)

from .get_combinations_params import get_data_for_signal,clear_combinations
from .get_coins import find_coin,proof_coins
from .get_df import get_df
from .backtest import backtest
from .utils import *

def iter_coin_by_params(coins,data_signals,fieldnames,indicator,folder_path,folder_result,date_range):
    try:
        #time.sleep(np.random.randint(1,3))
        for i,coin in enumerate(coins):
            df=get_df(folder_path,coin,date_range)
            rows=[]
            try:
                df_old=pd.read_csv(f'{folder_result}/{coin}.csv')
                combinations=clear_combinations(data_signals,df_old)
            except FileNotFoundError:
                combinations=data_signals
            if len(combinations)==0: continue
            for comb in combinations:
                try:
                    res=backtest(df,comb,indicator)
                    row = get_row(coin,comb,res,indicator)
                    rows.append(row)
                except Exception as e:
                    logging.error(f'error {coin}\n{comb}\n{e}',exc_info=True)


            file_path=f'{folder_result}/{coin}.csv'
            file_exists = os.path.isfile(file_path)
            with open(file_path, 'a+', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerows(rows)


            logging.info(f'{coin} is finish {i+1}/{len(coins)}')
    except Exception as e:
        logging.error(f'Main error {e}',exc_info=True)



async def backtest_coins_by_params(data): #TODO: Гдето тут нужно исправитть чтобы использовать folder
    try:
        indicator=data['indicator']
        fieldnames=get_fieldnames(indicator)
        timeframe=data[indicator].get('params',{}).get('timeframe',30)
        daterange=data.get('date_range','2000-1-1/2099-1-1')
        top=data[indicator].get('params',{}).get('top',100)

        folder_path=data['folder_path']

        folder_path_result=get_patch_to_result(timeframe,indicator,daterange)

        if not os.path.exists(folder_path_result):
            os.makedirs(folder_path_result,exist_ok=True)




        print(f'Сбор монеток')
        coins=find_coin(folder_path)
        print(f'Найдено монеток {len(coins)}')
        print("Проверка на соответвие диапазона дат")
        coins=proof_coins(folder_path,coins,daterange)
        print(f'Монеток соотвествуют диапазону {len(coins)}')


        data_signals=get_data_for_signal(data[indicator]['params'],indicator=indicator)
        logging.info(msg=f'Начало сбора, параметры:\n{data[indicator].get('params',{})}\n'
                         f'Кол-во Комбинаций {len(data_signals)}')
        num_processes = data.get('core',10)
        coin_chunks = np.array_split(coins, num_processes)
        try:
            with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes) as executor:
                futures = [
                    executor.submit(iter_coin_by_params, chunk,data_signals,fieldnames,indicator,folder_path,folder_path_result,daterange)
                    for chunk in coin_chunks
                ]
        except Exception as e:
            logging.error(f"ERROR WHEN CREATE MULTIPROC {e}")
        logging.info(f'Конец сбора')
    except Exception as e:
        logging.error(f"ERROR FULL {e}",exc_info=True)


if __name__ == '__main__':
    with open('config.json', 'r') as f:
        data=json.load(f)
    asyncio.run(backtest_coins_by_params(data))
