#INTEGRANTES**
#**NAVARRETE RUVALCABA DIEGO**
#**MARTINEZ MAYA JULIA**
#**TRUJILLO MORALES DAFNE SOFIA**
#**PUEBLITA ZACARIAS ARACELI MICHEL**

import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from scipy.stats import norm
from scipy.stats import t
# Configuración de la página
st.markdown("""
<style>

/* 🌌 Fondo */
.stApp {
    background-image: url("https://png.pngtree.com/background/20230520/original/pngtree-bitcoin-on-a-black-background-picture-image_2673444.jpg");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* 🔥 overlay SIN romper layout */
[data-testid="stAppViewContainer"] {
    background-color: rgba(0, 0, 0, 0.50);
}

/* 🧊 glass effect */
.block-container {
    background: rgba(20, 20, 20, 0.6);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 2rem;
}

/* ✨ texto */
h1, h2, h3, h4, h5, h6, p, div, span {
    color: #f5f5f5 !important;
}

</style>
""", unsafe_allow_html=True)
def get_data():
    ticker = "BTC-USD"
    data = yf.download(ticker, start="2010-01-01")

    if 'Adj Close' in data.columns:
        data['Retornos'] = data['Adj Close'].pct_change()
    else:
        data['Retornos'] = data['Close'].pct_change()

    data = data.dropna()

    return data

data = get_data()


st.title("📉 Análisis de Riesgo Financiero")
st.write("Estimación de Value at Risk (VaR) y Expected Shortfall (ES)")

st.header("Datos históricos", divider="gray")
st.write(data.head())

# Rendimientos

st.header("Rendimientos diarios", divider="gray")

st.line_chart(data['Retornos'])


st.header("Estadísticas", divider="gray")
#INCISO B
media = data['Retornos'].mean()
sesgo = data['Retornos'].skew()
curtosis = data['Retornos'].kurt()

col1, col2, col3 = st.columns(3)

col1.metric("Media", f"{media:.6f}")
col2.metric("Sesgo", f"{sesgo:.4f}")
col3.metric("Curtosis", f"{curtosis:.4f}")
#INCISO C
st.header("VaR y Expected Shortfall", divider= 'red')
alpha = [0.95, 0.975, 0.99]

def var_es_normal(retornos, alpha):
    mean = retornos.mean()
    std = retornos.std()

    z = norm.ppf(1 - alpha)

    VaR = mean + z * std
    ES = mean - std * (norm.pdf(z) / (1 - alpha))

    return VaR, ES


from scipy.stats import t as student_t

def var_es_t(retornos, alpha):
    retornos = pd.Series(retornos)

    retornos = retornos.replace([np.inf, -np.inf], np.nan)
    retornos = retornos.dropna()

    retornos = pd.to_numeric(retornos, errors='coerce').dropna()

    if len(retornos) < 20:
        return np.nan, np.nan

    if retornos.std() == 0:
        return np.nan, np.nan

    data = retornos.values

    try:
        gl, media, desv = student_t.fit(data)

        # evitar gl problemático
        if gl <= 2:
            return np.nan, np.nan

        x = student_t.ppf(1 - alpha, gl)

        VaR = media + desv * x

        ES = media - desv * (
            (student_t.pdf(x, gl) / (1 - alpha)) * (gl + x**2) / (gl - 1)
        )

        return VaR, ES

    except Exception as e:
        return np.nan, np.nan

    return VaR, ES
def var_es_hist(retornos, alpha):
    sorted_retornos = pd.Series(retornos).dropna().sort_values()

    n = len(sorted_retornos)

    if n < 10:
        return np.nan, np.nan

    index = int((1 - alpha) * n)

    index = max(1, min(index, n - 1))

    VaR = sorted_retornos.iloc[index]

    ES = sorted_retornos.iloc[:index].mean()

    return VaR, ES
def var_es_mc(retornos, alpha, n_sim=10000):
    media = retornos.mean()
    dev = retornos.std()


    sim = np.random.normal(media, dev, n_sim)

    # VaR
    VaR = np.percentile(sim, (1 - alpha) * 100)

    # ES
    ES = sim[sim <= VaR].mean() #Seleccionamos solo los que son menores a VaR

    return VaR, ES

retornos = data['Retornos']

# DataFrame donde guardarás res
roll_res = pd.DataFrame(index=retornos.index) #Necesitamos indice de tiempo

# Inicializar columnas
roll_res['Retornos'] = retornos
roll_res['VaR_95_hist'] = np.nan
roll_res['ES_95_hist'] = np.nan
roll_res['VaR_99_hist'] = np.nan
roll_res['ES_99_hist'] = np.nan
roll_res['VaR_95_norm'] = np.nan
roll_res['ES_95_norm'] = np.nan
roll_res['VaR_99_norm'] = np.nan
roll_res['ES_99_norm'] = np.nan


for i in range(252, len(retornos)):

    window_data = retornos.iloc[i-252:i]

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

    roll_res.iloc[i, roll_res.columns.get_loc('VaR_95_hist')] = VaR_95_h
    roll_res.iloc[i, roll_res.columns.get_loc('ES_95_hist')] = ES_95_h
    roll_res.iloc[i, roll_res.columns.get_loc('VaR_99_hist')] = VaR_99_h
    roll_res.iloc[i, roll_res.columns.get_loc('ES_99_hist')] = ES_99_h

    roll_res.iloc[i, roll_res.columns.get_loc('VaR_95_norm')] = VaR_95_n
    roll_res.iloc[i, roll_res.columns.get_loc('ES_95_norm')] = ES_95_n
    roll_res.iloc[i, roll_res.columns.get_loc('VaR_99_norm')] = VaR_99_n
    roll_res.iloc[i, roll_res.columns.get_loc('ES_99_norm')] = ES_99_n
    violacion = roll_res['Retornos'] < roll_res['VaR_95_hist']


try:
    import plotly.graph_objects as go
    use_plotly = True
except:
    use_plotly = False


# 📉 GRÁFICA
st.subheader("📉 Retornos vs VaR")

plot_data = roll_res.copy()

if use_plotly:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=plot_data.index,
        y=plot_data['Retornos'],
        name='Retornos'
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
        plot_data[['Retornos', 'VaR_95_hist']]
    )


# 📊 VaR y ES

st.header("📊 VaR y Expected Shortfall", divider='red')

metodos = ["Normal", "t-Student", "Histórico", "Monte Carlo"]
metodo_sel = st.selectbox("Selecciona método", metodos)

alpha_sel = st.selectbox("Selecciona nivel de confianza", [0.95, 0.975, 0.99])

if metodo_sel == "Normal":
    VaR, ES = var_es_normal(retornos, alpha_sel)
elif metodo_sel == "t-Student":
    VaR, ES = var_es_t(retornos, alpha_sel)
elif metodo_sel == "Histórico":
    VaR, ES = var_es_hist(retornos, alpha_sel)
else:
    VaR, ES = var_es_mc(retornos, alpha_sel)

col1, col2 = st.columns(2)
col1.metric("VaR", f"{VaR:.5f}")
col2.metric("ES", f"{ES:.5f}")


# TABLA

st.subheader("📋 Comparación de métodos")

res = []

for a in [0.95, 0.975, 0.99]:
    var_n, es_n = var_es_normal(retornos, a)
    var_t, es_t = var_es_t(retornos, a)
    var_h, es_h = var_es_hist(retornos, a)
    var_mc, es_mc = var_es_mc(retornos, a)

    res.append({
        "Alpha": a,
        "VaR Normal": var_n,
        "VaR t": var_t,
        "VaR Hist": var_h,
        "VaR MC": var_mc,
    })

df_results = pd.DataFrame(res)
st.dataframe(df_results)


# GRÁFICA
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
    cols = ['Retornos', 'VaR_95_hist', 'ES_95_hist']
else:
    cols = ['Retornos', 'VaR_95_norm', 'ES_95_norm']

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
#PERDIDAS MAYORES, INCISO E)

st.header("📉 Backtesting")

# Ajuste  sola vez (clave para que no se trabe)
gl_t, media_t, desv_t = student_t.fit(retornos)

violacion_results = []

for alpha in [0.95, 0.975, 0.99]:

    var_violacion = 0
    es_violacion = 0
    total = 0

    x = student_t.ppf(1 - alpha, gl_t)

    VaR_const = media_t + desv_t * x
    ES_const = media_t - desv_t * (
        (student_t.pdf(x, gl_t) / (1 - alpha)) * (gl_t + x**2) / (gl_t - 1)
    )

    for i in range(252, len(retornos)):

        r_t = retornos.iloc[i]
        total += 1

        if r_t < VaR_const:
            var_violacion += 1

        if r_t < ES_const:
            es_violacion += 1

    violacion_results.append({
        "Alpha": alpha,
        "VaR Violations": var_violacion,
        "VaR %": var_violacion / total if total != 0 else np.nan,
        "Expected %": 1 - alpha,
        "ES Violations": es_violacion,
        "ES %": es_violacion / total if total != 0 else np.nan
    })

df_viol = pd.DataFrame(violacion_results)
st.dataframe(df_viol)



# INCISO (f) — VaR con volatilidad móvil


st.header("📊 VaR Volatilidad Móvil")

# Cálculo rolling VaR
roll_res['VaR_95_vol'] = np.nan
roll_res['VaR_99_vol'] = np.nan

for i in range(252, len(retornos)):

    window = retornos.iloc[i-252:i]

    mu = window.mean()
    sigma = window.std()

    z_95 = norm.ppf(0.05)
    z_99 = norm.ppf(0.01)

    roll_res.iloc[i, roll_res.columns.get_loc('VaR_95_vol')] = mu + sigma * z_95
    roll_res.iloc[i, roll_res.columns.get_loc('VaR_99_vol')] = mu + sigma * z_99


# GRÁFICA VaR VOL


st.subheader("📉 VaR con volatilidad móvil")

plot_data = roll_res.dropna(subset=['VaR_95_vol'])

if len(plot_data) == 0:
    st.warning("⚠️ No hay datos para graficar VaR vol")
else:
    if use_plotly:
        import plotly.graph_objects as go

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=plot_data.index,
            y=plot_data['Retornos'],
            name='Retornos'
        ))

        fig.add_trace(go.Scatter(
            x=plot_data.index,
            y=plot_data['VaR_95_vol'],
            name='VaR 95%',
            line=dict(dash='dash')
        ))

        fig.add_trace(go.Scatter(
            x=plot_data.index,
            y=plot_data['VaR_99_vol'],
            name='VaR 99%',
            line=dict(dash='dot')
        ))

        st.plotly_chart(fig)

    else:
        st.line_chart(plot_data[['Retornos','VaR_95_vol','VaR_99_vol']])



#  Backtesting VaR VOL


st.subheader("📊 Backtesting VaR (Volatilidad móvil)")

violacion_vol = []

for alpha, col in [(0.95, 'VaR_95_vol'), (0.99, 'VaR_99_vol')]:

    violacion = 0
    total = 0

    for i in range(252, len(retornos)):

        VaR_t = roll_res.iloc[i][col]
        r_t = retornos.iloc[i]

        if np.isnan(VaR_t):
            continue

        total += 1

        if r_t < VaR_t:
            violacion += 1

    violacion_vol.append({
        "Alpha": alpha,
        "VaR Violations": violacion,
        "VaR %": violacion / total if total != 0 else np.nan,
        "Expected %": 1 - alpha
    })

df_vol = pd.DataFrame(violacion_vol)

st.dataframe(df_vol)



# DEBUG ÚTIL

st.write("Preview rolling:")
st.write(roll_res[['VaR_95_vol','VaR_99_vol']].tail())
