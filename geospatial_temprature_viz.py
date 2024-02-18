import geopandas as gpd
import folium
import ee

# Authenticate to the Earth Engine servers
ee.Initialize()

def visualize_temperature_patterns(region_of_interest):
    # Load MODIS Land Surface Temperature data
    modis_lst = ee.ImageCollection('MODIS/006/MOD11A2').select('LST_Day_1km')

    # Define a function to mask out cloudy pixels
    def maskClouds(image):
        qa = image.select('QC_Day')
        cloud = qa.bitwiseAnd(1 << 10).eq(0)
        return image.updateMask(cloud)

    # Filter the collection, apply the cloud mask function
    modis_lst_filtered = modis_lst.filterDate('2022-01-01', '2022-12-31').map(maskClouds)

    # Calculate the mean temperature
    mean_temp_img = modis_lst_filtered.mean()

    # Clip the image to the region of interest
    mean_temp_img_clipped = mean_temp_img.clip(region_of_interest)

    # Convert Earth Engine image to GeoPandas dataframe
    mean_temp_gdf = gpd.GeoDataFrame.from_features(
        mean_temp_img_clipped.reduceToVectors(geometryType='polygon'))

    # Create an interactive Folium map
    m = folium.Map(location=[mean_temp_gdf.geometry.centroid.y.mean(), 
                             mean_temp_gdf.geometry.centroid.x.mean()], 
                   zoom_start=8)

    # Add the GeoPandas GeoDataFrame to the map
    folium.GeoJson(mean_temp_gdf).add_to(m)

    # Save the map as an HTML file
    m.save('temperature_visualization.html')

# Example usage
region_of_interest = ee.Geometry.Rectangle([longitude_min, latitude_min, longitude_max, latitude_max])
visualize_temperature_patterns(region_of_interest)
