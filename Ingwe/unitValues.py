import pandas as pd
import numpy as np

transactions = pd.read_csv('all_transactions.csv', index_col='date', parse_dates=True)
performance = pd.read_csv('daily_performance.csv', index_col='Date', parse_dates=True)

ts_df = transactions[['typeid', 'value', 'symbol']]
ts_df = ts_df.sort_index()
ts_df = ts_df.rename_axis('Date')

current_balance = 0
def sum_cash(a, b):
    global current_balance
    if a == 'buylong' or a == 'quarterlymanagementfee':
        current_balance = current_balance - b
    else:
        current_balance = current_balance + b
    return current_balance

ts_df = ts_df.assign(Cash_balance = ts_df.apply(lambda x: sum_cash(a = x['typeid'], b = x['value']), axis=1))
df_cash_balance = ts_df[['Cash_balance']]

df = df_cash_balance.groupby(df_cash_balance.index).tail(1)

df1 = performance.join(df, how='outer')

running_balance = 0
def calculate_running_balance(a):
    global running_balance
    if pd.notna(a):
        running_balance = a
        return a
    else:
        return running_balance

performance_cols = ['Total_cost', 'Total_profit', 'Performance']
for col in performance_cols:
    df1[col] = df1[col].map(calculate_running_balance)
    running_balance = 0

def calculate_unit_value(a, b):
    profit = 0
    if pd.notna(a):
        profit = a
    percentage = profit / b
    return np.round_(1 + percentage, decimals=4)

df1 = df1.assign(Running_balance = df1['Cash_balance'].map(calculate_running_balance))
df1 = df1.assign(Net_asset_value = df1['Total_cost'].fillna(0) + df1['Total_profit'].fillna(0) + df1['Running_balance'])
df1 = df1.assign(Unit_value = df1.apply(lambda x: calculate_unit_value(a = x['Total_profit'], b = x['Net_asset_value']), axis=1))
df1 = df1.assign(Unit_val_change = df1['Unit_value'].map(lambda x: np.round_(((x - 1) / 1) * 100, decimals=2)))

week_day_col_values = df1.index.weekday_name
df1.insert(loc=0, column='Weekday', value=week_day_col_values)
print(df1.head(10)) #PRINT------------PRINT--------------PRINT#
print(df1.tail(10)) #PRINT------------PRINT--------------PRINT#
print(df1.info()) #PRINT------------PRINT--------------PRINT#
df1.to_csv('daily_unit_value.csv', encoding='utf-8')

print(df1['Performance'].describe())
maxpf_daily = df1['Performance'].idxmax()
print(df1.loc[maxpf_daily])

df_weeks = df1.loc[df1['Weekday'] == "Friday"]
print(df_weeks.head(10)) #PRINT------------PRINT--------------PRINT#
print(df_weeks.tail(10)) #PRINT------------PRINT--------------PRINT#
print(df_weeks.info()) #PRINT------------PRINT--------------PRINT#
df_weeks.to_csv('weekly_unit_value.csv', encoding='utf-8')

print(df_weeks['Performance'].describe())
maxpf_weekly = df_weeks['Performance'].idxmax()
print(df_weeks.loc[maxpf_weekly])