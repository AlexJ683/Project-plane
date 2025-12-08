import plotly.express as px
import requests
import pandas as pd
import streamlit as st
from word2number import w2n
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium


class Data_processing():
    def __init__(self):
        self.data = self.load_data()
        
        self.upload_headers =  {"airline": str,
                                "flight_number": str,
                                "departure_city": str,
                                "departure_time": str,
                                "stops": int,
                                "arrival_time": str,
                                "arrival_city": str,
                                "travel_class": str,
                                "duration": str,
                                "days_left": int,
                                "price": int}
        if self.data.empty:
            self.data_for_upload = [{"airline": "Placedholder",
                                "flight_number": "PH000",
                                "departure_city":"Placedholder",
                                "departure_time": "Placedholder",
                                "stops": 0,
                                "arrival_time": "Placedholder",
                                "arrival_city": "Placedholder",
                                "travel_class": "Placedholder",
                                "duration": "Placedholder",
                                "days_left": 0,
                                "price": 0}]
            self.post_data()
            self.data = self.load_data()
        else:
            self.data_for_upload = self.data.to_dict(orient="records")
            
        
        

    def load_data(self):
        url = "http://backend:8000/all_items/"
        data = requests.get(url)
        flights = data.json()
        df = pd.DataFrame(flights)
        return df
    
    def get_column_types(self, df=None):
        """Extract column names and their data types as a dictionary."""
        if df is None:
            df = self.data
            df = df.drop(columns=["id"])
        # Convert pandas dtypes to Python types
        type_map = {
            'int64': int,
            'int32': int,
            'float64': float,
            'float32': float,
            'object': str,
            'bool': bool,
            'datetime64': str
        }
        column_types = {}
        for col, dtype in df.dtypes.items():
            dtype_str = str(dtype)
            column_types[col] = type_map.get(dtype_str, str)
        return column_types

    def check_data(self, data):
        expected_types = self.get_column_types()
        for column, expected_type in expected_types.items():
            if column not in data.columns:
                return f"Missing column: {column}"
            if not all(isinstance(val, expected_type) or pd.isna(val) for val in data[column]):
                return f"Incorrect data type in column: {column}. Expected {expected_type.__name__}."
        return "Data is valid"
       
    def convert_to_JSON(self, data):
        self.data_for_upload= data.to_dict(orient="records")
        return self.data_for_upload
    
    def post_data(self):
        url = "http://backend:8000/posts/"
        for data in self.data_for_upload:
            if len(self.data) != 0 and data["flight_number"] in self.data["flight_number"].values:
                pass  # Skip duplicate flight_number
            else:
                response = requests.post(url, json=data)
                if response.status_code not in (200, 201):
                    return f"Failed to post data: {response.status_code}"
                
        return "Data posted successfully"
    
    def w2n_stuff(self, text):
        try:
            number = w2n.word_to_num(text)
            return number
        except ValueError:
            if text == "two_or_more":
                return 3
            return text
    
    def int_to_str_duration(self, duration):
        return str(duration)
    
    @st.cache_resource
    def get_geolocator(_self):
        """Cache the geolocator instance to avoid repeated initialization."""
        return Nominatim(user_agent="flight_app")
    
    @st.cache_data
    def geo_data(_self, departure_city: str, arrival_city: str):
        """Cache geocoding results by city names."""
        geolocator = _self.get_geolocator()
        try:
            dep_location = geolocator.geocode(departure_city, timeout=10)
            arr_location = geolocator.geocode(arrival_city, timeout=10)
        except Exception as e:
            st.error(f"Geocoding error: {e}")
            return None
        
        if dep_location and arr_location:
            flight_location = {
                "latitude_departure": dep_location.latitude,
                "longitude_departure": dep_location.longitude,
                "latitude_arrival": arr_location.latitude,
                "longitude_arrival": arr_location.longitude,
            }
            return flight_location
        return None
    
class web_app():
    def __init__(self):
        self.data_processing = Data_processing()

    def home_page(self):
        st.title("Flight Data Home")
        left, right = st.columns([1, 1])
        with left:
            bar_chart = px.bar(self.data_processing.data['airline'].value_counts(), title="Number of Flights per Airline")
            st.plotly_chart(bar_chart)
            st.write("Airlines available:", self.data_processing.data['airline'].nunique())
        with right:
            df = self.data_processing.data
            df["price"] = pd.to_numeric(df["price"], errors='coerce')
            df["duration"] = pd.to_numeric(df["duration"], errors='coerce')
            fig = px.scatter(df, x="price", y="duration", color="airline", title="Price vs Duration by Airline")
            st.plotly_chart(fig)
            st.write("Total flights loaded:", len(self.data_processing.data))
        
        st.dataframe(self.data_processing.data)
    

    def search_page(self):
        st.title("Flight Data search")
        st.write("Search for a flight by flight number\nPlease enter a flight number")
        flight_number = st.text_input("Flight Number: ")
        if flight_number:
            flight_details = self.data_processing.data[self.data_processing.data["flight_number"] == flight_number]
            if not flight_details.empty:
                st.write("Flight Details:")
                st.dataframe(flight_details)
                departure_city = flight_details.iloc[0]["departure_city"]
                arrival_city = flight_details.iloc[0]["arrival_city"]
                flight_locations = self.data_processing.geo_data(departure_city, arrival_city)
                if flight_locations:
                    m = folium.Map(location=[(flight_locations["latitude_departure"] + flight_locations["latitude_arrival"]) / 2,
                                            (flight_locations["longitude_departure"] + flight_locations["longitude_arrival"]) / 2], zoom_start=4)
                    folium.Marker([flight_locations["latitude_departure"], flight_locations["longitude_departure"]],
                                popup=f"Departure: {flight_details.iloc[0]['departure_city']}", icon=folium.Icon(color = "blue", icon="star")).add_to(m)
                    folium.Marker([flight_locations["latitude_arrival"], flight_locations["longitude_arrival"]],
                                popup=f"Arrival: {flight_details.iloc[0]['arrival_city']}", icon=folium.Icon(color = "blue", icon="star")).add_to(m)
                    folium.PolyLine(locations=[[flight_locations["latitude_departure"], flight_locations["longitude_departure"]],
                                            [flight_locations["latitude_arrival"], flight_locations["longitude_arrival"]]],
                                    color="blue").add_to(m)
                    st_folium(m, width=1200, height=500)
                else:
                    st.write("Could not retrieve geolocation data for the specified cities.")
            else:
                st.write("No flight found with that flight number.")
    
    def data_upload_page(self):
        st.title("Upload Flight Data")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
            # data preprocessing
            df = pd.read_csv(uploaded_file)
            df = df.drop(columns=["index"])
            df["stops"] = df["stops"].apply(self.data_processing.w2n_stuff)
            df["duration"] = df["duration"].apply(self.data_processing.int_to_str_duration)
            df = df.drop_duplicates(subset=["flight_number"], keep="first")
            st.dataframe(df)
            validation_message = self.data_processing.check_data(df)
            if validation_message != "Data is valid":
                st.error(validation_message)
            else:
                # data upload
                Json_data = self.data_processing.convert_to_JSON(df)
                if st.button("Upload Data"):
                    message = self.data_processing.post_data()
                    st.success(message)
                    self.data_processing.data = self.data_processing.load_data()


if __name__ == "__main__":
    app = web_app()

    st.set_page_config(page_title="Flight Data App", layout="wide")
    ROUTES = {"Home": app.home_page, "Overview": app.search_page, "Data Upload": app.data_upload_page}
    query_params = st.query_params
    page = query_params.get("page", ["Home"])[0] if isinstance(query_params.get("page"), list) else query_params.get("page", "Home")
    if page not in ROUTES:
        page = "Home"
        
    with st.sidebar:
        st.title("Navigation")
        selection = st.radio("Go to", list(ROUTES.keys()), index=list(ROUTES.keys()).index(page), format_func=str.title)

    if selection != page:
        st.query_params["page"] = selection
        st.rerun()
    
    if page == "Home":
        app.home_page()
    elif page == "Overview":
        app.search_page()
    elif page == "Data Upload":
        app.data_upload_page()
    