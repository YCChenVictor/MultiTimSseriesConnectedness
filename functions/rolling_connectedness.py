# import the required module
import functions.f_connectedness as f_conn
import functions.f_coef as f_coef
from functions.f_date import add_date, date_format, daterange, minus_date
import pandas as pd
import numpy as np
import pickle


# functions to make batches of rolling connectedness
def roll_conn_elements(df, periods):
    # slice this timeseries df
    roll_dict = {}

    # iteratively divide dataframe
    for i in range(len(df)):
        # print(i)

        # get divided data
        data = df.iloc[i: periods+i, :]
        # rint(data)
        if len(data) < periods:
            break

        # get the end date
        rowname = list(data.index)
        end_dt = rowname[-1]
        # print(end_dt)

        # reset the index
        data = data.reset_index(drop=True)
        # print(data)

        # turn into array (matrix)
        data = data.values
        data = np.asarray(data, np.float32)
        # print(data)

        # add to data_dict
        roll_dict[end_dt] = data

    return roll_dict


class Rolling_Connectedness:

    def __init__(self, vol_df, max_lag, periods_one_conn, predict_period):

        # variables to run this module
        self.vol_df = vol_df  # the volatility dataframe to calculate connectedness
        self.name = list(vol_df)
        self.max_lag = max_lag
        self.periods_one_conn = periods_one_conn
        self.predict_period = predict_period  # the 'future-period' connectedness predicted by the data

        # save the calculated connectedness
        self.vol_dict = None
        self.roll_conn_dict = None
        self.accuracy_list = None
        self.df = None

    def divide_vol_dataframe(self):

        # required variables
        dataframe = self.vol_df
        periods = self.periods_one_conn

        # dict to save the data
        vol_dict = {}

        # iteratively divide dataframe
        for i in range(len(dataframe)):

            # get divided data
            data = dataframe.iloc[i: periods+i, :]
            if len(data) < periods:
                break

            # reset the index and get the end date
            data = data.reset_index(drop=True)
            end_dt = data["Date"].iloc[-1]
            # print(end_dt)

            # add to data_dict
            vol_dict[end_dt] = data

        self.vol_dict = vol_dict

    def calculate_rolling(self, start_dt, end_dt, saving_folder):

        """
        The start_dt and end_dt are the dates to calculate the predicted
        connectedness.

        Because we are going to predict the connectedness forward with
        'predict_period' periods, the start_dt and end_dt of vol_df should
        minus 'predict_period' days.

        The start_dt and end_dt here are the dates to select vol_df
        """

        vol_dict = self.vol_dict
        max_lag = self.max_lag
        periods = self.periods_one_conn
        predict_period = self.predict_period
        name = self.name
        vol_dict = self.vol_dict
        name.remove("Date")
        name.append("all")

        # print(vol_dict)

        # the target dates
        start_dt = date_format(start_dt)
        end_dt = date_format(end_dt)
        date_range = daterange(start_dt, end_dt)
        dates_list = list(date_range)

        # convert the elements of dates_list into string
        dates_list_str = []
        for date in dates_list:
            date = date.strftime('%Y-%m-%d')
            dates_list_str.append(date)
        # print(dates_list_str)

        # the dict specifies target dates
        vol_dict = {date: vol_dict[date] for date in dates_list_str}

        # start to calculate rolling
        roll_conn_dict = {}
        roll_conn_dict_flat = {}

        for key, data in vol_dict.items():
            # print(data)

            # get start and end date
            start_date = data["Date"][0]
            end_date = data["Date"][periods-1]
            period = start_date + " ~ " + end_date

            print("calculating rolling, period: %s" % period)

            # coef and sigma_hat ####
            coef = f_coef.Coef(data, max_lag)
            coef.f_ols_coef()
            ols_coef = coef.OLS_coef
            ols_sigma = coef.OLS_sigma

            # accuracy
            # accuracy = coef.accuracy

            # connectedness
            conn = f_conn.Connectedness(ols_coef, ols_sigma)
            conn.f_full_connectedness(h=predict_period)
            conn.rename_table(name)
            conn.table_restructure()

            # name the rowname
            result = conn.flat_connectedness

            # the key name is the end date + 1 day
            end_date_1 = add_date(end_date, 1)
            end_date_1 = end_date_1.strftime('%Y-%m-%d')

            # append all the flat_connectedness
            roll_conn_dict[end_date_1] = conn.full_connectedness
            roll_conn_dict_flat[end_date_1] = result

            # save the dict into this class
            self.roll_conn_dict = roll_conn_dict
            self.roll_conn_dict_flat = roll_conn_dict_flat

            save_path_flat = saving_folder + 'roll_conn_flat.pickle'
            save_path = saving_folder + 'roll_conn.pickle'

            # print(save_path_flat)
            # print(save_path)

            with open(save_path_flat, 'wb') as f:
                pickle.dump(roll_conn_dict_flat, f)

            with open(save_path, 'wb') as f:
                pickle.dump(roll_conn_dict, f)

    def add_connectedness_and_df(self, start_dt, end_dt, saving_folder):

        """
        The start_dt and end_dt are the last date + 1 day in the vol_dataframe
        which is the date in roll_conn_dict
        """

        vol_dict = self.vol_dict
        max_lag = self.max_lag
        periods = self.periods_one_conn
        predict_period = self.predict_period
        name = self.name
        vol_dict = self.vol_dict
        name.remove("Date")
        name.append("all")

        # the target dates
        start_dt = minus_date(start_dt, predict_period)
        end_dt = minus_date(end_dt, predict_period)
        date_range = daterange(start_dt, end_dt)
        dates_list = list(date_range)
        # print(dates_list)

        # convert the elements of dates_list into string
        dates_list_add = []
        for date in dates_list:
            date = date.strftime('%Y-%m-%d')
            dates_list_add.append(date)

        # get the calculated connectedness path
        save_path_flat = saving_folder + 'roll_conn_flat.pickle'
        save_path = saving_folder + 'roll_conn.pickle'

        # print(save_path_flat)
        # print(save_path)

        # load the calculated connectedness
        with open(save_path_flat, 'rb') as f:
            roll_conn_dict_flat = pickle.load(f)

        with open(save_path, 'rb') as f:
            roll_conn_dict = pickle.load(f)

        # get the dates already calculated connectedness
        dates_list_origin = list(roll_conn_dict.keys())
        # print(dates_list_origin)

        # get the dates going tp add connectedness
        dates_list_add = [date for date in dates_list_add if date not in
                          dates_list_origin]
        # print(dates_list_add)

        # calculate connectedness
        for date in dates_list_add:

            # date - 1
            date = minus_date(date, 1)
            date = date.strftime('%Y-%m-%d')

            # specify the target volatility dataframe
            target = vol_dict[date]
            # print(target)

            # get start and end date
            start_date = target["Date"][0]
            end_date = target["Date"][periods-1]
            period = start_date + " ~ " + end_date

            print("calculating rolling, period: %s" % period)

            # remove Date column
            # target.drop(["Date"], axis=1, inplace=True)

            # coef and sigma_hat ####
            coef = f_coef.Coef(target, max_lag)
            coef.f_ols_coef()
            ols_coef = coef.OLS_coef
            # print(ols_coef)
            ols_sigma = coef.OLS_sigma

            # accuracy
            # accuracy = coef.accuracy

            # connectedness
            conn = f_conn.Connectedness(ols_coef, ols_sigma)
            conn.f_full_connectedness(h=predict_period)
            conn.rename_table(name)
            conn.table_restructure()

            # name the rowname
            result = conn.flat_connectedness

            # the key name is the end date + 1 day
            end_date_1 = add_date(end_date, 1)
            end_date_1 = end_date_1.strftime('%Y-%m-%d')

            # append all the flat_connectedness
            roll_conn_dict[end_date_1] = conn.full_connectedness
            roll_conn_dict_flat[end_date_1] = result

            # save the dict into this class
            self.roll_conn_dict = roll_conn_dict
            self.roll_conn_dict_flat = roll_conn_dict_flat

            save_path_flat = saving_folder + 'roll_conn_flat.pickle'
            save_path = saving_folder + 'roll_conn.pickle'

            # print(save_path_flat)
            # print(save_path)

            with open(save_path_flat, 'wb') as f:
                pickle.dump(roll_conn_dict_flat, f)

            with open(save_path, 'wb') as f:
                pickle.dump(roll_conn_dict, f)

    def turn_into_df(self):
        """
        suppose the connectedness added is later than the calculated
        connectedness
        """
        roll_conn_dict = self.roll_conn_dict

        # turn dict into df
        result = pd.concat(roll_conn_dict)
        result = result.reset_index().set_index('level_0').drop(['level_1'], axis=1)

        self.df = result

    def plot_rolling():
        pass
