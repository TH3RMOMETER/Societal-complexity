######
#
# run with bokeh serve --show dashboard_demo.py
#


from bokeh.models import BoxAnnotation, ColumnDataSource, Slider, Legend, LegendItem, Plot, Range1d, CustomJS
from bokeh.io import curdoc
from bokeh.plotting import figure, show
from bokeh.layouts import column, row
from bokeh.transform import cumsum

from math import pi
import pandas as pd
from functools import partial

from bokeh.palettes import Category20c
from bokeh.sampledata.browsers import browsers_nov_2013 as df



data=pd.DataFrame({
    'device': ['lighting','heating', 'kitchen', 'water', 'bathroom', 'free'], 
    'use': [10, 50, 15, 10, 10, 5]
})    

# Values
data['angle'] = data['use']/data['use'].sum() * 2 * pi  # Wedges
data['color'] = Category20c[len(data)]                  # Colors
data['value'] = 100 * (data['use']/data['use'].sum())   # Actual Values in kW/h


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

    other = list(filter(lambda x: x != device, [heating, lighting, kitchen, water, bathroom]))

    # For iteration
    n = 4
    quotient, remainder = divmod(rest, n)
    result = [quotient if i < remainder else quotient for i in range(n)]

    for idx, slider in enumerate(other):
        slider.start = 0
        if slider.end + result[idx] > 100:
            slider.end = 100
           # print(slider.end)
        else:
            slider.end += result[idx]
        print(slider.end)

def slider_update(device, attrname, old, new):
        """Slider callback function to change the year and label accordingly"""
        #print(slider.value)
        global data, source , heating, lighting, kitchen, water, bathroom

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
            device.end = max_value
            free.end = max_value - device_use
       

# Slider for heat
heating = Slider(
    start=0, 
    end=data.loc[data['device'].isin(['heating', 'free']), 'use'].sum(), 
    value=data.loc[data['device'] == 'heating', 'use'].values[0], 
    step=1, 
    title='heating')

# Slider for light
lighting = Slider(
    start=0, 
    end=data.loc[data['device'].isin(['lighting', 'free']), 'use'].sum(), 
    value=data.loc[data['device'] == 'lighting', 'use'].values[0],
    step=1,
    title='lighting')

kitchen = Slider(
    start=0, 
    end=data.loc[data['device'].isin(['kitchen', 'free']), 'use'].sum(), 
    value=data.loc[data['device'] == 'kitchen', 'use'].values[0],
    step=1,
    title='kitchen')

water = Slider(
    start=0, 
    end=data.loc[data['device'].isin(['water', 'free']), 'use'].sum(), 
    value=data.loc[data['device'] == 'water', 'use'].values[0],
    step=1,
    title='water')

bathroom = Slider(
    start=0, 
    end=data.loc[data['device'].isin(['bathroom', 'free']), 'use'].sum(), 
    value=data.loc[data['device'] == 'bathroom', 'use'].values[0],
    step=1,
    title='bathroom')

free = Slider(
    start=0, 
    end=data.loc[data['device'].isin(['free', 'free']), 'use'].sum(), 
    value=data.loc[data['device'] == 'free', 'use'].values[0],
    step=1,
    title='free')

# Callback calls for sliders
heating.on_change('value', partial(slider_update, heating))
lighting.on_change('value', partial(slider_update, lighting))
kitchen.on_change('value', partial(slider_update, kitchen))
water.on_change('value', partial(slider_update, water))
bathroom.on_change('value', partial(slider_update, bathroom))


p.annular_wedge(x=0, y=1,  inner_radius=0.15, outer_radius=0.25, direction="anticlock",
                start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                line_color="white", fill_color='color', source=source)

p.axis.axis_label=None
p.axis.visible=False
p.grid.grid_line_color = None


curdoc().add_root(
    column(row(p, column(
                        heating,
                        lighting,
                        kitchen,
                        water,
                        bathroom
                        )
                )
            )
    )