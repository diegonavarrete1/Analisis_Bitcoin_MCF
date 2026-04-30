**INTEGRANTES
NAVARRETE RUVALCABA DIEGO
MARTINEZ MAYA JULIA
TRUJILLO MORALES DAFNE SOFIA
PUEBLITA ZACARIAS ARACELI MICHEL**

# INTRODUCCION
Bitcoin nació el 31 de octubre de 2008, cuando una entidad o persona bajo el seudónimo de Satoshi Nakamoto publicó el libro blanco titulado *"Bitcoin: A Peer-to-Peer Electronic Cash System"*. Fue una respuesta directa a la crisis financiera global de ese año, diseñada como una alternativa descentralizada al sistema bancario tradicional, permitiendo transacciones de valor sin intermediarios.
Su comportamiento y la volatilidad que ves en tus análisis pueden explicarse a través de varios hitos clave:
# Eventos que definen precio
El Halving: Cada cuatro años, la recompensa por minar Bitcoin se reduce a la mitad. Este evento de choque de oferta suele preceder a los grandes mercados alcistas (bull).
Adopción Institucional: La entrada de fondos como BlackRock y la aprobación de ETFs han inyectado liquidez, pero también han cambiado la forma en que el mercado reacciona a las noticias macroeconómicas.
Crisis Globales: Como observamos el evento de marzo de 2020 (pandemia) generó un pico de volatilidad extrema que disparó los niveles de riesgo.

 la Curtosis de 7.8872 es el dato más contundente. Una distribución normal tiene una curtosis de 3. Al ser de casi 8, simboliza alta volatilidad
Indica que los eventos extremos (ganancias o pérdidas masivas) ocurren con mucha más frecuencia de lo que la estadística clásica predeciría.
# VaR (Value at Risk) 
El VaR intenta cuantificar la pérdida máxima en un tiempo determinado. Al comparar los métodos, vemos que el VaR Normal suele subestimar el peligro.
VaR Histórico: Refleja lo que realmente ha pasado. Para un nivel de confianza del 99%, el VaR Histórico se sitúa en -0.1006, indicando una pérdida potencial del 10% en un día.
   *VaR t-Student:* Es el que mejor se adapta a Bitcoin porque permite "colas" más anchas. Por eso es el más severo, llegando a -0.1118.
# Expected Shortfall (ES) y su Fluctuación
 * Análisis: con un nivel del 97.5%, el VaR t es -0.0716, pero el ES salta a -0.1348.
Esta fluctuación ocurre porque, cuando Bitcoin entra en pánico, el promedio de las pérdidas en la "cola" de la distribución es devastador. El ES no solo te dice que vas a perder, sino que si pierdes, probablemente sea un movimiento de doble dígito.
Conclusión sobre los Métodos
La fluctuación entre métodos (Histórico, Normal, Monte Carlo) se debe a cómo cada uno "interpreta" el pasado. Mientras que el Normal es una simplificación matemática, el Histórico y el Monte Carlo capturan mejor la naturaleza errática de Bitcoin, especialmente en años como 2020, donde el retorno diario cayó estrepitosamente.

   VaR Monte Carlo (MC): Tiende a promediar los resultados, siendo útil para simular miles de escenarios posibles, aunque en tus capturas suele estar cerca del Histórico.
El Expected Shortfall (ES) y su fluctuación
El ES siempre es mayor (más negativo) que el VaR porque no te dice "cuánto podrías perder", sino "si superas el VaR, qué tan grave será la pérdida en promedio".
 Años Específicos y Retornos Diarios
Mirando el gráfico de "Rendimientos diarios":
 * 2020 (El gran pico negativo): Se observa una caída masiva que llega casi al -0.4 (-40%). Esto coincide con el "Crash del COVID" en marzo de 2020. Es el punto que más ensucia la curtosis y obliga al Expected Shortfall a ser tan alto.
   2017-2018: Se nota una dispersión muy alta de puntos azules hacia arriba y hacia abajo, reflejando el mercado alcista de 2017 y el posterior mercado bajista.
   2024-2026: El gráfico muestra una volatilidad que parece "estabilizarse" un poco en comparación con los años salvajes de 2017 o 2020, aunque sigue manteniendo picos constantes por encima del 10% diario.
# Conclusión Técnica
El análisis infiere que Bitcoin no puede medirse con herramientas financieras tradicionales (VaR Normal) de forma segura. El hecho de que el ES sea casi el doble que el VaR en algunos niveles confirma que, cuando Bitcoin rompe sus soportes, lo hace de forma violenta.


