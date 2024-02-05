from croniter import croniter_range
from datetime import datetime, timedelta, date
from random import random, randint
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(layout="wide")

def random_datetime_between(first_datetime, last_datetime):
    random_datetime = first_datetime + (last_datetime - first_datetime) * random()
    return random_datetime

def sample_dataframe(records=30):
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)

    data = []

    for i in range(records):
        task = f'Task {i + 1}'
        start = random_datetime_between(today, tomorrow)
        finish = random_datetime_between(start, tomorrow)
        resource = f'Server {randint(1, 5)}'

        line = {'Task': task, 'Start': start, 'Finish': finish, 'Resource': resource}
        data.append(line)

    df = pd.DataFrame(data)
    df = df.sort_values('Start')
    return df


def cron_dataframe(crontab_info, resource='Sample'):
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_finish = today_start.replace(hour=23, minute=59, second=59, microsecond=999)

    data = []

    crontabs = crontab_info.splitlines()

    for crontab_expression in crontabs:
        if not crontab_expression:
            continue
        splitted_expression = crontab_expression.split(' ')
        crontab = ' '.join(splitted_expression[:5])
        task = ' '.join(splitted_expression[5:])
        for start in croniter_range(today_start, today_finish, crontab):
            finish = start + timedelta(minutes=1)

            line = {'Task': task, 'Start': start, 'Finish': finish, 'Resource': resource}
            data.append(line)

    df = pd.DataFrame(data)
    df = df.sort_values('Start')
    return df


def generate_gaant(df):
    padding = 150 # arbitrary value depending on legends
    row_size = 30 # arbitrary value
    num_fields = df['Task'].nunique()
    height = padding + row_size * num_fields

    gaant_figure = ff.create_gantt(df, index_col='Resource', show_colorbar=True, show_hover_fill=True, group_tasks=True, height=height)

    gaant_figure.add_shape(
            go.layout.Shape(
                type="line",
                yref="paper",
                x0=datetime.now(),
                y0=0,
                x1=datetime.now(),
                y1=1,
                line=dict(
                    color="RoyalBlue",
                    width=3
                )
    ))
    return gaant_figure

crontab_info_default = """0 11 * * * Task 1
30 10 * * * Task 2
*/5 * * * * Task 3
0 12 * * * Task 4
40 15 * * * Task 5
*/30 * * * * Task 6
* */20 * * * Task 7
5 5 * * * Task 8
45 8 * * * Task 9
*/10 9 * * * Task 10
0 9 * * * Task 11
0 10 * * * Task 12
30 18 * * * Task 13
20 20 * * * Task 14
15 22 * * * Task 15
0 0 * * * Task 16"""

st.title('Streamlit Gaant')
crontab_info = st.text_area("Enter crontab expression", value=crontab_info_default)

# df = sample_dataframe()
df = cron_dataframe(crontab_info, 'Server 1')
gaant_figure = generate_gaant(df)

st.plotly_chart(gaant_figure, use_container_width=True, sharing="streamlit", theme="streamlit")
