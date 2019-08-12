import pandas as pd
import numpy as np
import statsmodels.api as sm
#NAN,inf处理函数
def deal_nan(df,factors,method):
    df_=df.copy()
    df_.iloc[np.where(np.isinf(df_))]=np.nan
    if method=="0":#用0补充
        df_=df_.fillna(0)
    if method=="mean":#截面均值补充
        variables=factors
        for variable in variables:
            df_[df_[variable].isna()]=df_[variable].mean()   
    return df_
#去极值
def winsorize(df,factors,limit=3):
    df_=df.copy()
    variables=factors
    for variable in variables:
        mean=df_[variable].mean()
        std=df_[variable].std()
        df_[variable][df[variable]<(mean-std*limit)]=mean-std*limit
        df_[variable][df[variable]>(mean+std*limit)]=mean+std*limit
    return df_
#标准化
def normalize(df,factors):
    df_=df.copy()
    variables=factors
    for variable in variables:
        df_[variable]=(df_[variable]-df_[variable].mean())/df_[variable].std()
    return df_
#对称正交
def symmetric_orthog(df,factors):
    A=df.copy()
    A=A.loc[:,factors]
    A=A.dropna(axis=0,how="all")
    A = A.dropna(axis=1, how="all")
    A=A.values
    A[np.isnan(A)]=0
    A=np.mat(A)
    T=np.shape(A)[0]
    M = (T - 1) * np.cov(A.T)  # 获得重叠矩阵
    M = np.mat(M)
    u, v = np.linalg.eig(M)  # u是特征值，v是特征向量
    sk1 = np.dot(np.dot(v, np.linalg.inv(np.diag(u ** 0.5))), v.T)
    F = np.dot(A, sk1)
    df.loc[:,factors]=np.array(F)
    return df
#市值中性化：采用流通市值，保证市值列名为“market_cap”
def market_cap_normalize(df,factors):
    df_=df.copy()
    variables=factors
    for variable in variables:
        mean=df_[variable]*df_["market_cap"]/df_["market_cap"].sum()
        df_[variable]=(df_[variable]-mean)/df_[variable].std()
    return df_
#行业、市值中性化：多出两列，流通市值(market_cap)和行业名称或代码(industry)
def industry_neutrilize(df,factors):
    #行业哑变量
    df_=df.copy()
    industry_list=list(set(df_["industry"]))
    for i in industry_list:
        df_[i]=0
        df_.loc[df_["industry"]==i,i]=1
    industry_list.extend(["market_cap"])
    for factor in factors:
        mod = sm.OLS(df_[factor], df_[list(set(industry_list))])
        res = mod.fit()
        df_[factor]=res.resid
    return df_
