import backtrader as bt
import math


class VolumeWeightedMovingAverage(bt.Indicator):
    lines = ('vwma',)
    params = dict(period=28,
                  source=None)

    def __init__(self):
        source_volume = self.params.source * self.data.volume
        cumulative_price_volume = bt.indicators.MovingAverageSimple(source_volume, period=self.params.period)
        cumulative_volume = bt.indicators.MovingAverageSimple(self.data.volume, period=self.params.period)
        self.lines.vwma = cumulative_price_volume / cumulative_volume


class MSS(bt.Strategy):
    params = (
        ('take_profit_percent', 500.0),  # Процент тейк-профита
        ('stop_loss_percent', 99.0),  # Процент стоп-лосса
        ('rsi_length', 14),  # Длина RSI
        ('rsi_upper', 70),  # Уровень RSI для продаж
        ('ma_length', 28),
        ('rsi_bb_length', 3),  # Длина MA
        ('deviation', 2.0),  # Отклонение для Bollinger Bands
        ('MA_type', "VWMA"),
        ('rsi_type', 'cross'),
        ('rsi_type_sell','VWMA'),
        ('break_sell', 'marsi')
    )

    def __init__(self):
        # Индикаторы
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_length)

        match self.params.MA_type:
            case "SMA":
                self.ma = bt.indicators.MovingAverageSimple(self.rsi, period=self.params.ma_length)
            case "EMA":
                self.ma = bt.indicators.ExponentialMovingAverage(self.rsi, period=self.params.ma_length)
            case "SMMA":
                self.ma = bt.indicators.SmoothedMovingAverage(self.rsi, period=self.params.ma_length)
            case "WMA":
                self.ma = bt.indicators.WeightedMovingAverage(self.rsi, period=self.params.ma_length)
            case "VWMA":
                self.ma = VolumeWeightedMovingAverage(self.data, source=self.rsi, period=self.params.ma_length)
            case _:
                raise ValueError(f"Unsupported MA type: {self.params.MA_type}")

        match self.params.rsi_type_sell:
            case "SMA":
                self.rsi_bb = bt.indicators.MovingAverageSimple(self.rsi, period=self.params.rsi_bb_length)
            case "EMA":
                self.rsi_bb = bt.indicators.ExponentialMovingAverage(self.rsi, period=self.params.rsi_bb_length)
            case "SMMA":
                self.rsi_bb = bt.indicators.SmoothedMovingAverage(self.rsi, period=self.params.rsi_bb_length)
            case "WMA":
                self.rsi_bb = bt.indicators.WeightedMovingAverage(self.rsi, period=self.params.rsi_bb_length)
            case "VWMA":
                self.rsi_bb = VolumeWeightedMovingAverage(self.data, source=self.rsi, period=self.params.rsi_bb_length)
            case _:
                raise ValueError(f"Unsupported MA type: {self.params.MA_type}")

        # Переменные состояния
        self.sell_signal = False
        self.close_position = False
        self.break_sell=False

    def next(self):

        if self.params.rsi_type == 'cross':
            if self.rsi[0] < self.ma[0] and (
                    self.rsi[-2] > self.params.rsi_upper and self.rsi[-1] <= self.params.rsi_upper):
                self.sell_signal = True
        elif self.params.rsi_type == 'rsi_bb':
            if self.rsi_bb[0] < self.ma[0] and (self.rsi_bb[-1] > self.params.rsi_upper and self.rsi[0] <= self.params.rsi_upper):
                self.sell_signal = True
        elif self.params.rsi_type == 'crossfast':
            if self.rsi[0] < self.ma[0] and (
                    self.rsi[-1] > self.params.rsi_upper and self.rsi[0] <= self.params.rsi_upper):
                self.sell_signal = True

        match self.params.break_sell:
            case 'marsi':
                if self.rsi[0] > self.ma[0]:
                    self.break_sell = True
                    self.sell_signal = False
            case 'maup':
                if self.rsi[0]>self.ma[0] or self.rsi[0]>self.params.rsi_upper:
                    self.break_sell = True
                    self.sell_signal = False
            case 'rsi_bb':
                if self.ma[0]<self.rsi_bb[0]:
                    self.break_sell = True
                    self.sell_signal = False




        if self.position and self.break_sell:
            self.close()
            self.break_sell=False
            self.sell_signal=False


        # Открытие первой позиции
        if self.sell_signal and not self.position:
            self.sell()
            self.sell_signal=False



def start_backtest(df, cerebro):
    bt_feed = bt.feeds.PandasData(dataname=df)

    cerebro.adddata(bt_feed)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='tradeanalyzer')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")

    cerebro.addsizer(bt.sizers.PercentSizer, percents=3)
    cerebro.broker.setcommission(commission=0.00075)
    cash = 100000
    cerebro.broker.setcash(cash)

    strats = cerebro.run()

    res_ta = strats[0].analyzers.getbyname('tradeanalyzer').get_analysis()
    res_dd = strats[0].analyzers.getbyname('drawdown').get_analysis()
    res_sh = strats[0].analyzers.getbyname('sqn').get_analysis()

    res = {}
    res['pnl_perc'] = res_ta.get('pnl', {}).get('net', {}).get('total', 0) / cash * 100 if cash else 0
    res['pnl_average_perc'] = res_ta.get('pnl', {}).get('net', {}).get('average', 0) / cash * 100 if cash else 0
    res['sqn'] = res_sh.get('sqn', 0)
    res['moneydown'] = res_dd.get('max', {}).get('drawdown', 0)
    res['won'] = res_ta.get('won', {}).get('total', 1)
    res['lost'] = res_ta.get('lost', {}).get('total', 1)
    res['winrate'] = round(res['won'] / (res['won'] + res['lost']), 2)
    return res


def backtest_coin(df, data_signals):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(
        MSS,
        rsi_length=data_signals['rsi_length'],
        ma_length=data_signals['ma_length'],
        MA_type=data_signals['MA_type'],
        rsi_type=data_signals['rsi_type'],
        break_sell=data_signals['break_sell'],
        rsi_upper=data_signals['rsi_upper'],
        rsi_bb_length=data_signals['rsi_sell'],
        rsi_type_sell=data_signals['rsi_type_sell']
    )
    res = start_backtest(df, cerebro)

    return res


def backtest(df, data_signal, indicator):
    if indicator == 'rsi_ma_short':
        res = backtest_coin(df, data_signal)
    return res
