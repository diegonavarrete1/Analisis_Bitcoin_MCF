import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from scipy.stats import norm
from scipy.stats import t

# Configuración de la página
st.set_page_config(
    page_title="Risk Dashboard",
    page_icon="📉",
    layout="wide"
)
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1611078489935-0cb964de46d6");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* 🔥 overlay bien oscuro (esto garantiza negro sí o sí) */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.9); /* casi negro total */
        z-index: -1;
    }

    h1, h2, h3, h4, h5, h6, p, div, span {
        color: #f0f0f0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
@st.cache_data
def get_data():
    ticker = "BTC-USD"
    data = yf.download(ticker, start="2010-01-01")

    if 'Adj Close' in data.columns:
        data['Returns'] = data['Adj Close'].pct_change()
    else:
        data['Returns'] = data['Close'].pct_change()

    data = data.dropna()

    return data

data = get_data()


st.title("📉 Análisis de Riesgo Financiero")
st.write("Estimación de Value at Risk (VaR) y Expected Shortfall (ES)")

st.header("Datos históricos", divider="gray")
st.write(data.head())

# Rendimientos

st.header("Rendimientos diarios", divider="gray")

st.line_chart(data['Returns'])



st.header("Estadísticas", divider="gray")
#INCISO B
media = data['Returns'].mean()
sesgo = data['Returns'].skew()
curtosis = data['Returns'].kurt()

col1, col2, col3 = st.columns(3)

col1.metric("Media", f"{media:.6f}")
col2.metric("Sesgo", f"{sesgo:.4f}")
col3.metric("Curtosis", f"{curtosis:.4f}")
#INCISO C
st.header("VaR y Expected Shortfall", divider= 'red')
alpha = [0.95, 0.975, 0.99]

def var_es_normal(returns, alpha):
    mean = returns.mean()
    std = returns.std()

    z = norm.ppf(1 - alpha)

    VaR = mean + z * std
    ES = mean - std * (norm.pdf(z) / (1 - alpha))

    return VaR, ES

from scipy.stats import t as student_t

from scipy.stats import t as student_t

from scipy.stats import t as student_t

def var_es_t(returns, alpha):
    returns = pd.Series(returns)

    # 🧹 limpieza completa
    returns = returns.replace([np.inf, -np.inf], np.nan)
    returns = returns.dropna()

    # 🔒 asegurar tipo numérico
    returns = pd.to_numeric(returns, errors='coerce').dropna()

    # 🔥 evitar casos degenerados
    if len(returns) < 20:
        return np.nan, np.nan

    if returns.std() == 0:
        return np.nan, np.nan

    data = returns.values

    try:
        df, loc, scale = student_t.fit(data)

        # evitar df problemático
        if df <= 2:
            return np.nan, np.nan

        x = student_t.ppf(1 - alpha, df)

        VaR = loc + scale * x

        ES = loc - scale * (
            (student_t.pdf(x, df) / (1 - alpha)) * (df + x**2) / (df - 1)
        )

        return VaR, ES

    except Exception as e:
        return np.nan, np.nan

    return VaR, ES
def var_es_hist(returns, alpha):
    sorted_returns = pd.Series(returns).dropna().sort_values()

    n = len(sorted_returns)

    if n < 10:
        return np.nan, np.nan

    index = int((1 - alpha) * n)

    # 🔒 CLAMP del índice
    index = max(1, min(index, n - 1))

    VaR = sorted_returns.iloc[index]

    ES = sorted_returns.iloc[:index].mean()

    return VaR, ES
def var_es_mc(returns, alpha, n_sim=10000):
    media = returns.mean()
    dev = returns.std()

   
    sim = np.random.normal(media, dev, n_sim)

    # VaR
    VaR = np.percentile(sim, (1 - alpha) * 100)

    # ES
    ES = sim[sim <= VaR].mean() #Seleccionamos solo los que son menores a VaR

    return VaR, ES

returns = data['Returns']

# DataFrame donde guardarás resultados
rolling_results = pd.DataFrame(index=returns.index) #Necesitamos indice de tiempo

# Inicializar columnas
rolling_results['Returns'] = returns
rolling_results['VaR_95_hist'] = np.nan
rolling_results['ES_95_hist'] = np.nan
rolling_results['VaR_99_hist'] = np.nan
rolling_results['ES_99_hist'] = np.nan
rolling_results['VaR_95_norm'] = np.nan
rolling_results['ES_95_norm'] = np.nan
rolling_results['VaR_99_norm'] = np.nan
rolling_results['ES_99_norm'] = np.nan


for i in range(252, len(returns)):

    window_data = returns.iloc[i-252:i]

    # HISTÓRICO
    sorted_r = window_data.sort_values()

    # 95%
    idx_95 = int(0.05 * len(sorted_r))
    VaR_95_h = sorted_r.iloc[idx_95]
    ES_95_h = sorted_r.iloc[:idx_95].mean()

    # 99%
    idx_99 = int(0.01 * len(sorted_r))
    VaR_99_h = sorted_r.iloc[idx_99]
    ES_99_h = sorted_r.iloc[:idx_99].mean()

    # NORMAL
    mu = window_data.mean()
    sigma = window_data.std()

    z_95 = norm.ppf(0.05)
    z_99 = norm.ppf(0.01)

    VaR_95_n = mu + sigma * z_95
    VaR_99_n = mu + sigma * z_99

    ES_95_n = mu - sigma * (norm.pdf(z_95) / 0.05)
    ES_99_n = mu - sigma * (norm.pdf(z_99) / 0.01)

    rolling_results.iloc[i, rolling_results.columns.get_loc('VaR_95_hist')] = VaR_95_h
    rolling_results.iloc[i, rolling_results.columns.get_loc('ES_95_hist')] = ES_95_h
    rolling_results.iloc[i, rolling_results.columns.get_loc('VaR_99_hist')] = VaR_99_h
    rolling_results.iloc[i, rolling_results.columns.get_loc('ES_99_hist')] = ES_99_h

    rolling_results.iloc[i, rolling_results.columns.get_loc('VaR_95_norm')] = VaR_95_n
    rolling_results.iloc[i, rolling_results.columns.get_loc('ES_95_norm')] = ES_95_n
    rolling_results.iloc[i, rolling_results.columns.get_loc('VaR_99_norm')] = VaR_99_n
    rolling_results.iloc[i, rolling_results.columns.get_loc('ES_99_norm')] = ES_99_n
    violations = rolling_results['Returns'] < rolling_results['VaR_95_hist']

# ---------------------------
# 🔧 IMPORT SEGURO
# ---------------------------
try:
    import plotly.graph_objects as go
    use_plotly = True
except:
    use_plotly = False

# ---------------------------
# 📉 GRÁFICA PRINCIPAL
# ---------------------------
st.subheader("📉 Returns vs VaR")

plot_data = rolling_results.copy()

if use_plotly:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=plot_data.index,
        y=plot_data['Returns'],
        name='Returns'
    ))

    fig.add_trace(go.Scatter(
        x=plot_data.index,
        y=plot_data['VaR_95_hist'],
        name='VaR 95%',
        line=dict(dash='dash')
    ))

    st.plotly_chart(fig)

else:
    st.line_chart(
        plot_data[['Returns', 'VaR_95_hist']]
    )

# ---------------------------
# 📊 VaR y ES
# ---------------------------
st.header("📊 VaR y Expected Shortfall", divider='red')

metodos = ["Normal", "t-Student", "Histórico", "Monte Carlo"]
metodo_sel = st.selectbox("Selecciona método", metodos)

alpha_sel = st.selectbox("Selecciona nivel de confianza", [0.95, 0.975, 0.99])

if metodo_sel == "Normal":
    VaR, ES = var_es_normal(returns, alpha_sel)
elif metodo_sel == "t-Student":
    VaR, ES = var_es_t(returns, alpha_sel)
elif metodo_sel == "Histórico":
    VaR, ES = var_es_hist(returns, alpha_sel)
else:
    VaR, ES = var_es_mc(returns, alpha_sel)

col1, col2 = st.columns(2)
col1.metric("VaR", f"{VaR:.5f}")
col2.metric("ES", f"{ES:.5f}")

# ---------------------------
# 📋 TABLA
# ---------------------------
st.subheader("📋 Comparación de métodos")

resultados = []

for a in [0.95, 0.975, 0.99]:
    var_n, es_n = var_es_normal(returns, a)
    var_t, es_t = var_es_t(returns, a)
    var_h, es_h = var_es_hist(returns, a)
    var_mc, es_mc = var_es_mc(returns, a)

    resultados.append({
        "Alpha": a,
        "VaR Normal": var_n,
        "VaR t": var_t,
        "VaR Hist": var_h,
        "VaR MC": var_mc,
    })

df_results = pd.DataFrame(resultados)
st.dataframe(df_results)

# ---------------------------
# 📊 GRÁFICA COMPARATIVA
# ---------------------------
st.subheader("📊 Comparación VaR")

if use_plotly:
    fig = go.Figure()

    for col in ["VaR Normal", "VaR t", "VaR Hist", "VaR MC"]:
        fig.add_bar(
            x=df_results["Alpha"],
            y=df_results[col],
            name=col
        )

    st.plotly_chart(fig)

else:
    st.bar_chart(
        df_results.set_index("Alpha")
    )


# INCISO D
st.subheader(" Rolling VaR (252 días)")

tipo_rolling = st.selectbox(
    "Tipo de VaR rolling",
    ["Histórico", "Normal"]
)

if tipo_rolling == "Histórico":
    cols = ['Returns', 'VaR_95_hist', 'ES_95_hist']
else:
    cols = ['Returns', 'VaR_95_norm', 'ES_95_norm']

if use_plotly:
    fig2 = go.Figure()

    for col in cols:
        fig2.add_trace(go.Scatter(
            x=plot_data.index,
            y=plot_data[col],
            name=col
        ))

    st.plotly_chart(fig2)

else:
    st.line_chart(plot_data[cols])
        
