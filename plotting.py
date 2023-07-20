from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
from history import load_ticker_history_pd_frame

def plot_ticker(ticker, ticker_history, module_config):
    # df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')
    df = load_ticker_history_pd_frame(ticker, ticker_history, convert_to_datetime=True, human_readable=True)
    fig = go.Figure(data=[go.Candlestick(x=df['date'],
                    open=df['open'], high=df['high'],
                    low=df['low'], close=df['close'])
                         ])
    # fig.append_trace()
    fig.update_layout(xaxis_rangeslider_visible=False,xaxis=dict(type = "date"),height=40000)
    fig.show()


def plot_ticker_with_indicators(ticker, ticker_history, indicator_data, module_config):

    df = load_ticker_history_pd_frame(ticker, ticker_history[-80:], convert_to_datetime=True, human_readable=True)
    subplot_titles = [x  for x in indicator_data.keys() if not indicator_data[x]['overlay']]
    # candle_fig  = make_subplots(rows=len([not x['overlay'] for x in indicator_data.values()]), cols=2, subplot_titles=subplot_titles)
    candle_fig = go.Figure(data=[go.Candlestick(x=df['date'],
                                         open=df['open'], high=df['high'],
                                         low=df['low'], close=df['close'],name=ticker)] )
    r = 1
    # c =2
    indicator_figure = make_subplots(rows=len([not x['overlay'] for x in indicator_data.values()]), cols=1, subplot_titles=subplot_titles)
    for key,x in indicator_data.items():
        if x['overlay']:
            if type(x['plot']) not in [list, tuple]:
                candle_fig.add_trace(x['plot'])
            else:
                for i in range(0, len(x['plot'])):
                    if type(x['plot'][i]) == go.Scatter:

                        candle_fig.add_trace(x['plot'][i])
                    else:
                        candle_fig.add_shape(x['plot'][i])
        else:
            if type(x['plot']) not in [list,tuple]:
                indicator_figure.add_trace(x['plot'], row=r, col=1)
            else:
                for i in range(0, len(x['plot'])):
                    indicator_figure.add_trace(x['plot'][i], row=r, col=1)
            r = r + 1
    candle_fig.update_layout(xaxis_rangeslider_visible=False, xaxis=dict(type="date"))
    min_percent=(50/100)*min([x.low for x in ticker_history])
    max_percent=(50/100)*max([x.low for x in ticker_history])
    # fig.update_yaxes( type='log')

    candle_fig.update_xaxes(rangebreaks=[
            dict(bounds=["sat", "mon"]),
            dict(bounds=[16, 9.5], pattern="hour"),

        ])
    candle_fig.show()
    indicator_figure.show()
    figures_to_html(ticker, [candle_fig, indicator_figure])
    pass

# def plot_sma(ticker, ticker_history,indicator_data, module_config):
#     df = load_ticker_history_pd_frame(ticker, ticker_history, convert_to_datetime=True, human_readable=True)
#     return go.Scatter(
#         x=df['date'],
#         y=[indicator_data[x.timestamp] for x in ticker_history],
#         name=f"sma{module_config['sma_window']}", mode='lines', line={'color':'blue'}
#     )

def plot_indicator_data(ticker, ticker_history,indicator_data, module_config, name='', color='blue', max=100):
    df = load_ticker_history_pd_frame(ticker, ticker_history, convert_to_datetime=True, human_readable=True)
    return go.Figure(data=go.Scatter(
        x=df['date'],
        y=[indicator_data[x.timestamp] for x in ticker_history],
        name=name, mode='lines', line={'color':color, 'width':1},
    ), layout_yaxis_range=[0, max]).data[0]


def plot_indicator_data_dual_y_axis(ticker, ticker_history,indicator_data, module_config,keys=[],colors=['blue']):

    fig  = make_subplots(rows=1, cols=1)
    # fig.add_trace()
    counter = 2

    for i in range(0, len(keys)):

        fig.add_trace(plot_indicator_data(ticker, ticker_history,indicator_data[keys[i]],module_config, color=colors[i], name=keys[i]), row=1, col=1)


    return fig.data

def plot_sr_lines(ticker, ticker_history,indicator_data, module_config):
    lines = []
    for sr_level in indicator_data:
        lines.append(go.Line(
            x0=ticker_history[0].dt,
            y0=sr_level,
            x1=ticker_history[-1].dt,
            y1=sr_level, line={'color': 'blue', 'width': 0.25, 'dash':'dashdot'}
        ))
    return lines


def figures_to_html(ticker,figs, filename="dashboard.html"):
    with open(filename, 'w') as dashboard:
        dashboard.write(f"<html><head></head><body><h2>${ticker}</h2>" + "\n")
        for fig in figs:
            inner_html = fig.to_html().split('<body>')[1].split('</body>')[0]
            dashboard.write(inner_html)
        dashboard.write("</body></html>" + "\n")