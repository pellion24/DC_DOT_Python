#imports

import pandas as pd
import requests
import time


#set up intial API call, where we get all our permit coordinates
url = 'https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_APPS/DDOT_TOPS/MapServer/24/query'

names = ['Potomac Electric Power Company', 'Pepco holdings inc', 'DCWATER/OPS', ]

parameters = {
    'where': "EventTypeDescription IN ('Construction Staging Area', 'Mobile Crane Work Zone') AND (OwnerName LIKE '%PEPCO%' OR OwnerName LIKE '%POTOMAC ELECTRIC%' OR OwnerName LIKE '%DCWATER%' OR OwnerName LIKE '%WASHINGTON GAS%') AND ApplicationDate >= DATE '2026-01-01'",
    'outFields': 'PermitNumber,EventTypeDescription,ApplicationDate,OwnerName,XCoord,YCoord',
    'f': 'json'
}

response = requests.get(url, params=parameters)
print(f"\nPermit API Status code:  {response.status_code}")

#take the data from the response and set it to a dataframe
data = response.json()
features = data.get('features', [])
attributes_list = [f['attributes'] for f in features]
df = pd.DataFrame(attributes_list)
print("\nPermit Data frame:\n")
print(df.count())

#Clean duplicate coordinates
other_coords = df[['XCoord', 'YCoord']].drop_duplicates().reset_index(drop=True)
#print(other_coords.count())
unique_coords = df.drop_duplicates(subset=['XCoord', 'YCoord'])
print("\nData Cleaning complete, new counts:\n")
print(unique_coords.count())

#Now set up second api call, where we associate the functional class
#this line does take a while to run
lrs_url = (
    "https://rh.dcgis.dc.gov/dcgis/rest/services/DDOT/RoadwayBlocks/MapServer/exts/DdotLrsExtensions/getPointOnSubBlock"
)

lrs_results = []

input("\nNext step will take around 14 minutes to run, press Enter to continue...")

for index, row in unique_coords.iterrows():

  if index % 100 == 0:
    print(f"Processed {index} rows", flush=True)

  params = {
      "x": row["XCoord"],
      "y": row["YCoord"],
      "inSR": 26985,
      "outSR": 26985,
      "includeSectionEvents": True,
      "returnNearestMatchOnly": True,
      "searchRadius": 15,
      "f": "json",
  }

  try:
    res = requests.get(lrs_url, params=params, timeout=20)
    #print(f"Status:" + str(res.status_code))
    data = res.json()

    sub_blocks = data.get("pointOnSubBlocks", [])
    if sub_blocks:
      road_data = sub_blocks[0].get("roadData", {})
      roadway_Attributes = road_data.get("roadwayAttributes", {})
      other = roadway_Attributes.get("other", {})
      functional_Class = other.get("functionalClass", {})
      route_name = sub_blocks[0].get("routeName")
    else:
      functional_Class = None
      route_name = None

    lrs_results.append({
        "XCoord": row["XCoord"],
        "YCoord": row["YCoord"],
        "FunctionalClass": functional_Class,
        "RouteName": route_name,
    })

  except Exception as e:
    print(f"Error at {row['XCoord']}, {row['YCoord']}: {e}")
    lrs_results.append({
        "XCoord": row["XCoord"],
        "YCoord": row["YCoord"],
        "FunctionalClass": None,
        "RouteName": None,
    })

  time.sleep(0.05)

#Check the results after the above runs
lrs_lookup_df = pd.DataFrame(lrs_results)
print(lrs_lookup_df.count())

#Organize functional class hierarchy, filter out alleys, and export to csv
final_df = pd.merge(df, lrs_lookup_df, on=['XCoord', 'YCoord'], how='left')

class_ranking = {
    'Local': 1,
    'Collector': 2,
    'Minor Arterial': 3,
    'Principal Arterial': 4,
    'Other Freeway and Expressway': 5,
    'Interstate': 6,
}

final_df['Rank'] = final_df['FunctionalClass'].map(class_ranking).fillna(0)

final_df['HighestFunctionalClass'] = final_df.groupby('PermitNumber', group_keys=False)[
    'FunctionalClass'
].transform(
    lambda x: x.loc[final_df.loc[x.index, 'Rank'].idxmax()]
)

final_df = final_df[~final_df['RouteName'].str.contains('Alley', case=False, na=False)].copy()
final_df = final_df.drop_duplicates(subset=['PermitNumber', 'XCoord', 'YCoord'])

output_filename = 'dc_utility_permits_enriched.csv'
final_df.to_csv(output_filename, index=False)

print(f'Workflow complete! Successfully exported to {output_filename}')
print(f'Final dataset shape: {final_df.shape}')
print(final_df[['PermitNumber', 'FunctionalClass', 'HighestFunctionalClass']].head(10))
