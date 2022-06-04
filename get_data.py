"""
Contains all the functions to retrieve and wrangle datasets
- API Calls
- Join, merge
- File type changing
"""


def get_token():
    return ('dwri0008', "sk.eyJ1IjoiZHdyaTAwMDgiLCJhIjoiY2t0YzV4dnZtMjJzMDM0bzgxZXgxa2V2cSJ9.ClL3-NEdsSZGxX3Xn-eWIg")


def daily_api():
    """ Call API for daily update data """
    import pandas as pd
    from sodapy import Socrata
    from tqdm import tqdm
    import itertools
    # Connect to client
    print("Getting data from API")
    client = Socrata("data.melbourne.vic.gov.au", 'Fv4fWBXLlwoSc7yHoB12IFAex')

    # Get data from open data Melboourne
    results = client.get("wuf8-susg", limit=99999)
    df = pd.DataFrame.from_records(results)
    del results
    df = df[['the_geom', 'bay_id']]
    df = df.drop_duplicates(subset='bay_id', keep='first').reset_index(drop=True)
    print('Daily API Retrieved')
    # Change location from polygons to point data
    df.the_geom = df.the_geom.apply(lambda x: x['coordinates'][0][0][0]).values
    time = pd.date_range(start='09/06/21', end='09/13/21', freq='1H')[:-1]
    temp_list = []
    # Transform each BayID to have input for every day and every hour
    for i in tqdm(df.index):
        temp_df = pd.DataFrame({'BayID':df['bay_id'].iloc[i], 'Time':time,
                          'lat':df['the_geom'].iloc[i][1], 'lon':df['the_geom'].iloc[i][0]}).values.tolist()
        temp_list.append(temp_df)
    temp_list = list(itertools.chain(*temp_list)) # Flatten list
    df = pd.DataFrame(temp_list, columns=['BayID', 'Time', 'lat', 'lon'])
    df['Time'] = pd.to_datetime(df['Time'])
    df['DOW'] = df['Time'].dt.dayofweek + 1 # Change day of week to align with other dataset
    df['HOUR'] = df['Time'].dt.hour # Get hour from time
    df = df.drop(columns={'Time'})
    return df


def join_historical_and_daily(historical_df, daily_df):
    """ Join Historical and Daily Dataframe to use """
    # Set both as string type to ensure matching
    print("Joining Historical Data")
    historical_df.BayID = historical_df.BayID.astype(str)
    daily_df.BayID = daily_df.BayID.astype(str)
    df = historical_df.merge(daily_df, how='right', on=['BayID','HOUR','DOW']) # all with location
    #df = historical_df.set_index('BayID').join(daily_df.set_index('BayID'), how='outer')
    #df = df.reset_index().rename(columns={'index':'BayID'})
    print("Historical Data Joined")
    return df


def df_to_geojson(df, json_name='MappingData.geojson'):
    """ Transform pandas dataframe to geojson file """
    import geopandas
    import pandas as pd
    gdf = geopandas.GeoDataFrame(
        df, geometry=geopandas.points_from_xy(df.lon, df.lat)).rename(columns={'level: 0':'Index'})
    gdf.to_file(json_name, driver="GeoJSON")
    return


def geojson_split(df, folder_path="MappingData"):
    """ Split into GeoJSON for each day and hour """
    import geopandas
    import pandas as pd
    from get_data import df_to_geojson
    print("Making GeoJSON files")
    hours = range(24)
    dow = range(1,8)
    [[df_to_geojson(df.loc[(df.DOW==day) & (df.HOUR==hour)], f'{folder_path}/Mapping_day-{day}_hour-{hour}.geojson') for hour in hours] for day in dow]
