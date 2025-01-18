from fetch_data_and_signal import backtest_coins_by_params
#from analysis import full_analysis
import asyncio
import json
import logging
import multiprocessing



def read_data():
    try:
        with open('config.json', 'r') as f:
            data=json.load(f)
    except Exception as e:
        logging.error(f"Ошибка {e}")
        data={}
    return data


async def main():
    data=read_data()
    while True:

        command = input("Введите команду (run, analysis): ").strip().lower()
        if command == "run":
            data=read_data()
            await backtest_coins_by_params(data)
            print('Сбор данных завершен')

        elif command == "analysis":
            data=read_data()

            print('Начало анализа')
            #full_analysis(data)
            print("Анализ завершен")
        else:
            print("Неизвестная команда. Попробуйте снова.")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    asyncio.run(main())