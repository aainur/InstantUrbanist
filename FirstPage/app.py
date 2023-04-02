import math
from pymongo import MongoClient
from flask import Flask, render_template, request, jsonify, redirect, url_for
app = Flask(__name__)
#connecting to the dataset
mongo_uri = "mongodb+srv://amanainur7:InstantUrbanist2023@instanturbanist.o5ojcgj.mongodb.net/test"

client = MongoClient(mongo_uri)

# Access your database
db = client["InstantUrbanist"]

# Access a collection and perform operations
addresses_collection = db["Addresses and coordinates of household units in Košice"]
antik_routes_collection = db["Antik routes"]
services_coordinates_collection = db["Coordinates of 23 public and private service types with 5,10,15,20 minute walking"]

addresses = list(addresses_collection.find())
antik_routes = list(antik_routes_collection.find())
services_coordinates = list(services_coordinates_collection.find())

#
# def convert_to_geojson_feature(properties, geometry, feature_type="Point"):
#     feature = {
# "type": "Feature",
# "properties": properties,
# "geometry": {
# "type": feature_type,
# "coordinates": geometry
# }
# }
#     return feature
#

def convert_to_geojson_feature(properties, geometry, feature_type="Point", feature_id=None):
    feature = {
        "type": "Feature",
        "id": feature_id,
        "properties": properties,
        "geometry": {
            "type": feature_type,
            "coordinates": geometry
        }
    }
    return feature


addresses_geojson = {
"type": "FeatureCollection",
"features": []
}
antik_routes_geojson = {
"type": "FeatureCollection",
"features": []
}
services_coordinates_geojson = {
"type": "FeatureCollection",
"features": []
}

# for address in addresses:
#     properties = {
# "street": address["Street name"],
# "house_number": address["House number"],
# # "street_house_number": address["Street and House number"],
# "building_type": address["Building Type"],
# }
#     geometry = [address["x"], address["y"]]
#     feature = convert_to_geojson_feature(properties, geometry)
#     addresses_geojson["features"].append(feature)

for index, address in enumerate(addresses):
       properties = {
           "street": address["Street name"],
           "house_number": address["House number"],
           # "street_house_number": address["Street and House number"],
           "building_type": address["Building Type"],
       }
       geometry = [address["x"], address["y"]]
       feature = convert_to_geojson_feature(properties, geometry, feature_id=index)
       addresses_geojson["features"].append(feature)


for route in antik_routes:
    properties = {
    "year": route.get("Year"),
    "vehicle_type": route["Vehicle Type"],
    "length": route["length"],
}
    geometry = route.get("geometry")
    feature = convert_to_geojson_feature(properties, geometry, "LineString")
    antik_routes_geojson["features"].append(feature)

for service in services_coordinates:
    properties = {
    "name": service["Name"],
    "type_0": service["Typ_0"],
    "type_1": service["Typ_1"],
    }
    geometry = [service["x"], service["y"]]
    feature = convert_to_geojson_feature(properties, geometry)
    services_coordinates_geojson["features"].append(feature)






# calculation of the distance between two points with their latitude and longitude, using the Haversine formula:
# def haversine_distance(lat1, lon1, lat2, lon2):
#     R = 6371 # radius of Earth in kilometers
#
# # Convert latitudes to radians
#     lat1 = math.radians(lat1)
#     lat2 = math.radians(lat2)
#
# # Calculate differences
#     delta_lat = lat2 - lat1
#     delta_lon = math.radians(lon2 - lon1)
#
#     a = math.sin(delta_lat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon/2)**2
#     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
#
#     distance = R * c
#     return distance
#
#
# # function that finds all locations within a specified radius, given a specific point's coordinates:
# def find_locations_within_radius(lat, lon, radius):
#     locations = db.your_locations_collection
#     nearby_locations = []
#
#     for location in locations.find():
#         lat2 = location['latitude']
#         lon2 = location['longitude']
#         distance = haversine_distance(lat, lon, lat2, lon2)
#
#     if distance <= radius: # Check if the location is within the specified radius
#         nearby_locations.append(location)
#
#     return nearby_locations
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # radius of Earth in kilometers

    # Convert latitudes to radians
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    # Calculate differences
    delta_lat = lat2 - lat1
    delta_lon = math.radians(lon2 - lon1)

    a = math.sin(delta_lat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    distance = R * c
    return distance

point1 = {'x': 21.2240771, 'y': 48.7077919}  # example point 1
point2 = {'x': 21.2259599, 'y': 48.7082246}  # example point 2

distance = haversine_distance(point1['x'], point1['y'], point2['x'], point2['y'])
print(f"Distance between the points: {distance} km")



# # Assume that you have an array of [x, y] coordinates for each point
# # which can be generated from your existing data like below
# coords = np.array([[address["x"], address["y"]] for address in addresses])
#
# # Determine the best k value or test different k values
# best_k = 5
#
# # Fit the model to your coordinates data
# kmeans = KMeans(n_clusters=best_k, random_state=0).fit(coords)
#
# # To access the k centroids (service points) that minimize the distance to all points
# centroids = kmeans.cluster_centers_


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/map', methods=['GET', 'POST'])
def map():
    if request.method == 'POST':
        return render_template(
        "map.html",
        addresses_geojson=addresses_geojson,
        antik_routes_geojson=antik_routes_geojson,
        services_coordinates_geojson=services_coordinates_geojson
)
    else:
        return redirect(url_for('index.html'))

# @app.route('/locations/nearby/<float:lat>/<float:lon>/<float:radius>', methods=['GET'])
# def get_nearby_locations(lat, lon, radius):
#     nearby_locations = find_locations_within_radius(lat, lon, radius)
#     return jsonify(nearby_locations)


if __name__ == '__main__':
    app.run(debug=True)