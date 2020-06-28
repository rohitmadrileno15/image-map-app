
import geopy.distance

def geo_data_of_distance(current_lat , current_long , want_lat , want_long):


    coords_1 = (current_lat , current_long )
    coords_2 = (want_lat , want_long)

    distance =  (geopy.distance.vincenty(coords_1, coords_2).km)

    return distance
