# -*- coding: utf-8 -*-
# Copyright 2018-2019 Streamlit Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""An example of showing geographic data."""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

DATE_TIME = "data"
# DATA_URL = (
#     "http://s3-us-west-2.amazonaws.com/streamlit-demo-data/uber-raw-data-sep14.csv.gz"
# )

st.title("Óbitos registrados no DATASUS no estado de São Paulo")
# st.markdown(
#     """
# This is a demo of a Streamlit app that shows the Uber pickups
# geographical distribution in New York City. Use the slider
# to pick a specific hour and look at how the charts change.

# [See source code](https://github.com/streamlit/demo-uber-nyc-pickups/blob/master/app.py)
# """)


@st.cache(persist=True)
def load_data(nrows):
    # data = pd.read_csv(DATA_URL, nrows=nrows)
    data = pd.read_parquet("../data/clean/dataset.parquet.gzip")

    def lowercase(x):
        return str(x).lower()

    data.rename(lowercase, axis="columns", inplace=True)
    data[DATE_TIME] = pd.to_datetime(data[DATE_TIME])
    return data


data = load_data(10000000)

hour = st.slider("Horário para observar", 0, 23)

data = data[data[DATE_TIME].dt.hour == hour]

st.subheader("Dados de geolocalização entre %i:00 e %i:00" % (hour, (hour + 1) % 24))
midpoint = (np.average(data["lat"]), np.average(data["lon"]))
st.deck_gl_chart(
    viewport={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 7,
        "pitch": 50,
    },
    layers=[
        {
            "type": "HexagonLayer",
            "data": data,
            "radius": 1000,
            "elevationScale": 4,
            "elevationRange": [0, 10000],
            "pickable": True,
            "extruded": True,
        }
    ],
)

st.subheader("Quebra por minuto entre %i:00 e %i:00" % (hour, (hour + 1) % 24))
filtered = data[
    (data[DATE_TIME].dt.hour >= hour) & (data[DATE_TIME].dt.hour < (hour + 1))
]
hist = np.histogram(filtered[DATE_TIME].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({"minuto": range(60), "obitos": hist})
st.write(
    alt.Chart(chart_data, height=150)
    .mark_area(interpolate="step-after", line=True)
    .encode(
        x=alt.X("minuto:Q", scale=alt.Scale(nice=False)),
        y=alt.Y("obitos:Q"),
        tooltip=["minuto", "obitos"],
    )
)

if st.checkbox("Mostrar dado cru (raw)", False):
    st.subheader("Dados por minuto entre %i:00 e %i:00" % (hour, (hour + 1) % 24))
    st.write(data)
