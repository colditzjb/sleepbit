import fitbit
from datetime import datetime as dt
import pandas as pd

authd_client = fitbit.Fitbit(OAuthTwoClientID, ClientOrConsumerSecret, oauth2=True,
                             access_token=AccessToken, refresh_token=RefreshToken)
sleepdata = authd_client.sleep()

di = 0 #day identifier: index in the 'sleep' list
minutes = sleepdata['sleep'][di]['minuteData']

start = {}
start['dt'] = dt.strptime(sleepdata['sleep'][di]['startTime'], '%Y-%m-%dT%H:%M:%S.000')
start['Y'] = int(dt.strftime(start['dt'], '%Y'))
start['m'] = int(dt.strftime(start['dt'], '%m'))
start['d'] = int(dt.strftime(start['dt'], '%d'))

def correct_dt(t_str, start=start):
  newdt = dt.strptime(t_str, '%H:%M:%S').replace(year=start['Y'], month=start['m'] , day=start['d'])
  if newdt < start['dt']:
    newdt = newdt.replace(day=start['d']+1)
  else: pass
  return newdt

dfdata = []
for m in minutes:
  dfdata.append([correct_dt(m['dateTime']),m['value']])

df=pd.DataFrame(dfdata, columns=['dateTime','value'])

df['dateTime'] =  pd.to_datetime(df['dateTime'], unit='M')
df = df.set_index(['dateTime'])
df['value'] = df['value'].convert_objects(convert_numeric=True)

# Preliminary approach for smoothing data
smoothed = df.resample('15min', how='mean')
smoothed = smoothed.resample('1min', how='mean').interpolate(method='cubic')
smoothed = smoothed.resample('15min', how='mean')
smoothed = smoothed.resample('1min', how='mean').interpolate(method='cubic')
smoothed = pd.rolling_mean(smoothed, 45, min_periods=1)
smoothed.plot()

frames = [df, smoothed]
joined = pd.concat(frames, axis=1)
joined.columns = ['raw', 'smooth']
joined.plot()
