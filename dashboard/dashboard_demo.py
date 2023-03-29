######
#
# run with bokeh serve --show dashboard_demo.py
#


from bokeh.models import LinearColorMapper, ColumnDataSource, Slider, ColorBar, SingleIntervalTicker, RangeSlider, Range1d, FactorRange, CustomJS
from bokeh.io import curdoc
from bokeh.plotting import figure, show
from bokeh.layouts import column, row
from bokeh.transform import cumsum, transform
from bokeh.palettes import Category20c


from datetime import date
from math import pi
import pandas as pd
from functools import partial

from helper import preprocess

##### Weather #######

weather = preprocess(
    r'/Users/yvette/Coding/SCDD/Societal-complexity/dashboard/dataset_with_preds.parquet')

weather_source = ColumnDataSource(data=dict(weather))

min, max = 0, 84
#range_slider = RangeSlider(value=(min, max), start=0, end=len((weather)), width=1200)
range_slider = Slider(
    start=min,
    end=(len(weather) - 84),
    value=max,
    step=1,
    title='Startday from which 7 days ahead will be predicted',
    width=1200)

plot = figure(width=1200, x_range=(weather.time.min(), weather.time.loc[84]), title="Weather forecast",
              toolbar_location=None, tools="")

def slided(attrname, old, new):
    global weather, weather_source, range_slider, plot, min, max

    start_day = range_slider.value
    weather_data = weather.query('@start_day <= index <= @start_day + 84')
    weather_source.data = weather_data
    plot.x_range.start = weather_data.time.min()
    plot.x_range.end = weather_data.time.max()

# range_slider.js_on_change('value', callback)
range_slider.on_change('value', slided)

# color_mapper = np.array([ [r, g, 150] for r, g in zip(50 + 2 * x, 30 + 2 * y) ], dtype="uint8")
color_mapper = LinearColorMapper(
    palette='Turbo256', low=weather.tsurf_pred.min(), high=weather.tsurf_pred.max())

    
# Plot
plot.scatter('time',
             'dustcol_pred',
             radius='norm_wind',
             alpha=0.8,
             source=weather_source,
             fill_color={'field': 'tsurf_pred', 'transform': color_mapper}
             )

color_bar = ColorBar(color_mapper=color_mapper, label_standoff=12, border_line_color=None,
                     ticker=SingleIntervalTicker(interval=10))

plot.add_layout(color_bar, 'right')

plot.xaxis.axis_label = 'Marsian Days'
plot.yaxis.axis_label = 'Predicted Dustcolumn'


##### Weather end #########

data = pd.DataFrame({
    'device': ['lighting', 'heating', 'kitchen', 'water', 'bathroom', 'free'],
    'use': [10, 50, 15, 10, 10, 5]
})


# Values
data['angle'] = data['use']/data['use'].sum() * 2 * pi  # Wedges
data['color'] = Category20c[len(data)]                  # Colors
data['value'] = 100 * (data['use']/data['use'].sum())   # Actual Values in kW/h

# color_dict = {
#     'lighting': Category20c[len(data)][0],
#     'heating': Category20c[len(data)][1],
#     'kitchen': Category20c[len(data)][2],
#     'water': Category20c[len(data)][3],
#     'bathroom': Category20c[len(data)][4],
#     'free': Category20c[len(data)][5]
# }

source = ColumnDataSource(data=dict(data))

p = figure(height=350, title="", toolbar_location=None,
           tools="hover", tooltips="@device: @value{0.2f} %", x_range=(-.5, .5))


def update_angle(data):
    data['value'] = 100 * (data['use']/data['use'].sum())
    return data


def is_energy(new_free_use):
    return new_free_use >= 0


def update_slider_end(rest, device):
    # Use those vars here
    global heating, lighting, kitchen, water, bathroom

    other = list(filter(lambda x: x != device, [
                 heating, lighting, kitchen, water, bathroom]))

    # For iteration
    n = 4
    quotient, remainder = divmod(rest, n)
    result = [quotient if i < remainder else quotient for i in range(n)]
    i = 0
    for idx, slider in enumerate(other):
        slider.start = 0
        if slider.end + result[idx] > 100:
            slider.update(end=100)
            #slider.end = 100
        else:
            slider.update(end=slider.end+result[idx])
            #slider.end += result[idx]


def slider_update(device, attrname, old, new):
    """Slider callback function to change the year and label accordingly"""
    # print(slider.value)
    global data, source, heating, lighting, kitchen, water, bathroom

    # Get values from data
    device_use = data.loc[data['device'] == device.title, 'use'].values[0]
    free_use = data.loc[data['device'] == 'free', 'use'].values[0]

    # Get new desired use from slider
    new_device_use = device.value

    # Check if energy still positive
    new_free_use = free_use + device_use - new_device_use
    if is_energy(new_free_use):

        # Take energy from free and add to heating
        data.loc[data['device'] == device.title, 'use'] = new_device_use
        data.loc[data['device'] == 'free', 'use'] = new_free_use

        # Update the value column based on the updated use values
        data['value'] = 100 * (data['use'] / data['use'].sum())

        # Update the angle column based on the updated value column
        data['angle'] = data['value'] / data['value'].sum() * 2 * pi
        source.data = data

        update_slider_end(new_free_use, device)
    else:
        update_slider_end(new_free_use, device)
        max_value = device_use + free_use
        device.update(end=max_value)
        free.end = max_value - device_use


# Slider for heat
heating = Slider(
    start=0,
    end=data.loc[data['device'].isin(['heating', 'free']), 'use'].sum(),
    value=data.loc[data['device'] == 'heating', 'use'].values[0],
    step=1,
    title='heating',
    bar_color='#6baed6')

# Slider for light
lighting = Slider(
    start=0,
    end=data.loc[data['device'].isin(['lighting', 'free']), 'use'].sum(),
    value=data.loc[data['device'] == 'lighting', 'use'].values[0],
    step=1,
    title='lighting',
    bar_color='#3182bd')

kitchen = Slider(
    start=0,
    end=data.loc[data['device'].isin(['kitchen', 'free']), 'use'].sum(),
    value=data.loc[data['device'] == 'kitchen', 'use'].values[0],
    step=1,
    title='kitchen',
    bar_color='#9ecae1')

water = Slider(
    start=0,
    end=data.loc[data['device'].isin(['water', 'free']), 'use'].sum(),
    value=data.loc[data['device'] == 'water', 'use'].values[0],
    step=1,
    title='water',
    bar_color='#c6dbef')

bathroom = Slider(
    start=0,
    end=data.loc[data['device'].isin(['bathroom', 'free']), 'use'].sum(),
    value=data.loc[data['device'] == 'bathroom', 'use'].values[0],
    step=1,
    title='bathroom',
    bar_color='#e6550d')

free = Slider(
    start=0,
    end=data.loc[data['device'].isin(['free', 'free']), 'use'].sum(),
    value=data.loc[data['device'] == 'free', 'use'].values[0],
    step=1,
    title='free',
    bar_color='#fd8d3c')

# Callback calls for sliders
heating.on_change('value', partial(slider_update, heating))
lighting.on_change('value', partial(slider_update, lighting))
kitchen.on_change('value', partial(slider_update, kitchen))
water.on_change('value', partial(slider_update, water))
bathroom.on_change('value', partial(slider_update, bathroom))


p.annular_wedge(x=0, y=1,  inner_radius=0.15, outer_radius=0.25, direction="anticlock",
                start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                line_color="white", fill_color='color', source=source)


p.axis.axis_label = None
p.axis.visible = False
p.grid.grid_line_color = None


curdoc().add_root(
    column(row(p, column(
        heating,
        lighting,
        kitchen,
        water,
        bathroom
    ),
    ),
        row(range_slider),
        row(plot)
    )
)
