# Semáforo bursátil — versión móvil

Aplicación web Streamlit con una selección fija de 100 grandes acciones, otros activos y búsqueda por ticker. Análisis técnico basado en cierre diario de Yahoo Finance.

## Cómo obtener tu link público (una sola vez)

1. Creá una cuenta en https://github.com e iniciá sesión.
2. Creá un repositorio nuevo (por ejemplo `semaforo-bursatil`).
3. Subí **`app.py`** y **`requirements.txt`** a la raíz del repositorio (no subas el ZIP como único archivo).
4. Iniciá sesión en https://share.streamlit.io con GitHub.
5. Elegí **Create app / Deploy a public app**, seleccioná tu repositorio, rama `main` y archivo principal `app.py`.
6. Hacé clic en **Deploy**. Streamlit te asignará una URL propia terminada en `.streamlit.app`.
7. Abrí esa URL desde ChatGPT o tu teléfono y guardala en los favoritos o en la pantalla de inicio.

El alojamiento público depende de un tercero y puede tener límites, suspensiones, cambios de precio o dormir por inactividad. La URL concreta solo existe después del despliegue desde tu cuenta; este ZIP no es todavía un enlace público.

## Uso local opcional

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Cómo leer el semáforo

Se computan cinco señales binarias (precio frente a EMA20, EMA20 frente a EMA50, precio frente a SMA200, MACD frente a señal y RSI frente a 50). **COMPRAR** si 3 o más son alcistas y RSI está debajo de 70. **VENDER** si 3 o más son bajistas y RSI supera 30. De lo contrario **ESPERAR**. El score no es probabilidad de éxito y no contempla información fundamental, noticias ni costos de transacción.

Los niveles por ATR son ilustrativos para posiciones largas. La lista Top 100 es fija, una selección aproximada de grandes emisoras negociadas en EE. UU. a noviembre de 2026; puede dejar de corresponder al ranking actual. Para símbolos como BRK.B Yahoo Finance suele requerir `BRK-B`.
