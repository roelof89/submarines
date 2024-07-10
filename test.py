import ee
import geemap
import requests

# Authenticate and initialize the Earth Engine API.
ee.Authenticate()
ee.Initialize(project='sub-mlx')

# Define the coordinates for the center of the area of interest
latitude = 52.916389  # 52°54'59"N
longitude = 158.488333  # 158°29'18"E
center = ee.Geometry.Point([longitude, latitude])

# Define the buffer distance in meters (approx. 900m height)
buffer_distance = 450  # Half of 900m to get a square of 900m x 900m

# Define the area of interest by buffering the center point
aoi = center.buffer(buffer_distance).bounds()

# Define the time range for the image collection
start_date = '2023-01-01'
end_date = '2023-12-31'

# Get Sentinel-2 image collection
collection = ee.ImageCollection('COPERNICUS/S2') \
    .filterDate(start_date, end_date) \
    .filterBounds(aoi) \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10))

# Get the median image to reduce cloud cover
image = collection.median().clip(aoi)

# Define visualization parameters
vis_params = {
    'min': 0,
    'max': 3000,
    'bands': ['B4', 'B3', 'B2']  # RGB bands
}

# Download the image with higher resolution
image_url = image.getThumbURL({
    'region': aoi,
    'min': vis_params['min'],
    'max': vis_params['max'],
    'bands': vis_params['bands'],
    'format': 'png',
    'dimensions': '3096x3096',
    'maxPixels': 1e99
})

# Save the image to disk
response = requests.get(image_url)

if response.status_code == 200:
    with open('satellite_image_high_res.png', 'wb') as f:
        f.write(response.content)
    print('Image saved as satellite_image_high_res.png')
else:
    print('Failed to retrieve the image')
