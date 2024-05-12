import os
import pickle
import functions.rolling_connectedness as f_roll
import time
import json
import functions.about_path as fap
# import pandas as pd


# count the time span, start
start_time = time.time()

# load variables
file_dir = os.path.dirname(os.path.abspath(__file__))
with open(file_dir + '/variables.json') as f:
    variables = json.load(f)
target_folder = variables["target_folder"]
predict_conns_periods = variables["predict_conns_periods"]
maximum_lag = variables["maximum_lag"]
periods_one_conn = variables["periods_one_conn"]
start_date = variables['start_date']
end_date = variables['end_date']


# the number of data
# simple version for working with CWD
file_path = os.path.dirname(os.path.realpath(__file__))
parent_path = fap.f_parent_path(file_path, 0)
save_path = parent_path + '/docs/' + target_folder
# print(save_path)
n_instruments = sum([len(files) for r, d, files in os.walk(save_path)])
# print(n_instruments)


# delete .DS_store
if os.path.isfile(save_path + '/.DS_Store'):
    os.remove(save_path + '/.DS_Store')


# load volatility_dataframe
file_path = os.path.dirname(os.path.realpath(__file__))
save_path = file_path + '/docs/' + 'volatility.pickle'
with open(save_path, 'rb') as f:
    volatility_dataframe = pickle.load(f)
# print(len(list(volatility_dataframe)))
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(volatility_dataframe)


# start the rolling connectedness
roll_conn = (f_roll.
             Rolling_Connectedness(volatility_dataframe,
                                   maximum_lag,
                                   periods_one_conn,
                                   predict_conns_periods))
roll_conn.divide_vol_dataframe()

file_path = os.path.dirname(os.path.realpath(__file__))
saving_folder = file_path + '/docs/'
# print(saving_folder)
roll_conn.calculate_rolling(start_dt, end_dt, saving_folder)

# count the time span, end
elapsed_time = time.time() - start_time
print("the time span in calculating rolling connectedness:", elapsed_time)
print("===================")
