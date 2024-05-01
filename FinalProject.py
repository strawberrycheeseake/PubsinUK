import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt
from PIL import Image

st.set_option('deprecation.showPyplotGlobalUse', False)

#[PY3]
#This function will make a dictionary where the keys are the districts and the values are a list of the pubs in each district
#It will also return a list of the number of pubs in each district
def pubs_in_distric(df):
  dist_pubs_dict = {} #[PY5]
  for index, row in df.iterrows(): #[DA8]
    district = row['District']
    if district not in dist_pubs_dict:
      dist_pubs_dict[district] = [index]
    else:
      dist_pubs_dict[district].append(index)
  count_pubs = [len(pubs) for pubs in dist_pubs_dict.values()] #[PY4]
  return dist_pubs_dict, count_pubs #[PY2]

#This function will return a dictionary joining the districts with the number of pubs
#[PY3]
def join_publists(list1, list2):
  pub_dict = dict(zip(list1, list2)) #[PY5]
  return pub_dict

#This function will make a dataframe of the top_n (default is 5) rows in descending order of pub_dict
#[PY1] and [PY3]
def top_districtsforpubs(pub_dict, top_n = 5):
  df_topdistricts = pd.DataFrame(pub_dict.items(), columns=['District', 'Pub Count'])
  df_topdistricts = df_topdistricts.sort_values(by='Pub Count',ascending=False) #[DA2]
  df_topdistricts = df_topdistricts.set_index('District')
  df_topdistricts = df_topdistricts.head(top_n) #[DA3]
  return df_topdistricts

#This function will print the map of the two df's and change when a user picks a stop
def london_map(center_lat, center_lon, tubestops, pubs):
    tube_layer = pdk.Layer('ScatterplotLayer', data=tubestops,
                           get_position='[Long, Lat]',
                           get_radius=75,
                           get_fill_color=[0, 0, 255],
                           pickable=True)
    pubs_layer = pdk.Layer('ScatterplotLayer', data=pubs,
                           get_position='[Long, Lat]',
                           get_radius=50,
                           get_fill_color=[255, 0, 0],
                           pickable=True, auto_highlight=True)
    tool_tip = {"html": "Location:<br/> <b>{PubName}</b>",
            "style": { "backgroundColor": "steelblue",
                       "color": "white"}}
    mapview = pdk.ViewState(latitude=center_lat, longitude=center_lon,
                            zoom=13, pitch=0)
    londonmap = pdk.Deck(map_style='mapbox://styles/mapbox/outdoors-v11',
                         layers=[tube_layer, pubs_layer], tooltip= tool_tip, initial_view_state=mapview)
    st.pydeck_chart(londonmap) #[VIZ4]

#Intro
st.title("Pubs in the UK")
img = Image.open('beer.jpg')
st.image(img, width=300) #[ST4]

#Make Dataset
dfpubs = pd.read_csv('PubData2.csv',index_col='PubName')

#Clean out all pubs that don't have longitude or latitude given
#Had to change '\N' to NULL in the excel file
#[DA1]
dfpubs.replace({'NULL': None},inplace=True) #Used ChatGPT for the dictionary inside the replace
dfpubs.dropna(inplace=True)


#Map of all Pubs
st.header('Map of 9855 Pubs in the UK')
viewpubs = pdk.ViewState(latitude=dfpubs['Lat'].mean(), longitude=dfpubs['Long'].mean(),zoom=4, pitch=0)
tool_tip = {"html": "Pub Name:<br/> <b>{PubName}</b> <br/>District: <b>{District}</b>",
            "style": { "backgroundColor": "steelblue",
                       "color": "white"}
            }
layer = pdk.Layer('ScatterplotLayer', data=dfpubs.reset_index(), get_position='[Long, Lat]',
                  get_radius=1000, get_fill_color=[255, 0, 0], pickable=True) #ChatGPT Helped me with reset index


pubsmap = pdk.Deck(map_style='mapbox://styles/mapbox/outdoors-v11',
                   layers=[layer],
                   tooltip=tool_tip,
                   initial_view_state=viewpubs)
st.pydeck_chart(pubsmap) #[VIZ4]

#Pub Crawl Question
st.header("Looking for Nearby Pubs in London?")

#Make df of popular tube stops
#User can pick which stop they're at
#User can select from a multi-select which pubs they want to go to
#Map displays the tube stop and the pubs
dftube = pd.read_csv('TubeStops1.csv')
dftube['PubName'] = 'Station'

london_main_districts = ['Camden', 'Greenwich', 'Hackney', 'Hammersmith and Fulham',
                         'Islington', 'Kensington and Chelsea', 'Lambeth',
                         'Lewisham', 'Southwark', 'Tower Hamlets', 'Wandsworth',
                         'Westminster', 'City of London']
dflondonpubs = dfpubs[dfpubs['District'].isin(london_main_districts)] #df of london pubs
dflondonpubs = dflondonpubs.reset_index()

picked_stops = st.multiselect('Select Tube Stops:', dftube['TubeStop']) #[ST1]
dfpickedstops = dftube[dftube['TubeStop'].isin(picked_stops)] #df of tube stops picked

if not picked_stops:
    center_lat = dflondonpubs['Lat'].mean()
    center_long = dflondonpubs['Long'].mean()
else:
    center_lat = dfpickedstops['Lat'].mean()
    center_long = dfpickedstops['Long'].mean()
st.write('Blue dots are Tube Stops. Red dots are pubs')
london_map(center_lat, center_long, dfpickedstops, dflondonpubs)


#Best District out of the 359 to be in for Pubs
st.header('Best District out of the 359 to be in for Pubs')
counties_dict = pubs_in_distric(dfpubs)[0] #[PY3]
counties = list(counties_dict.keys()) #[PY5]
numcounty_pub = pubs_in_distric(dfpubs)[1] #[PY3]
num_pubs_county = join_publists(counties, numcounty_pub) #[PY3]

#Displaying the slider to control the number of districts displayed in the bar chart
#ChatGPT helped me with the parameters for the functions called for the slider and bar chart
#Also helped me rotating the x-axis labels
top_n = st.slider('Select the Number of Districts', min_value=1, max_value=10, value=5) #[ST2]
df_num_pubs_county = top_districtsforpubs(num_pubs_county, top_n) #[PY3]
bars = plt.bar(df_num_pubs_county.index, df_num_pubs_county['Pub Count'], color='blue')
plt.xlabel('Districts')
plt.xticks(rotation = 45, ha='right')
plt.ylabel('Number of Pubs')
plt.title('District with the Most Pubs')
for bar in bars:
    total_pubs = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, total_pubs, total_pubs, va='bottom')
st.pyplot() #[VIZ1]

#Displaying the Pie Chart
#Making 2 lists to call my joining lists to make dictionary function and then other function to make a dataframe
totalpubs = sum(numcounty_pub)
totalnpubs = df_num_pubs_county['Pub Count'].sum() #[DA9]
remainingpubs = totalpubs - totalnpubs
list1 = ["Top Districts' Pubs", 'Remaining Pubs']
list2 = [totalnpubs, remainingpubs]
dftotal_remainingpubs = top_districtsforpubs(join_publists(list1, list2),top_n) #[PY3]
plt.pie(dftotal_remainingpubs['Pub Count'], labels=dftotal_remainingpubs.index, autopct='%1.1f%%')
plt.title('Total Pubs in Top District vs Remaining Districts')
st.pyplot() #[VIZ2]

#User Ratings
st.header("Top 10 Pubs with the Highest Ratings")

#Display the dataframe of top 10 pubs with the highest ratings
#Generate random ratings for all pubs and find the average
#In other attached file

import randomrating
pub_sumrating_dict = randomrating.sumratings2

#Make a dictionary generating the average ratings
avg_ratings_dict = {}
for pub, ratings in pub_sumrating_dict.items(): #[PY5]
  sum_ratings, num_ratings = ratings #ChatGPT
  avg_rating = round((sum_ratings / num_ratings), 2)
  avg_ratings_dict[pub] = avg_rating


#Add to main df and display a pivot table of top 10 pubs with highest average ratings
dfpubs['Average Rating'] = dfpubs.index.map(avg_ratings_dict) #[DA9]
df_top10_pubs = dfpubs.sort_values(by='Average Rating', ascending=False).head(10)
st.dataframe(df_top10_pubs[['District','Average Rating']]) #[DA4]

#User can input their district, returns line chart of their pubs' ratings
st.write('Enter your District and see how your top 10 pubs are rated')
user_district = st.text_input('Enter District Name', 'County Durham') #[ST3]
df_user_district = dfpubs[dfpubs['District'] == user_district] #[DA4]
df_user_district_ratings = df_user_district[['Average Rating']].head(10)
plt.plot(df_user_district_ratings.index, df_user_district_ratings['Average Rating'], marker='o') #Used ChatGPT for marker
plt.xticks(rotation=45, ha='right')
st.pyplot() #[VIZ3]

#User search for a pubs rating
st.write('Search for a Pubs Average Rating')
pubs = dfpubs.index.tolist()
user_pub = st.text_input('Enter a Pub:')
if user_pub in pubs:
    st.write('This pub has an average rating of', avg_ratings_dict[user_pub]) #[PY5]