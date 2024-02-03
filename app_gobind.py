# Import necessary packages:
import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium, folium_static

# Write necessary functions:
def get_lat_lon(address):
    result = df[df['address'] == address]
    if not result.empty:
        return result.iloc[0]['HDB_lat'], result.iloc[0]['HDB_lon']
    else:
        return None, None

def get_closest_mrt(address):
    result = df[df['address'] == address]
    if not result.empty:
        return result.iloc[0]['most_closest_mrt']
    else:
        return None
def get_mrt_lat_lon(address):
    result = df[df['address'] == address]
    if not result.empty:
        return result.iloc[0]['mrt_lat'], result.iloc[0]['mrt_lon']
    else:
        return None, None
def get_mrt_time(address):
    result = df[df['address'] == address]
    if not result.empty:
        return result.iloc[0]['walking_time_mrt']
    else:
        return None
def get_recent_trans(address, flat_type):
    result = df2[(df2['address'] == address) & (df2['flat_type'] == flat_type)][['sold_year_month', 'flat_type', 'storey_range', 'floor_area_sqm',  'resale_price']]
    if not result.empty:
        return result.sort_values(by=['sold_year_month'], ascending=False).head(5).rename(columns={'sold_year_month': 'Date Sold', 'flat_type': 'Flat Type', 'storey_range': 'Storey Range', 'floor_area_sqm':'Floor Area (sqm)',  'resale_price':'Resale Price'})
    else:
        return pd.DataFrame()

# Start streamlit app:

st.image('For Streamlit.jpg', use_column_width=True)

st.write("""
# HDB Price Prediction App

##### This application utilises historical HDB sales data, walking distances to the nearest MRT station, and economic indicators to forecast future price trends within Singapore. Select an address to explore!
""")
st.write('---')

# Loads the HDB Unique House Price Dataset
df = pd.read_csv('hdb_unique_info.csv')
df2 = pd.read_parquet('final_HDB_for_model.parquet.gzip')
predictions_df = pd.read_parquet('dnn_HDB_forecast_2024_2033.parquet.gzip')

# Sidebar
# Header of Specify Input Parameters
st.sidebar.header('Specify Input Parameters')

# Initialize session state variables
if 'address_submitted' not in st.session_state:
    st.session_state['address_submitted'] = False
if 'flat_type_submitted' not in st.session_state:
    st.session_state['flat_type_submitted'] = False
if 'filtered_df' not in st.session_state:
    st.session_state['filtered_df'] = pd.DataFrame()
if 'submit_button' not in st.session_state:
    st.session_state['submit_button'] = None
if 'prediction' not in st.session_state:
    st.session_state['prediction'] = None
if 'map' not in st.session_state:
    st.session_state['map'] = None
if 'closest_mrt' not in st.session_state:
    st.session_state['closest_mrt'] = None

# Function to set the state when the address is submitted
def handle_address_submit():
    st.session_state['address_submitted'] = True
    st.session_state['filtered_df'] = df[df['address'] == address]

# Function to set the state when the flat_type is submitted
def handle_flat_type_submit():
    st.session_state['flat_type_submitted'] = True
    st.session_state['filtered_df'] = df[(df['flat_type'] == flat_type) & (df['address'] == address)]

# Start with the address input
address = st.sidebar.selectbox("Address", sorted(df['address'].unique()), placeholder="Choose an option", label_visibility="visible")

# When the user submits the address
if st.sidebar.button("Select Address", on_click=handle_address_submit):
    st.session_state['address'] = address

if not st.session_state['submit_button']:
    map_center = [1.3521, 103.8198]
    my_map = folium.Map(location=map_center, zoom_start=11.4)
    st_folium(my_map, width=725, height=484)




# If the address has been submitted, show additional inputs
if st.session_state['address_submitted']:
    filtered_df = st.session_state['filtered_df']

    # then is the flat_type input
    flat_type = st.sidebar.selectbox("Flat Type", sorted(filtered_df['flat_type'].unique()), placeholder="Choose an option", label_visibility="visible")

    # When the user submits the flat_type
    if st.sidebar.button("Select Flat Type", on_click=handle_flat_type_submit):
        st.session_state['flat_type'] = flat_type

    if st.session_state['flat_type_submitted']:
        filtered_df = st.session_state['filtered_df']


        with st.sidebar.form(key='User Input HDB Features'):
            # prediction_year
            year = st.slider('Year', 2024, 2033, 2028)
            # storey_range
            storey_range = st.selectbox("Storey Range", sorted(filtered_df['storey_range'].unique()), placeholder="Choose an option", label_visibility="visible")
            # flat_model
            flat_model = st.selectbox("Flat Model", sorted(filtered_df['flat_model'].unique()), placeholder="Choose an option", label_visibility="visible")
            # floor_area_sqm
            floor_area = st.selectbox('Floor Area (sqm)', sorted(filtered_df['floor_area_sqm'].unique()), placeholder="Choose an option", label_visibility="visible")

            submit_button = st.form_submit_button(label = 'Submit')

            if submit_button and not st.session_state.submit_button:
                st.session_state.submit_button = True


        if st.session_state.submit_button:
            filtered_df = st.session_state['filtered_df']
            # town:
            town = filtered_df['town'].mode()[0]
            # max_floor_lvl:
            max_floor_lvl = filtered_df['max_floor_lvl'].mean()
            # lease commencement date:
            lease_commence_date = int(filtered_df['lease_commence_date'].mean())
            # remaining lease:
            remaining_lease = 99 - (year - lease_commence_date)
            # closest mrt:
            closest_mrt = filtered_df['MRT'].mode()[0]
            # closest walking time:
            walking_time_mrt = filtered_df['walking_time_mrt'].mean()


            # Get prediction
            # predictions_df[(predictions_df['town'] == town) &
            #                (predictions_df['flat_type'] == flat_type) &
            #                (predictions_df['storey_range'] == storey_range) &
            #                (predictions_df['floor_area_sqm'] == floor_area) &
            #                (predictions_df['flat_model'] == flat_model) &
            #                (predictions_df['lease_commence_date'] == lease_commence_date) &
            #                (predictions_df['max_floor_lvl'] == max_floor_lvl) &
            #                (predictions_df['most_closest_mrt'] == closest_mrt)
            #                ]

            # prediction = predictions_df[(predictions_df['town'] == town) &
            #                (predictions_df['flat_type'] == flat_type) &
            #                (predictions_df['storey_range'] == storey_range) &
            #                (predictions_df['floor_area_sqm'] == floor_area) &
            #                (predictions_df['flat_model'] == flat_model) &
            #                (predictions_df['lease_commence_date'] == lease_commence_date) &
            #                (predictions_df['max_floor_lvl'] == max_floor_lvl) &
            #                (predictions_df['most_closest_mrt'] == closest_mrt)
            #                ].iloc[0:1]

            url = f'https://hdb-price-estimator-utpkxrm6xa-ew.a.run.app/predict?year={year}&town={town}&flat_type={flat_type}&storey_range={storey_range}&floor_area_sqm={floor_area}&flat_model={flat_model}&lease_commence_date={lease_commence_date}&sold_remaining_lease={remaining_lease}&max_floor_lvl={max_floor_lvl}&most_closest_mrt={closest_mrt}&walking_time_mrt={walking_time_mrt}'

            # Make the GET request
            response = requests.get(url)

            # Check if the request was successful
            if response.status_code == 200:
                # Parse the JSON response
                data = response.json()

                # Extract the 'hdb_pricing' value
                prediction = data.get("hdb_pricing", "Pricing not available")

            else:
                prediction = "Error: Could not retrieve prediction"

            # https://hdb-price-estimator-utpkxrm6xa-ew.a.run.app/predict?year=2028&town=HOUGANG&flat_type=3%20ROOM&storey_range=13%20TO%2015%20&floor_area_sqm=95&flat_model=Simplified&lease_commence_date=1980&sold_remaining_lease=93&max_floor_lvl=12&most_closest_mrt=KALLANG&walking_time_mrt=1500

            st.header('Prediction')
            st.session_state['prediction'] = st.subheader(f'The predicted price of a {(flat_type).lower()} flat of {floor_area} sqm in {town.title()} is :orange[SGD ${round(prediction/1000)*1000:,}] in {year}')
            # st.write(f'The predicted price of a {flat_type_selector} flat is SGD {round(prediction/1000000,2)} million in {year_selector}')
            st.write('---')

            st.header('Recent Transactions')
            st.subheader(f'{address.title()}')
            recent_trans = get_recent_trans(address, flat_type)
            recent_trans['Year'] = pd.DatetimeIndex(recent_trans['Date Sold']).year.astype(str)
            recent_trans['Month'] = pd.DatetimeIndex(recent_trans['Date Sold']).month
            recent_trans['Month'] = pd.to_datetime(recent_trans['Month'], format='%m').dt.strftime('%b')
            if not recent_trans.empty:
                st.dataframe(recent_trans, column_order=('Year', 'Month', 'Flat Type', 'Storey Range', 'Floor Area (sqm)', 'Resale Price'), hide_index=True, use_container_width=True)
            else:
                st.write("No recent transactions found")
            st.write('---')

            hdb_lat, hdb_lon = get_lat_lon(address)
            st.session_state['closest_mrt'] = get_closest_mrt(address)
            closest_mrt_lat, closest_mrt_lon = get_mrt_lat_lon(address)
            closest_mrt_time = get_mrt_time(address)

            m = folium.Map(location=[hdb_lat, hdb_lon], zoom_start=16)
            # ... add your markers to the map ...
            folium.Marker([hdb_lat, hdb_lon], popup="chosen unit", tooltip="chosen unit", icon=folium.Icon(color='red', prefix='fa',icon='home')).add_to(m)
            folium.Marker([closest_mrt_lat, closest_mrt_lon], popup="MRT", tooltip="MRT", icon=folium.Icon(color='green', prefix='fa',icon='subway')).add_to(m)
            folium.Circle([hdb_lat, hdb_lon], radius=500).add_to(m)
            st.session_state['map'] = m

            if st.session_state['map']:
                st.header('Proximity Map')
                st.write(f'The nearest MRT is: **{st.session_state["closest_mrt"]}**')
                # st.write(closest_mrt_lat, closest_mrt_lon)
                st.write(f'Walking time to the nearest MRT is: **{round(closest_mrt_time/60)} mins**')
                st_data = st_folium(st.session_state['map'], width=725, height=484)
                st.markdown('''*The circle shows everything within 500m walking distance*''')
                # st.write(hdb_lat, hdb_lon)
