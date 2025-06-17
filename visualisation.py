import json
import os
import pandas as pd
import plotly.express as px
import plotly.io as pio

# Load configuration paths
with open("./config.json", 'r', encoding='utf-8') as f:
    conf = json.load(f)

# Get path
file_path = conf['output']['path']

# Create the images directory if it doesn't exist
image_dir = conf['images']['path']
if not os.path.exists(image_dir):
    os.makedirs(image_dir)

# Load CSV file
data = pd.read_csv(file_path, sep=',')

# Convert 'datetime' to datetime type for proper plotting
data['datetime'] = pd.to_datetime(data['datetime'])


# Time Series Plot for PM2.5 values over time
def plot_time_series(data):
    fig_time_series = px.line(
        data,
        x='datetime',
        y='value',
        facet_row='parameter',
        color='quality',
        title='Time Series of PM2.5 Values',
        labels={'datetime': 'Date and Time'},
        hover_data={'location': True}
    )
    fig_time_series.write_image(f"{image_dir}/time_series.png")
    fig_time_series.show()


# Geospatial Plot for PM2.5 values
# this visualisation will be useful, with multiple locations and paramters
def plot_geospatial(data):
    fig_geo = px.scatter_geo(
        data,
        lat='lat',
        lon='lon',
        color='parameter',
        size='value',
        hover_name='location',
        title='Geospatial Distribution',
        projection='natural earth'
    )
    fig_geo.write_image(f"{image_dir}/geospatial_distribution.png")
    fig_geo.show()


# Parameter Distribution Plot
# Quality Category Analysis Plot
def plot_quality_category(data):
    fig_quality = px.bar(
        data,
        x='quality',
        color='parameter',
        title='Distribution of Air Quality Categories',
        labels={'quality': 'Quality Category', 'count': 'Count'},
    )
    fig_quality.write_image(f"{image_dir}/quality_category.png")
    fig_quality.show()


plot_time_series(data)
plot_geospatial(data)
plot_quality_category(data)

