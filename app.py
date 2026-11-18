import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title='Semáforo Bursátil', page_icon='🚦', layout='wide')
st.markdown('''<style>
@media (max-width: 700px) { .block-container {padding: 1rem .75rem 3rem !important;} .signal {font-size:26px !important;padding:18px 10px !important;} }
.stApp {background:#0b1220;color:#eaf0fb}div[data-testid="stMetric"]{background:#162235;border:1px solid #27364e;padding:17px;border-radius:14px}
.signal{border-radius:18px;padding:24px 30px;text-align:center;font-weight:800;font-size:35px;margin:10px 0 18px}
.green{background:#123e30;color:#5af0a1;border:2px solid #2bc77a}.red{background:#482128;color:#ff8891;border:2px solid #ea4d62}.yellow{background:#493c1a;color:#ffd76d;border:2px solid #e3ad35}
.small{font-size:14px;font-weight:400;margin-top:8px}
</style>''', unsafe_allow_html=True)

st.title('🚦 Semáforo bursátil')
st.caption('Señales técnicas objetivas • Datos históricos de Yahoo Finance • No ejecuta órdenes ni garantiza resultados')
# Selección de 100 grandes empresas negociadas en mercados estadounidenses.
# Lista de referencia fija (noviembre 2026), no ranking recalculado automáticamente.
TOP_100 = [
('AAPL','Apple'),('MSFT','Microsoft'),('NVDA','Nvidia'),('GOOGL','Alphabet (Google)'),
('AMZN','Amazon'),('TSM','Taiwan Semiconductor'),('META','Meta Platforms'),('AVGO','Broadcom'),
('TSLA','Tesla'),('LLY','Eli Lilly'),('BRK-B','Berkshire Hathaway'),('WMT','Walmart'),
('MU','Micron Technology'),('V','Visa'),('JPM','JPMorgan Chase'),('XOM','ExxonMobil'),
('JNJ','Johnson & Johnson'),('MA','Mastercard'),('NFLX','Netflix'),('COST','Costco'),
('PG','Procter & Gamble'),('HD','Home Depot'),('ABBV','AbbVie'),('ASML','ASML'),
('ORCL','Oracle'),('UNH','UnitedHealth'),('MRK','Merck'),('BAC','Bank of America'),
('GE','GE Aerospace'),('KO','Coca-Cola'),('AMD','AMD'),('CVX','Chevron'),
('PLTR','Palantir'),('TMUS','T-Mobile US'),('WFC','Wells Fargo'),('TM','Toyota'),
('SHEL','Shell'),('PM','Philip Morris'),('SAP','SAP'),('PANW','Palo Alto Networks'),
('RTX','RTX'),('CAT','Caterpillar'),('CSCO','Cisco'),('TMO','Thermo Fisher'),
('AMGN','Amgen'),('IBM','IBM'),('ACN','Accenture'),('MS','Morgan Stanley'),
('AZN','AstraZeneca'),('NVS','Novartis'),('LIN','Linde'),('BABA','Alibaba'),
('AXP','American Express'),('GILD','Gilead Sciences'),('DIS','Disney'),('PEP','PepsiCo'),
('MCD',"McDonald's"),('ISRG','Intuitive Surgical'),('GS','Goldman Sachs'),('ABT','Abbott'),
('ARM','Arm Holdings'),('T','AT&T'),('NVO','Novo Nordisk'),('QCOM','Qualcomm'),
('BX','Blackstone'),('DHR','Danaher'),('HSBC','HSBC'),('CRM','Salesforce'),
('TXN','Texas Instruments'),('VZ','Verizon'),('BKNG','Booking Holdings'),('COP','ConocoPhillips'),
('PFE','Pfizer'),('SPGI','S&P Global'),('HDB','HDFC Bank'),('AMAT','Applied Materials'),
('BLK','BlackRock'),('C','Citigroup'),('BSX','Boston Scientific'),('RY','Royal Bank of Canada'),
('NEE','NextEra Energy'),('UBS','UBS Group'),('UBER','Uber'),('ANET','Arista Networks'),
('SCHW','Charles Schwab'),('TJX','TJX Companies'),('PGR','Progressive'),('SHOP','Shopify'),
('UL','Unilever'),('BHP','BHP'),('APP','AppLovin'),('VRTX','Vertex'),
('LMT','Lockheed Martin'),('MRVL','Marvell Technology'),('ETN','Eaton'),('KKR','KKR'),
('BA','Boeing'),('SYK','Stryker'),('UNP','Union Pacific'),('TTE','TotalEnergies')]
assert len(TOP_100)==100 and len({ticker for ticker,_ in TOP_100})==100
EXTRAS=[('MELI','MercadoLibre'),('YPF','YPF ADR'),('GGAL','Grupo Galicia ADR'),
('BMA','Banco Macro ADR'),('PAM','Pampa Energía ADR'),('SPY','ETF S&P 500'),
('QQQ','ETF Nasdaq 100'),('BTC-USD','Bitcoin'),('ETH-USD','Ethereum')]
LOOKUP={f'{name} · {symbol}':symbol for symbol,name in TOP_100}
EXTRA_LOOKUP={f'{name} · {symbol}':symbol for symbol,name in EXTRAS}

st.markdown('### Elegí el activo que querés analizar')
mode=st.segmented_control('Universo', ['Top 100','Argentina / ETF / Crypto','Otro ticker'],default='Top 100', key='asset_type')
if mode == 'Top 100':
    selected=st.selectbox('Buscar por empresa o símbolo',sorted(LOOKUP),index=sorted(LOOKUP).index('Nvidia · NVDA'),key='big_stock')
    ticker=LOOKUP[selected]
elif mode == 'Argentina / ETF / Crypto':
    selected=st.selectbox('Elegí un activo',list(EXTRA_LOOKUP),key='extras')
    ticker=EXTRA_LOOKUP[selected]
else:
    ticker=st.text_input('Escribí un ticker, por ejemplo KO, GGAL.BA o MELI',value='MELI',max_chars=24).strip().upper()

col_h,col_p=st.columns([2,2])
with col_h:
    horizon=st.selectbox('Horizonte', ['1–7 días','2–6 semanas','2–6 meses'])
with col_p:
    holding=st.selectbox('Tu situación', ['No, estoy evaluando comprar','Sí, estoy evaluando vender'])
refresh=st.button('↻ Actualizar cotización y análisis',use_container_width=True)
st.caption('Las 100 acciones son una selección de grandes empresas listadas en EE. UU. (referencia de noviembre 2026). No se recalcula diariamente el ranking. También podés buscar cualquier ticker.')
if not ticker or not all(c.isalnum() or c in '.-^=' for c in ticker):
    st.warning('Ingresá un símbolo bursátil válido.')
    st.stop()

@st.cache_data(ttl=300, show_spinner=False)
def get_data(symbol):
    return yf.Ticker(symbol).history(period='2y', interval='1d', auto_adjust=True)

if refresh:
    get_data.clear()

try:
    df=get_data(ticker)
except Exception as e:
    st.error('No fue posible descargar la cotización. Revisá el símbolo o la conexión.')
    st.stop()

if df is None or df.empty or len(df)<220:
    st.warning('No hay suficientes datos para analizar este activo (se requieren al menos 220 sesiones). Probá otro ticker.')
    st.stop()

df=df.dropna(subset=['Close']).copy()
close=df['Close'].astype(float)
df['EMA20']=close.ewm(span=20,adjust=False).mean()
df['EMA50']=close.ewm(span=50,adjust=False).mean()
df['SMA200']=close.rolling(200).mean()
delta=close.diff(); gains=delta.clip(lower=0); losses=(-delta).clip(lower=0)
avg_gain=gains.ewm(alpha=1/14,adjust=False,min_periods=14).mean()
avg_loss=losses.ewm(alpha=1/14,adjust=False,min_periods=14).mean()
rs=avg_gain/avg_loss.replace(0,np.nan)
df['RSI']=100-(100/(1+rs))
ema12=close.ewm(span=12,adjust=False).mean(); ema26=close.ewm(span=26,adjust=False).mean()
df['MACD']=ema12-ema26;df['MACD_SIGNAL']=df['MACD'].ewm(span=9,adjust=False).mean()
prev_close=close.shift()
tr=pd.concat([(df['High']-df['Low']).abs(),(df['High']-prev_close).abs(),(df['Low']-prev_close).abs()],axis=1).max(axis=1)
df['ATR14']=tr.ewm(alpha=1/14,adjust=False,min_periods=14).mean()
latest=df.iloc[-1]; price=float(latest['Close']); rsi=float(latest['RSI']); atr=float(latest['ATR14'])
# Cada señal aporta +/- 1. Score no es probabilidad.
conditions=[('Precio vs. EMA 20',price>latest['EMA20']),('EMA 20 vs. EMA 50',latest['EMA20']>latest['EMA50']),('Precio vs. SMA 200',price>latest['SMA200']),('MACD vs. señal',latest['MACD']>latest['MACD_SIGNAL']),('RSI sobre 50',rsi>50)]
score=sum(1 if ok else -1 for _,ok in conditions)
# RSI extremo introduce cautela adicional: no recomienda comprar sobrecomprado ni vender sobrevendido.
if score>=3 and rsi<70:
    signal='COMPRAR';class_name='green';reason='Predominan las señales alcistas sin sobrecompra extrema.'
elif score<=-3 and rsi>30:
    signal='VENDER';class_name='red';reason='Predominan las señales bajistas sin sobreventa extrema.'
else:
    signal='ESPERAR';class_name='yellow';reason='Los indicadores se contradicen o el RSI sugiere cautela.'

# Niveles orientativos ATR, adecuados como referencias, no stop/targets optimizados.
atr_mult={'1–7 días':(1.5,2.5),'2–6 semanas':(2.0,3.5),'2–6 meses':(3.0,5.0)}
stop_mul,target_mul=atr_mult[horizon]
stop=max(0,price-atr*stop_mul); target=price+atr*target_mul
risk_pct=(price-stop)/price*100;gain_pct=(target-price)/price*100
last_date=df.index[-1].strftime('%d/%m/%Y')
from datetime import datetime, timezone
last_age_days=(datetime.now(timezone.utc).date()-df.index[-1].date()).days
if last_age_days>7:
    st.warning(f'El último dato disponible tiene {last_age_days} días de antigüedad; verificá la cotización antes de operar.')
chg=(close.iloc[-1]/close.iloc[-2]-1)*100
st.markdown(f'<div class="signal {class_name}">● {signal}<div class="small">{reason}</div></div>',unsafe_allow_html=True)
st.caption(f'{ticker} · Última sesión: {last_date} · Datos de cierre (no necesariamente en tiempo real) · Horizonte: {horizon}')
c1,c2=st.columns(2)
c3,c4=st.columns(2)
c1.metric('Último cierre',f'{price:,.2f}',f'{chg:+.2f}% sesión')
c2.metric('RSI (14)',f'{rsi:.1f}')
c3.metric('Puntuación técnica',f'{score:+d} / 5')
c4.metric('Volatilidad ATR (14)',f'{atr:,.2f}')

st.subheader('Lectura del semáforo')
st.write('La puntuación suma +1 por cada indicador alcista y −1 por cada indicador bajista. Comprar requiere +3 o más y RSI < 70; vender requiere −3 o menos y RSI > 30. En otro caso, esperar. **No es una probabilidad de éxito ni una recomendación personalizada.**')
for label,yes in conditions:
    a,b=st.columns([3,1])
    a.write(label)
    b.markdown('🟢 Alcista' if yes else '🔴 Bajista')

st.subheader('Precio e indicadores')
visible={'1–7 días':70,'2–6 semanas':130,'2–6 meses':240}[horizon]
view=df.tail(visible)
fig=make_subplots(rows=2,cols=1,shared_xaxes=True,vertical_spacing=.07,row_heights=[.75,.25])
fig.add_trace(go.Scatter(x=view.index,y=view['Close'],name='Precio',line=dict(color='#f4f6fb',width=2)),row=1,col=1)
fig.add_trace(go.Scatter(x=view.index,y=view['EMA20'],name='EMA20',line=dict(color='#42d99c',width=1.5)),row=1,col=1)
fig.add_trace(go.Scatter(x=view.index,y=view['EMA50'],name='EMA50',line=dict(color='#e8b557',width=1.5)),row=1,col=1)
fig.add_trace(go.Scatter(x=view.index,y=view['SMA200'],name='SMA200',line=dict(color='#a38bec',width=1.5)),row=1,col=1)
fig.add_trace(go.Scatter(x=view.index,y=view['RSI'],name='RSI14',line=dict(color='#50bff8',width=1.8)),row=2,col=1)
fig.add_hline(y=70,line_dash='dash',line_color='#e66b76',row=2,col=1)
fig.add_hline(y=30,line_dash='dash',line_color='#42d99c',row=2,col=1)
fig.update_layout(height=490,template='plotly_dark',paper_bgcolor='#0b1220',plot_bgcolor='#101b2c',margin=dict(l=10,r=10,t=20,b=10),legend=dict(orientation='h',y=1.08))
fig.update_yaxes(title_text='Precio',row=1,col=1)
fig.update_yaxes(title_text='RSI',row=2,col=1,range=[0,100])
st.plotly_chart(fig,use_container_width=True)

st.subheader('Niveles orientativos (basados en volatilidad)')
x,y=st.columns(2)
z=st.container()
x.metric('Referencia actual',f'{price:,.2f}')
y.metric('Protección ilustrativa',f'{stop:,.2f}',f'-{risk_pct:.1f}%')
z.metric('Objetivo ilustrativo',f'{target:,.2f}',f'+{gain_pct:.1f}%')
st.caption('Stop = cierre − múltiplo de ATR; objetivo = cierre + múltiplo de ATR. Son referencias mecánicas orientadas a una posición larga, no soportes/resistencias reales ni precios de ejecución. No consideran noticias, spreads, comisiones ni deslizamiento.')
if holding.startswith('Sí'):
    st.info('Si ya estás invertido, una señal VENDER indica deterioro técnico, pero no reemplaza tu análisis de precio de entrada, impuestos, horizonte y tamaño de posición. Una señal COMPRAR no obliga a incrementar la posición.')
else:
    st.info('Si todavía no compraste, una señal VENDER significa evitar nuevas compras según estas reglas; no implica vender en corto.')
st.divider()
st.caption('Fuente: Yahoo Finance a través de yfinance; datos de cierre, no tiempo real. Uso educativo/informativo, no asesoramiento personalizado. La clasificación es mecánica y puede fallar, sobre todo ante noticias o brechas de mercado.')
