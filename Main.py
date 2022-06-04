from get_data import daily_api, join_historical_and_daily, geojson_split
from upload_data import mapbox_upload
from parking_contexts import closest_bays, infer_non_sensor_parks
import pandas as pd
from time import sleep
import datetime


if __name__ == '__main__':
        """ This will take in all the data after running BigQuery on historical data and then join with 
            location data to get lat and lon and then infer non-sensor parking predictons and then upload
            to MapBox which is automatically reflected on the website. """

        while True:
                try: # In-case API fails, reuse the same data
                        daily = daily_api() # Get daily API
                        previous_daily = daily.copy()
                except Exception as err:
                        print(err)
                        daily = previous_daily.copy()
                df = pd.read_csv('2019_results.csv') # <- Read historical data
                df = df[~df.Percent_Occupied.isnull()] # Remove nulls
                df.Percent_Occupied = round(df.Percent_Occupied.astype(float),3) # Round
                df = df.sort_values(['DOW','HOUR','BayID']) # Sort to speed join
                df = join_historical_and_daily(df, daily) # Join historical data with API data
                closest_sensors = closest_bays(df) # Get closest-sensors for non-sensor parks
                # Get Percent_Occupied from nearest sensors for non sensors parks
                df = infer_non_sensor_parks(closest_sensors, df, run=False) # run=True to run, this takes a *very* long time
                df = df.sort_values(['DOW','HOUR','BayID']) # Sort to day, hour, bay for faster splitting
                df.to_csv('MappingData.csv', index=False)
                # Split into GeoJSON for every day and hour
                geojson_split(df)
                print("Waiting 7 Days until " + (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%d/%m/%Y %H:%M:%S"))
                sleep(60*60*24*7) # Wait 60s * 60m * 24hours * 7 days (i.e 7 day wait)
