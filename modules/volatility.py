# import required modules
import numpy as np
import datetime
import pandas as pd
import os
import pickle
from functions.f_about_path import f_parent_path

def yang_zhang_volatility(data, n=2, clean=False):
    """
    :param data: a list with Open, High, Low, Close price
    :param n: the periods to obtain the average volatilitys
    :param clean: If clean, then delete the NA values
    :return: A list of volatility data
    """
    # define required variables
    o_c = (data['Open'] / data['Close'].shift(1)).apply(np.log)
    c_o = (data['Close'] / data['Open']).apply(np.log)
    h_o = (data['High'] / data['Open']).apply(np.log)
    l_o = (data['Low'] / data['Open']).apply(np.log)

    # overnight volatility
    vo = o_c.rolling(window=n).apply(np.var, raw=True)

    # today(open to close) volatility
    vt = c_o.rolling(window=n).apply(np.var, raw=True)

    # rogers-satchell volatility
    rs_fomula = h_o * (h_o - c_o) + l_o * (l_o - c_o)
    rs = rs_fomula.rolling(window=n, center=False).sum() * (1.0 / n)

    # super parameter
    k = 0.34 / (1 + (n + 1) / (n - 1))

    # yang-zhang
    result = (vo + k * vt + (1 - k) * rs).apply(np.sqrt)
    if clean:
        return result.dropna()
    else:
        return result

def daterange(date1, date2):
    """
    :param date1: start date
    :param date2: end date
    :return: a list of date
    """
    for n in range(int((date2 - date1).days) + 1):
        yield date1 + datetime.timedelta(n)

def date_format(date):
    list_date = date.split("-")
    year, month, day = list_date[0], list_date[1], list_date[2]
    return datetime.date(int(year), int(month), int(day))

class volatility:

    def __init__(self, end_dt):

        # The variables we need to launch this class
        self.end_dt = end_dt
        # Variable generated in price_data_to_volatility
        self.dict_volatility = None
        # Variable generated in periods_of_volatility
        self.dataframe = None

    # read the price data, set up dictionary and then calculate the volatility
    def price_data_to_volatility(self):

        # import the stock price data
        file_path = os.path.dirname(os.path.realpath(__file__))
        parent_path = f_parent_path(file_path, 1)
        save_path = parent_path + '/docs/' + 'modified_price_df.pickle'
        with open(save_path, 'rb') as f:
            dict_data = pickle.load(f)

        # calculate volatility
        dict_volatility = {}
        for data in dict_data:
            vol_name = data + '_vol'
            dict_volatility[vol_name] = yang_zhang_volatility(dict_data[data])

        self.dict_volatility = dict_volatility
        
        """
        for key, item in self.dict_volatility.items():
            with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                print(key)
                print(item)
        """

    # turn them into dataframe
    def dataframe_volatility(self):

        start = date_format("1900-01-01")
        end = date_format(self.end_dt)

        list_date = []

        for dt in daterange(start, end):
            list_date.append(dt.strftime("%Y-%m-%d"))

        # specify date here, create specified Date data
        dataframe_date = pd.DataFrame({'Date': list_date})
        dataframe_date.index = list_date

        # merge all the volatility
        dict_volatility = self.dict_volatility
        result = dataframe_date
        for volatility in dict_volatility:

            # interpolate
            vol_data = dict_volatility[volatility]
            vol_data = vol_data.interpolate()

            # turn series to frame
            vol_data = vol_data.to_frame()
            vol_data.columns = [volatility]
            # print(movement_data)
            result = result.merge(vol_data, left_index=True,
                                  right_index=True)
        # result = result.drop(columns=['Date'])

        # drop rows includes nan
        # result = result.dropna()

        self.dataframe = result
        # print(result)
