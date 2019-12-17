import pandas as pd
import tushare as ts
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
import datetime
import os
sns.set()
mpl.rcParams['font.sans-serif'] = 'WenQuanYi Micro Hei'
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus'] = False
pro = ts.pro_api('f02bc8aa2c5c1ae3e5ce221b659802f61d75422c9cc6fe527cfbc6e1')
os.chdir(r'E:\FF3因子')
########################################################################################
#  下次运行前，先读取已经保存的数据，取出最后一条数据的时间，并将其下一天作为新的开始时间。 #
########################################################################################

def cal_smb_hml(df):
    # 划分大小市值公司
    df['SB'] = df['circ_mv'].map(lambda x: 'B' if x >= df['circ_mv'].median() else 'S')

    # 求账面市值比：PB的倒数
    df['BM'] = 1 / df['pb']
#    df['EP'] = 1 / df['pe_ttm']

    # 划分高、中、低账面市值比公司
    border_down, border_up = df['BM'].quantile([0.3, 0.7])
    df['HML'] = df['BM'].map(lambda x: 'H' if x >= border_up else 'M')
    df['HML'] = df.apply(lambda row: 'L' if row['BM'] <= border_down else row['HML'], axis=1)
    
    # 划分高、中、低公司市盈率公司
#    border_down, border_up = df['EP'].quantile([0.3, 0.7])
#    df['RMW'] = df['EP'].map(lambda x: 'R' if x >= border_up else 'M')
#    df['RMW'] = df.apply(lambda row: 'W' if row['EP'] <= border_down else row['RMW'], axis=1)  

    # 组合划分为6组
    df_SL = df.query('(SB=="S") & (HML=="L")')
    df_SM = df.query('(SB=="S") & (HML=="M")')
    df_SH = df.query('(SB=="S") & (HML=="H")')
    df_BL = df.query('(SB=="B") & (HML=="L")')
    df_BM = df.query('(SB=="B") & (HML=="M")')
    df_BH = df.query('(SB=="B") & (HML=="H")')

#    df_SW = df.query('(SB=="S") & (RMW=="W")')
#    df_SM1 = df.query('(SB=="S") & (RMW=="M")')
#    df_SR = df.query('(SB=="S") & (RMW=="R")')
#    df_BW = df.query('(SB=="B") & (RMW=="W")')
#    df_BM1 = df.query('(SB=="B") & (RMW=="M")')
#    df_BR = df.query('(SB=="B") & (RMW=="R")')
    # 计算各组收益率
    R_SL = (df_SL['pct_chg'] * df_SL['circ_mv'] / 100).sum() / df_SL['circ_mv'].sum()
    R_SM = (df_SM['pct_chg'] * df_SM['circ_mv'] / 100).sum() / df_SM['circ_mv'].sum()
    R_SH = (df_SH['pct_chg'] * df_SH['circ_mv'] / 100).sum() / df_SH['circ_mv'].sum()
    R_BL = (df_BL['pct_chg'] * df_BL['circ_mv'] / 100).sum() / df_BL['circ_mv'].sum()
    R_BM = (df_BM['pct_chg'] * df_BM['circ_mv'] / 100).sum() / df_BM['circ_mv'].sum()
    R_BH = (df_BH['pct_chg'] * df_BH['circ_mv'] / 100).sum() / df_BH['circ_mv'].sum()

#    R_SW = (df_SW['pct_chg'] * df_SW['circ_mv'] / 100).sum() / df_SW['circ_mv'].sum()
#    R_SM1 = (df_SM1['pct_chg'] * df_SM1['circ_mv'] / 100).sum() / df_SM1['circ_mv'].sum()
#    R_SR = (df_SR['pct_chg'] * df_SR['circ_mv'] / 100).sum() / df_SR['circ_mv'].sum()
#    R_BW = (df_BW['pct_chg'] * df_BW['circ_mv'] / 100).sum() / df_BW['circ_mv'].sum()
#    R_BM1 = (df_BM1['pct_chg'] * df_BM1['circ_mv'] / 100).sum() / df_BM1['circ_mv'].sum()
#    R_BR = (df_BR['pct_chg'] * df_BR['circ_mv'] / 100).sum() / df_BR['circ_mv'].sum()

    # 计算SMB, HML并返回
    smb = (R_SL + R_SM + R_SH - R_BL - R_BM - R_BH) / 3
    hml = (R_SH + R_BH - R_SL - R_BL) / 2
#    rmw = (R_SR + R_BR - R_SW - R_BW) / 2
    return smb, hml

# 输入时间
factor_data = pd.read_csv(r'E:\FF3因子\df_three_factors.csv')
factor_data = factor_data.set_index('trade_date')
factor_data.index = pd.to_datetime(factor_data.index)
print(factor_data.tail(1))

start_date = '20191031'# 格式：'20191217'
end_date = '20191217'

data = []
df_cal = pro.trade_cal(start_date=start_date, end_date=end_date) #交易日期
df_cal = df_cal.query('(exchange=="SSE") & (is_open==1)')
df_cal['month'] = df_cal['cal_date'].apply(lambda x:x[:6])
df_cal_1 = df_cal.drop_duplicates(subset='month',keep = 'last')
df_cal_1['change_stocks'] = 1
df_cal = pd.merge(df_cal,df_cal_1[['cal_date','change_stocks']],on='cal_date',how='left')

for i in range(1,df_cal.shape[0]):
    date = df_cal.cal_date[i]
    date_get_index = df_cal.iloc[:i,]
    date_get_index = date_get_index[date_get_index.change_stocks==1.0].tail(1).cal_date.to_list()[0]
    df_daily = pro.daily(trade_date=date)
    df_basic = pro.daily_basic(trade_date=date_get_index) # 使用上个月月末的财务指标
    df = pd.merge(df_basic[['ts_code','pb','circ_mv','total_mv']],df_daily[['ts_code','pct_chg']], on='ts_code', how='left')
    smb, hml = cal_smb_hml(df)
    data.append([date, smb, hml])
    print(date, smb, hml)


df_tfm = pd.DataFrame(data, columns=['trade_date', 'SMB', 'HML'])
df_tfm['trade_date'] = pd.to_datetime(df_tfm.trade_date)
df_tfm = df_tfm.set_index('trade_date')

# 计算完上面的数据后，与已有的数据合并
factor_data = factor_data.append(df_tfm)
factor_data = factor_data.reset_index()
factor_data = factor_data.drop_duplicates(subset='trade_date',keep='last')
factor_data = factor_data.set_index('trade_date')
factor_data.to_csv('df_three_factors.csv')

(factor_data+1).cumprod().plot(figsize=(20,10))
# 国泰安数据，结果合理
#test = pd.read_csv(r'three_four_five_factor_daily\fivefactor_daily.csv')
#test = test.set_index('trddy')
#test = test.iloc[2677:,]
#(test[['mkt_rf','smb','hml']]+1).cumprod().plot()
#(test[['hml','hml_equal']]+1).cumprod().plot()
#(-test[['rmw','rmw_equal']]+1).cumprod().plot()
#(-test[['cma','cma_equal']]+1).cumprod().plot()
#(test[['mkt_rf','smb','hml','rmw','cma']]+1).cumprod().plot(figsize=(20,10))
