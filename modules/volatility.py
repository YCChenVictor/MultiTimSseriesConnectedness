# import modules
import functions.f_volatility as f_vol
import os
import pickle
import time
import json

# count the time span, start
start_time = time.time()

# load Prerequisite
file_dir = os.path.dirname(os.path.abspath(__file__))
with open(file_dir + '/docs' + '/Prerequisite.json') as f:
    prerequisite = json.load(f)
# print(prerequisite)

# obtain start_date, end_date
end_dt = prerequisite['end_dt']

# calculate volatility dataframe
volatility = f_vol.volatility(end_dt)
volatility.price_data_to_volatility()
volatility.dataframe_volatility()
volatility_dataframe = volatility.dataframe
print(volatility_dataframe)
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(volatility_dataframe)

# save the volatility_dataframe into pickle
file_path = os.path.dirname(os.path.realpath(__file__))
save_path = file_path + '/docs/' + 'volatility.pickle'
with open(save_path, 'wb') as f:
    pickle.dump(volatility_dataframe, f)

# count the time span, end
elapsed_time = time.time() - start_time
print("the time span in calculating volatility:", elapsed_time)
print("===================")
