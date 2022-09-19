#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import requests
import osm2geojson
import shapely
import geopandas as gpd
import osmnx as ox
import numpy as np


# In[2]:


roads_central_district_with_intensity_and_noise = pd.read_csv('/Users/july/Desktop/Diplom_data_central_district_SPb/roads_central_district_with_intensivity.csv', sep = ";", encoding = 'utf-8')


# In[3]:


roads_central_district_with_intensity_and_noise


# In[4]:


emissons = pd.read_csv('/Users/july/Desktop/Diplom_data_central_district_SPb/emissions.csv', sep = ";", encoding = 'utf-8')


# In[5]:


roads_central_district_with_intensity_and_noise_and_emission = roads_central_district_with_intensity_and_noise.merge(emissons, on='linkId')


# In[6]:


roads_central_district_with_intensity_and_noise_and_emission


# In[7]:


roads_central_district_with_intensity_and_noise_and_emission = gpd.GeoDataFrame(roads_central_district_with_intensity_and_noise_and_emission, geometry=roads_central_district_with_intensity_and_noise_and_emission.apply(lambda x: shapely.wkt.loads(x['wkt_geom']),axis = 1))


# In[8]:


roads_central_district_with_intensity_and_noise_and_emission.to_file('roads_central_district_with_intensity_and_noise_and_emission.geojson',driver = 'GeoJSON')


# In[9]:


roads_central_district=gpd.read_file('/Users/july/Desktop/Diplom_data_central_district_SPb/roads_central_district_with_intensity_and_noise_and_emission.geojson').to_crs(3857)


# In[10]:


roads_central_district


# In[11]:


roads_buffered = gpd.read_file('/Users/july/Desktop/Diplom_data_central_district_SPb/roads_central_district_with_intensity_and_noise_and_emission.geojson').to_crs(3857)


# In[12]:


roads_buffered.geometry= roads_buffered.geometry.buffer(50)


# In[13]:


roads_buffered.to_file('roads_buffered.geojson',driver = 'GeoJSON')


# roads_buffered

# In[14]:


buildings=gpd.read_file('/Users/july/Desktop/Diplom_data_central_district_SPb/building_in_central_district.geojson').to_crs(3857)


# In[15]:


buildings


# In[16]:


buildings=buildings.to_crs(3857)


# In[18]:


poi=gpd.read_file('/Users/july/Desktop/Diplom_data_central_district_SPb/activities_in_roads_buffer_30.geojson').to_crs(3857)
work=gpd.read_file('/Users/july/Desktop/Diplom_data_central_district_SPb/work_central.geojson').to_crs(3857)
population=gpd.read_file('/Users/july/Desktop/Diplom_data_central_district_SPb/population_central.geojson').to_crs(3857)


# In[19]:


amount_of_population = []
for i in range(len(buildings)):
    s = population.within(buildings['geometry'][i])
    if len(s[s])>0:
        amount_of_population.append(1)
    else:
        amount_of_population.append(0)
print (amount_of_population)


# In[20]:


amount_of_work = []
for i in range(len(buildings)):
    s = work.within(buildings['geometry'][i])
    if len(s[s])>0:
        amount_of_work.append(1)
    else:
        amount_of_work.append(0)
print (amount_of_work)


# In[21]:


amount_of_poi = []
for i in range(len(buildings)):
    s = poi.within(buildings['geometry'][i])
    if len(s[s])>0:
        amount_of_poi.append(1)
    else:
        amount_of_poi.append(0)
print (amount_of_poi)


# In[22]:


buildings['amount_of_work']=amount_of_work
buildings['amount_of_population']=amount_of_population
buildings['amount_of_poi']=amount_of_poi
buildings['sum']=buildings['amount_of_poi']+buildings['amount_of_work']+buildings['amount_of_population']


# In[23]:


for index, row in buildings.iterrows():
        if row['sum'] == 3:
            buildings.loc[index, 'sum_of_point'] = 10
        elif row['sum'] == 2 :
            buildings.loc[index, 'sum_of_point'] = 6
        elif row['sum'] == 1 :
            buildings.loc[index, 'sum_of_point'] = 3
        elif row['sum'] == 0:
            buildings.loc[index, 'sum_of_point'] = 0


# In[24]:


amount_of_building = []
for i in range(len(roads_buffered)):
    s = buildings.intersects(roads_buffered['geometry'][i])
    if len(s[s])>0:
        a = len([item for item in s if item == True])
        amount_of_building.append(a)
    else:
        amount_of_building.append(0)
print (amount_of_building)


# In[26]:


#import sys
amount_of_point_of_building = []
for i in range(len(roads_buffered)):
    s = buildings.intersects(roads_buffered['geometry'][i])
    s = list(s)
    if len(s)>0:
        selected_building = []
        for i,j in enumerate(s):
            if j is True:
                selected_building.append(i)
        
        #selected_building = [item for item in s if item == True]
        #print(selected_building)
        acc_sum = 0
        for i in selected_building:
            point = buildings.loc[i, 'sum_of_point']
            #print(point)
            acc_sum+=point
        amount_of_point_of_building.append(acc_sum)
        #print(amount_of_building)
        #sys.exit(0)
        #a = len(selected_building)
        #amount_of_building.append(a)
    else:
        amount_of_point_of_building.append(0)
print (amount_of_point_of_building)


# In[27]:


roads_central_district['amount_of_building']=amount_of_building
roads_central_district['amount_of_point_of_building']=amount_of_point_of_building


# In[28]:


roads_central_district['point_for_mixed_used']=roads_central_district['amount_of_point_of_building']/roads_central_district['amount_of_building']


# In[29]:


roads_central_district


# In[30]:


activities=gpd.read_file('/Users/july/Desktop/Diplom_data_central_district_SPb/activities_in_roads_buffer_30.geojson').to_crs(3857)


# In[31]:


activities


# In[32]:


amount_of_organisation = []
for i in range(len(roads_buffered)):
    s = activities.intersects(roads_buffered['geometry'][i])
    if len(s[s])>0:
        a = len([item for item in s if item == True])
        amount_of_organisation.append(a)
    else:
        amount_of_organisation.append(0)
print (amount_of_organisation)


# In[33]:


roads_central_district['amount_of_organisation']=amount_of_organisation


# In[34]:


roads_central_district


# In[35]:


roads_central_district['amount_of_open_organisation']=roads_central_district['amount_of_organisation']/roads_central_district['amount_of_building']


# In[36]:


roads_central_district['roads_buffered_50_area']=roads_buffered.area


# In[37]:


open_public_places=gpd.read_file('/Users/july/Desktop/Diplom_data_central_district_SPb/open public spaces central district.geojson').to_crs(3857)


# In[38]:


open_public_places


# In[39]:


open_public_places_buffered_400 = open_public_places.copy()


# In[40]:


open_public_places_buffered_400 = open_public_places_buffered_400.buffer(400)


# In[41]:


open_public_places_buffered_1000 = open_public_places.copy()


# In[42]:


open_public_places_buffered_1000 = open_public_places_buffered_1000.buffer(1000)


# In[43]:


open_public_places_buffered_400


# In[44]:


from shapely.ops import unary_union
open_public_places_buffered_400_u = unary_union(open_public_places_buffered_400)
open_public_places_buffered_1000_u = unary_union(open_public_places_buffered_1000)


# In[45]:


opb_400_u = gpd.GeoDataFrame({'geometry': open_public_places_buffered_400_u})
opb_1000_u = gpd.GeoDataFrame({'geometry': open_public_places_buffered_1000_u})
opb_1000_400_u = gpd.overlay(opb_1000_u,opb_400_u,how='difference')


# In[46]:


opb_400_u['id'] = opb_400_u.index
opb_1000_400_u['id'] = opb_1000_400_u.index
roads_buffered['id'] = roads_buffered.index
intersection_400_u = gpd.overlay(roads_buffered, opb_400_u, how='intersection')
intersection_1000_400_u = gpd.overlay(roads_buffered, opb_1000_400_u, how='intersection')
intersection_400_u['intersection_400_u_area']=intersection_400_u.area
intersection_1000_400_u['intersection_1000_400_u_area']=intersection_1000_400_u.area
intersection_400_area = intersection_400_u.groupby('linkId')['intersection_400_u_area'].sum()
intersection_1000_area = intersection_1000_400_u.groupby('linkId')['intersection_1000_400_u_area'].sum()


# In[47]:


intersection_400_area=intersection_400_area.to_frame()
intersection_1000_area=intersection_1000_area.to_frame()


# In[48]:


roads_central_district_alldata = roads_central_district.copy()


# In[49]:


roads_central_district_alldata = roads_central_district_alldata.merge(intersection_400_area, how='left', on='linkId').fillna(0)
roads_central_district_alldata = roads_central_district_alldata.merge(intersection_1000_area, how='left', on='linkId').fillna(0)


# In[50]:


roads_central_district_alldata 


# In[51]:


roads_central_district_alldata .to_file('roads_central_district_alldata .geojson',driver = 'GeoJSON')


# In[55]:


all_data = roads_central_district_alldata.copy()


# In[56]:


all_data.to_file('all_data.geojson',driver = 'GeoJSON')


# In[57]:


all_data


# In[61]:


def sum_of_point_for_pedestrianisation(all_data):
    for i in range(len(all_data)):
        point_for_open_organisation = all_data['amount_of_open_organisation']*10
        all_data['point_for_open_organisation']=point_for_open_organisation
        intersection_out_1000_u_area = all_data['roads_buffered_50_area']-all_data['intersection_400_u_area']-all_data['intersection_1000_400_u_area']
        point_for_nearest_opb = ((all_data['intersection_400_u_area']/all_data['roads_buffered_50_area'])*3)+((all_data['intersection_1000_400_u_area']/all_data['roads_buffered_50_area'])*7)+((intersection_out_1000_u_area/all_data['roads_buffered_50_area'])*10)
        all_data['point_for_nearest_opb']=point_for_nearest_opb
    for index, row in all_data.iterrows():
        if row['point_for_open_organisation'] > 7:
            all_data.loc[index, 'point_for_open_organisation'] = 10
        all_data['transport_value'] = ''
    for index, row in all_data.iterrows():
        if row['INT_0-24'] < 200:
            all_data.loc[index, 'transport_value'] = 'низкая'
        elif row['INT_0-24'] > 200 and row['INT_0-24'] < 2000:
            all_data.loc[index, 'transport_value'] = 'ниже среднего'
        elif row['INT_0-24'] > 2000 and row['INT_0-24'] < 6000:
            all_data.loc[index, 'transport_value'] = 'среднее'
        elif row['INT_0-24'] > 6000:
            all_data.loc[index, 'transport_value'] = 'высокое'
        all_data['point_for_noise'] = int
    for index, row in all_data.iterrows():
        if row['L_7-23'] < 70:
            all_data['point_for_noise'] = all_data['L_7-23']/10
        elif row['L_7-23'] > 70:
            all_data.loc[index, 'point_for_noise'] = 10
    for index, row in all_data.iterrows():
        if row['point_for_noise'] > 7:
            all_data.loc[index, 'point_for_noise'] = 10
        all_data['point_for_emission'] = float
    for index, row in all_data.iterrows():
        if row['PM'] < 0.035:
            all_data['point_for_emission'] = all_data['PM']*7/0.035
        elif row['PM'] > 0.035:
            all_data.loc[index, 'point_for_emission'] = 10  
    for index, row in all_data.iterrows():
        if row['point_for_emission'] > 10:
            all_data.loc[index, 'point_for_emission'] = 10
        all_data['sum_of_point'] = all_data['point_for_mixed_used']+all_data['point_for_open_organisation']+all_data['point_for_nearest_opb']+all_data['point_for_noise']+all_data['point_for_emission']
    print(all_data)


# In[62]:


sum_of_point_for_pedestrianisation(all_data)


# In[64]:


all_data = all_data.drop(['INT_8-9', 'LOAD_8-9','INT_18-19','LOAD_18-19','NO2','SO2','NOX','L_6-9','L_16-19','distance','nearest_x','nearest_y','NMHC','CO','HC','FC','CO2_TOTAL','NO2','SO2','NOX'], axis=1)


# In[65]:


all_data

