from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def main():
    APIKEY='I2LOWWTHAE4MVV3X'
    ts = TimeSeries(key=APIKEY, output_format='pandas')
    
    df = pd.DataFrame()
    companies = ['MSFT','AMZN','JNJ','XOM',
                 'JPM','WFC','WMT','BAC','PG','T','GE','ORCL','CVX',
                 'PFE','KO','VZ','CMCSA','UNH','C','HD','MRK','PEP']
    
    testcompanies = ['JPM']
    
    for c in testcompanies:
        df = pd.DataFrame()
        data = ts.get_weekly_adjusted('JPM')[0]
        series = data.close
        series = series.rename(c)
        df = pd.concat([df,series],axis=1)
        print("finished {}".format(c))
        
        weeksforward = 2 #these parameters adjustable
        weeksback = 6
        df = df[np.abs(df.values-df.values.mean()<=2*df.values.std())] #remove outliers
        
        pastdf = df.pct_change(weeksback).dropna()*100 # convert to % change
        futdf = df.pct_change(-weeksforward).dropna() # new df as shifted values
        
        futdf = futdf.drop(futdf.index[0:weeksback])
        pastdf = pastdf.drop(pastdf.index[pastdf.size-weeksforward:pastdf.size]) # drop 1st val so we have same indeces in df2 and 3
        
        plt.scatter(pastdf,futdf,s=1)
        #plot best fit line
        fit = np.polyfit(pastdf.values.flatten(),futdf.values.flatten(),deg=1) 
        intercept = fit[1]
        y0 = fit[0] * pastdf.min() + intercept
        y1 = fit[0] * pastdf.max() + intercept

        plt.plot([pastdf.min(),pastdf.max()],[y0,y1],color='r')
        print("slope: {}".format(fit[0]))
        
        df4 = pd.concat([pastdf,futdf],axis=1)
        df4.columns = ['wk1','wk2',]
        df4.index = df4['wk1']
        df4 = df4.drop(['wk1'],axis=1)
        
        low_slope,up_slope = bootstrap(df4,df4.size,400)
        print("Lower slope: {} \n Upper slope: {}".format(low_slope,up_slope))
        
        y0 = low_slope * pastdf.min() + intercept
        y1 = low_slope * pastdf.max() + intercept
        plt.plot([pastdf.min(),pastdf.max()],[y0,y1],alpha=0.5,color='g')
        y0 = up_slope * pastdf.min() + intercept
        y1 = up_slope * pastdf.max() + intercept
        plt.plot([pastdf.min(),pastdf.max()],[y0,y1],alpha=0.5,color='g')
        plt.title("-{} week % increase vs current week % increase for {}".format(pastdf.columns[0],weeksback))
        plt.show()
        
def bootstrap(bsdf,size,samples): # will need a combined dataframe
    fits=[]
    for i in range(0,samples):
        bsdf = bsdf.sample(size,replace=True)
        fit = np.polyfit(bsdf.index,bsdf.values.flatten(),deg=1)
        fits.append(fit[0])
    return np.percentile(fits,2.5),np.percentile(fits,97.5)
    
if __name__ =="__main__": 
    main()
