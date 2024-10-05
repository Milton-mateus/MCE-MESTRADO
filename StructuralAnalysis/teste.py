import numpy as np
import plotly.graph_objects as go

# Dados iniciais
x = np.linspace(0, 10, 100)
fatores = [0.1, 1, 2, 3, 4, 5]

# Criando a figura
fig = go.Figure()

# Adicionando as linhas de função para diferentes fatores
for fator in fatores:
    y = fator * np.sin(x)
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=f'Fator: {fator}'))

# Configurando o layout
fig.update_layout(
    title='Gráfico Dinâmico com Slider',
    xaxis_title='x',
    yaxis_title='y',
)

# Adicionando slider para ajuste de fator
fig.update_layout(
    sliders=[{
        'active': 1,
        'yanchor': 'top',
        'xanchor': 'left',
        'currentvalue': {
            'prefix': 'Fator:',
            'visible': True,
            'xanchor': 'right'
        },
        'pad': {'b': 10},
        'len': 0.9,
        'x': 0.1,
        'y': -0.1,
        'steps': [{
            'label': str(fator),
            'method': 'update',
            'args': [
                {'y': [fator * np.sin(x) for fator in fatores]},
                {'title': f'Gráfico com Fator: {fator}'}
            ]
        } for fator in fatores]
    }]
)

# Exibindo o gráfico
fig.show()
