import os
from .get_df import proof_date_range



def find_coin(folder_path):
    coins = list()
    for filename in os.listdir(folder_path):
        coins.append(filename.split('.')[0])
    return coins

def proof_coins(folder_path,coins,date_range):
    coins_filt = list()
    for coin in coins:
        if proof_date_range(folder_path, coin, date_range):
            coins_filt.append(coin)
    return coins_filt
