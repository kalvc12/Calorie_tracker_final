import streamlit as st
import requests, pandas as pd, datetime, os

st.set_page_config('Calorie Tracker', '🍏')
LOG='food_log.csv'
def search(q):
  resp=requests.get('https://world.openfoodfacts.org/cgi/search.pl',
    params={'search_terms':q,'search_simple':1,'action':'process','json':1,'page_size':1})
  if resp.ok and resp.json().get('products'): return resp.json()['products'][0]
def nutrients(p):
  n=p.get('nutriments',{})
  return {
    'kcal':n.get('energy-kcal_100g'),
    'protein':n.get('proteins_100g'),
    'carbs':n.get('carbohydrates_100g'),
    'fat':n.get('fat_100g')
  }
def load():return pd.read_csv(LOG,parse_dates=['date']) if os.path.exists(LOG) else pd.DataFrame(columns=['date','food','g','kcal','protein','carbs','fat'])
# UI
st.title('🍏 Calorie Tracker')
q=st.text_input('Food name')
g=st.number_input('Amount (g)',100.0,step=10.0)
if st.button('Add') and q:
  p=search(q)
  if not p: st.error('Not found'); st.stop()
  n=nutrients(p)
  if not n['kcal']: st.error('Missing data'); st.stop()
  amt=g/100
  df=load()
  df=df.append({
    'date':datetime.date.today(), 'food':p.get('product_name',q),'g':g,
    'kcal':n['kcal']*amt,'protein':n['protein']*amt,'carbs':n['carbs']*amt,'fat':n['fat']*amt
  },ignore_index=True)
  df.to_csv(LOG,index=False)
  st.success('Added')
df=load()
today=df[df.date==pd.Timestamp(datetime.date.today())]
if not today.empty:
  st.table(today[['food','g','kcal','protein','carbs','fat']])
  st.write('Totals:', today[['kcal','protein','carbs','fat']].sum().to_dict())
else:
  st.write('Nothing logged today.')
