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




roads_central_district_with_intensity_and_noise = pd.read_csv('data/roads_central_district_with_intensivity.csv', sep = ";", encoding = 'utf-8')

emissons = pd.read_csv('data/emissions.csv', sep = ";", encoding = 'utf-8')

roads_central_district_with_intensity_and_noise_and_emission = roads_central_district_with_intensity_and_noise.merge(emissons, on='linkId')

roads_central_district_with_intensity_and_noise_and_emission = gpd.GeoDataFrame(roads_central_district_with_intensity_and_noise_and_emission, geometry=roads_central_district_with_intensity_and_noise_and_emission.apply(lambda x: shapely.wkt.loads(x['wkt_geom']),axis = 1))

roads_buffered.geometry= roads_buffered.geometry.buffer(50)

buildings=gpd.read_file('data/building_in_central_district.geojson').to_crs(3857)

buildings=buildings.to_crs(3857)


poi=gpd.read_file('data/activities_in_roads_buffer_30.geojson').to_crs(3857)
work=gpd.read_file('data/work_central.geojson').to_crs(3857)
population=gpd.read_file('data/population_central.geojson').to_crs(3857)



amount_of_population = []
for i in range(len(buildings)):
    s = population.within(buildings['geometry'][i])
    if len(s[s])>0:
        amount_of_population.append(1)
    else:
        amount_of_population.append(0)
print (amount_of_population)


amount_of_work = []
for i in range(len(buildings)):
    s = work.within(buildings['geometry'][i])
    if len(s[s])>0:
        amount_of_work.append(1)
    else:
        amount_of_work.append(0)
print (amount_of_work)


amount_of_poi = []
for i in range(len(buildings)):
    s = poi.within(buildings['geometry'][i])
    if len(s[s])>0:
        amount_of_poi.append(1)
    else:
        amount_of_poi.append(0)
print (amount_of_poi)


buildings['amount_of_work']=amount_of_work
buildings['amount_of_population']=amount_of_population
buildings['amount_of_poi']=amount_of_poi
buildings['sum']=buildings['amount_of_poi']+buildings['amount_of_work']+buildings['amount_of_population']


for index, row in buildings.iterrows():
        if row['sum'] == 3:
            buildings.loc[index, 'sum_of_point'] = 10
        elif row['sum'] == 2 :
            buildings.loc[index, 'sum_of_point'] = 6
        elif row['sum'] == 1 :
            buildings.loc[index, 'sum_of_point'] = 3
        elif row['sum'] == 0:
            buildings.loc[index, 'sum_of_point'] = 0


amount_of_building = []
for i in range(len(roads_buffered)):
    s = buildings.intersects(roads_buffered['geometry'][i])
    if len(s[s])>0:
        a = len([item for item in s if item == True])
        amount_of_building.append(a)
    else:
        amount_of_building.append(0)
print (amount_of_building)


amount_of_point_of_building = []
for i in range(len(roads_buffered)):
    s = buildings.intersects(roads_buffered['geometry'][i])
    s = list(s)
    if len(s)>0:
        selected_building = []
        for i,j in enumerate(s):
            if j is True:
                selected_building.append(i)
        
                acc_sum = 0
        for i in selected_building:
            point = buildings.loc[i, 'sum_of_point']
                        acc_sum+=point
        amount_of_point_of_building.append(acc_sum)
        
    else:
        amount_of_point_of_building.append(0)
print (amount_of_point_of_building)


roads_central_district['amount_of_building']=amount_of_building
roads_central_district['amount_of_point_of_building']=amount_of_point_of_building

roads_central_district['point_for_mixed_used']=roads_central_district['amount_of_point_of_building']/roads_central_district['amount_of_building']

activities=gpd.read_file('data/activities_in_roads_buffer_30.geojson').to_crs(3857)

amount_of_organisation = []
for i in range(len(roads_buffered)):
    s = activities.intersects(roads_buffered['geometry'][i])
    if len(s[s])>0:
        a = len([item for item in s if item == True])
        amount_of_organisation.append(a)
    else:
        amount_of_organisation.append(0)
print (amount_of_organisation)

roads_central_district['amount_of_organisation']=amount_of_organisation

roads_central_district['amount_of_open_organisation']=roads_central_district['amount_of_organisation']/roads_central_district['amount_of_building']

roads_central_district['roads_buffered_50_area']=roads_buffered.area


open_public_places=gpd.read_file('data/open public spaces central district.geojson').to_crs(3857)

open_public_places_buffered_400 = open_public_places.copy()

open_public_places_buffered_400 = open_public_places_buffered_400.buffer(400)

open_public_places_buffered_1000 = open_public_places.copy()

open_public_places_buffered_1000 = open_public_places_buffered_1000.buffer(1000)

open_public_places_buffered_400

from shapely.ops import unary_union
open_public_places_buffered_400_u = unary_union(open_public_places_buffered_400)
open_public_places_buffered_1000_u = unary_union(open_public_places_buffered_1000)

opb_400_u = gpd.GeoDataFrame({'geometry': open_public_places_buffered_400_u})
opb_1000_u = gpd.GeoDataFrame({'geometry': open_public_places_buffered_1000_u})
opb_1000_400_u = gpd.overlay(opb_1000_u,opb_400_u,how='difference')


opb_400_u['id'] = opb_400_u.index
opb_1000_400_u['id'] = opb_1000_400_u.index
roads_buffered['id'] = roads_buffered.index
intersection_400_u = gpd.overlay(roads_buffered, opb_400_u, how='intersection')
intersection_1000_400_u = gpd.overlay(roads_buffered, opb_1000_400_u, how='intersection')
intersection_400_u['intersection_400_u_area']=intersection_400_u.area
intersection_1000_400_u['intersection_1000_400_u_area']=intersection_1000_400_u.area
intersection_400_area = intersection_400_u.groupby('linkId')['intersection_400_u_area'].sum()
intersection_1000_area = intersection_1000_400_u.groupby('linkId')['intersection_1000_400_u_area'].sum()


intersection_400_area=intersection_400_area.to_frame()
intersection_1000_area=intersection_1000_area.to_frame()


roads_central_district_alldata = roads_central_district.copy()

roads_central_district_alldata = roads_central_district_alldata.merge(intersection_400_area, how='left', on='linkId').fillna(0)
roads_central_district_alldata = roads_central_district_alldata.merge(intersection_1000_area, how='left', on='linkId').fillna(0)

roads_central_district_alldata .to_file('roads_central_district_alldata .geojson',driver = 'GeoJSON')

all_data = roads_central_district_alldata.copy()

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


all_data = all_data.drop(['INT_8-9', 'LOAD_8-9','INT_18-19','LOAD_18-19','NO2','SO2','NOX','L_6-9','L_16-19','distance','nearest_x','nearest_y','NMHC','CO','HC','FC','CO2_TOTAL','NO2','SO2','NOX'], axis=1)

