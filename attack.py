from math import sqrt
import utm
from geopy.distance import distance
import googlemaps
from datetime import datetime
import random

# Each call to repeat_in_big_zone() corresponds to an execution of ORide


# As discussed in Section 2.2, analyzing location recovery for 1 driver
# over multiple executions is sufficient
n_drivers = 1
# Width of a lane
road_error = 3.5
gen_road_error = 3
buffer = 0
# Number of experiments
count_repeat_big_expts = 10
# Keep track of number of solutions to x^2+y^2=N
calc_count = 0
calc_count_denominator = 0

# Visit https://developers.google.com/maps/documentation/javascript/get-api-key
# to obtain a Map API key, with Road API and Distance Matrix API enabled
# Due to reasons of confidentiality, we are not 

api_key = 'enter the api key here'
gmaps = googlemaps.Client(key=api_key)

def solutions(n):
	solns = []
	for x in range(0,int(sqrt(n/2))+1):
		y=sqrt(n-x**2)
		if abs(y-int(y)) <= 1e-9:
			#  print('x=',x,'y=', y,'n=',n,'diff=', x**2+y**2 - n)
			y = int(y)
			soln = {(x, y)}
			soln.add((-x, y))
			soln.add((-x, -y))
			soln.add((x, -y))
			soln.add((y, x))
			soln.add((y, -x))
			soln.add((-y, -x))
			soln.add((-y, x))
			for ele in soln:
				solns.append(ele)
	return len(solns), solns


# Uncomment the four lines corresponding to the choice of city
# The following represent "bigger" zones, from which we choose a
# random zone of, say, 2km x 2km

# 30km x 30km Dallas
big_top_left = [32.894183, -96.957494]
big_top_right = [32.894183,-96.636144]
big_bottom_left = [32.622208, -96.957494]
big_bottom_right = [32.622208, -96.636144]

# 30km x 30km Los Angeles
# big_top_left = [34.087291, -118.396671]
# big_top_right = [34.087291,-118.074291]
# big_bottom_left = [33.807044, -118.396671]
# big_bottom_right = [33.807044, -118.074291]

# 30km x 30km london 
# big_top_left = [51.596569, -0.458188]
# big_top_right = [51.596569, -0.024122]
# big_bottom_left = [51.327949, -0.458188]
# big_bottom_right = [51.327949, -0.024122]

# 10km x 10km  new york
# big_top_left = [40.750875, -73.944110]
# big_top_right = [40.750875, -73.823221]
# big_bottom_left = [40.660444, -73.944110]
# big_bottom_right = [40.660444, -73.823221]

# 20km x 20km new york (separated by water)
# big_top_left = [40.846931, -73.937462]
# big_top_right = [40.846931, -73.694036]
# big_bottom_left = [40.666937, -73.937462]
# big_bottom_right = [40.666937, -73.694036]

# Side length (in kms) of bigger zone
big_size = 30

# Side length (in kms) of zone
size = 2

rows = int(big_size / size)
columns = int(big_size / size)


row_width = (big_top_left[0] - big_bottom_left[0]) / rows
column_width = (big_top_right[1] - big_top_left[1]) / columns

total_count_avg_pred = 0
total_count_correct_pred = 0

def repeat_in_big_zone():

    global total_count_avg_pred, total_count_correct_pred, calc_count, calc_count_denominator

    # Choosing a random zone of size "size" inside the bigger zone

    rand_row = random.randint(0, rows-1)
    rand_column = random.randint(0, columns-1)

    top_left = [big_top_left[0] - rand_row * row_width, big_top_left[1] + rand_column * column_width]
    top_right = [top_left[0], top_left[1] + column_width]
    bottom_left = [top_left[0] - row_width, top_left[1]]
    bottom_right = [top_left[0] - row_width, top_right[1]]


    width = (top_right[1] - top_left[1])
    height = (top_left[0] - bottom_left[0])

    def get_random_coord():
        la = top_left[0] - height*random.random()
        lo = top_left[1] + width*random.random()
        return (la, lo)

    def latlon_to_utm(latlon_coord):

        # Example : utm.from_latlon(51.2, 7.5)
        # Output: (395201.3103811303, 5673135.241182375, 32, 'u')
        
        (la, lo) = latlon_coord
        utm_coord = utm.from_latlon(la, lo)
        new_utm_coord = (round(utm_coord[0], 0), round(utm_coord[1], 0), utm_coord[2], utm_coord[3])
        return new_utm_coord

    def utm_to_latlon(utm_coord):
        # Example: utm.to_latlon(340000, 5710000, 32, 'U')
        # Output: (51.51852098408468, 6.693872395145327)
        (a, b, c, d) = utm_coord
        result = utm.to_latlon(a, b, c, d)
        return result

    top_left_utm = latlon_to_utm(top_left)
    top_right_utm = latlon_to_utm(top_right)
    bottom_left_utm = latlon_to_utm(bottom_left)
    bottom_right_utm = latlon_to_utm(bottom_right)

    def euclidean_latlon(coord1, coord2):
        return distance(coord1, coord2).m

    def euclidean_utm(coord1, coord2):
        (x1, y1) = (coord1[0], coord1[1])
        (x2, y2) = (coord2[0], coord2[1])
        return (x1-x2)**2 + (y1-y2)**2

    def is_inside_latlon_box(coord):
        (x, y) = coord
        result = True
        if y <= top_left[1]-buffer:
            result = False
        if y >= top_right[1]+buffer:
            result = False
        if x <= bottom_left[0]-buffer:
            result = False
        if x >= top_left[0]+buffer:
            result = False
        return result

    def is_inside_utm_box(coord):
        (x, y) = coord
        result = True
        if x <= top_left_utm[0]-5:
            result = False
        if x >= top_right_utm[0]+5:
            result = False
        if y <= bottom_left_utm[1]-5:
            result = False
        if y >= top_left_utm[1]+5:
            result = False
        return result

    def get_time(coord1, coord2, val = 1):
        result = gmaps.distance_matrix(coord1, coord2,
                                            mode = 'driving', departure_time = datetime.now(), traffic_model='best_guess')
        return result

    def get_nearest_road(coord):
        if type(coord) == type((1,2)):
            # for calls made inside function get_random_coord_on_road()
            coord = [coord]
        loc_result = gmaps.nearest_roads(coord)
        result = []
        for loc in loc_result:
            if loc['originalIndex'] > len(result):
                m = len(result)
                # sometimes, when there are no nearby roads, API doesn't return anything
                for _ in range(loc['originalIndex'] - m):
                    result.append((90, 0))
            elif loc['originalIndex'] < len(result):
                continue
            point = (loc['location']['latitude'], loc['location']['longitude'])
            result.append(point)
        for _ in range(len(coord) - len(result)):
            result.append((90, 0))
        return result

    def get_random_coord_on_road(error = 0):
        # Getting a random driver location on road
        if error == 0:
            local_gen_road_error = gen_road_error
        else:
            local_gen_road_error = error
        while True:
            a = get_random_coord()
            b = get_nearest_road(a)
            if b == [] or euclidean_latlon(a, b) > local_gen_road_error:
                continue
            break
        return a

    def get_both_random_coord_driver(val = 1):
        coord = get_random_coord_on_road()
        utm_coord = latlon_to_utm(coord)
        if val==0:
            return coord
        return coord, utm_coord

    def get_both_random_coord_rider(val = 1):
        # for 20km new york, uncomment below line and comment the line following it
        # coord = get_random_coord_on_road(300)
        coord = get_random_coord()
        utm_coord = latlon_to_utm(coord)
        if val==0:
            return coord
        return coord, utm_coord

    n_expts = 1
    for i in range(n_expts):
        count_avg_pred = 0
        count_correct_pred = 0
        
        drivers_latlon = []
        drivers_utm = []
        for j in range(n_drivers):
            coord, utm_coord = get_both_random_coord_driver()
            drivers_latlon.append(coord)
            drivers_utm.append(utm_coord)
        
        rider_latlon, rider_utm = get_both_random_coord_rider()
        x_rider = rider_utm[0]
        y_rider = rider_utm[1]
        euclidean_distances = []
        
        for driver_utm in drivers_utm:
            euclidean_distances.append(int(euclidean_utm(rider_utm, driver_utm)))
        predict_drivers_utm = []
        predict_drivers_latlon = []
        
        for j in range(n_drivers):
            count, solns = solutions(euclidean_distances[j])
            calc_count += count
            calc_count_denominator += 1
            if len(solns) == 0:
                predict_drivers_utm.append([])
                predict_drivers_latlon.append([])
                continue
            valid_solns_utm = []
            valid_solns_latlon = []

            for soln in solns:
                (x, y) = soln
                x_driver = x_rider + x
                y_driver = y_rider + y
                point_utm = (x_driver, y_driver, rider_utm[2], rider_utm[3])
                point_latlon = utm_to_latlon(point_utm)
                if is_inside_latlon_box(point_latlon):
                    valid_soln_utm = point_utm
                    valid_soln_latlon = point_latlon
                    valid_solns_utm.append(valid_soln_utm)
                    valid_solns_latlon.append(valid_soln_latlon)
            on_road_valid_solns_latlon = []
            on_road_valid_solns_utm = []

            nearest_road_coords = get_nearest_road(valid_solns_latlon)
            for k in range(len(valid_solns_latlon)):
                dist = euclidean_latlon(valid_solns_latlon[k], nearest_road_coords[k])
                if dist <= road_error:
                    on_road_valid_solns_latlon.append(valid_solns_latlon[k])
                    on_road_valid_solns_utm.append(valid_solns_utm[k])

            predict_drivers_utm.append(on_road_valid_solns_utm)
            predict_drivers_latlon.append(on_road_valid_solns_latlon)

        for j, valid_solns in enumerate(predict_drivers_latlon):
            val = False
            l = len(valid_solns)
            count_avg_pred += l
            if l == 1:
                count_correct_pred += 1
            
            for k in valid_solns:
                if euclidean_latlon(k, drivers_latlon[j]) <= 1.5:
                    val = True

            # Assurance that the actual driver is indeed present among the predicted locations   
            if val == False:
                print('Could not find the actual driver in experiment')
            assert(val == True)
        

        total_count_avg_pred += count_avg_pred
        total_count_correct_pred += count_correct_pred


for big_expt_iterate in range(count_repeat_big_expts):
    print('Experiment ', big_expt_iterate+1, '====================================================')
    repeat_in_big_zone()
    print('Current average predicted driver count', total_count_avg_pred / (big_expt_iterate+1))
    print('Current percent drivers predicted exactly', total_count_correct_pred / (big_expt_iterate+1) * 100, '%')
    
    # Uncomment the following line to print the number of solutions to x^2+y^2=N
    # print('Current intermediate solution count', calc_count / calc_count_denominator)

total_count_avg_pred /= count_repeat_big_expts
total_count_correct_pred /= count_repeat_big_expts

print('Experiments done ====================================================')

print('Total average predicted driver count', total_count_avg_pred)
print('Total percent of times drivers predicted exactly', total_count_correct_pred * 100, '%')

# Uncomment the following line to print the number of solutions to x^2+y^2=N
# print('Total intermediate solution count', calc_count / calc_count_denominator)