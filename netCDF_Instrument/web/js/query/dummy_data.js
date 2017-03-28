//This is the object to represent the station data
var station = function(lat_lon, station_id, type)
{
	var new_station = {}
	new_station.lat = lat_lon[0];
	new_station.lon = lat_lon[1];
	new_station.station_id = station_id;
	new_station.type = type;
	
	return new_station;
}

//This is a list of latitude and longitudes
//corresponding to static files
lat_long_list_ny = [
		[40.579200744462896,-74.07520294189453],
		[40.70109939575195,-74.0156021118164],
		[40.79249572753906,-73.82828521728516],
		[40.9005012512207,-73.35299682617188],
		[41.01546859741211,-72.56101989746094],
		[40.65813980102539,-74.23070678710938],
		[40.80109939575195,-74.0156021118164],
		[40.89249572753906,-73.92828521728516],
		[41.0005012512207,-73.45299682617188],
		[41.11546859741211,-72.66101989746094],
//		[43.80109939575195,-70.0156021118164],
//		[45.89249572753906,-78.92828521728516],
//		[49.0005012512207,-71.45299682617188],
//		[50.11546859741211,-72.66101989746094]
]

lat_long_list_nc = [
       [35.3472862243652,-75.5009536743164],
       [35.3472862243652,-75.5009536743164],
       [35.7675476074219,-75.5259246826172],
       [35.7675476074219,-75.5259246826172],
       [35.6846961975098,-75.4838562011719],
       [35.6846961975098,-75.4838562011719],
       [35.5850639343262,-75.4614105224609],
       [35.5850639343262,-75.4614105224609],
       [35.2662124633789,-75.5193557739258],
       [35.2662124633789,-75.5193557739258]
]

var station_list_ny = [];
var station_list_nc = [];
var sea = true;
var station_type = 'sea';
var sea_index = 0
var air_index = 0

//allocate stations by lat lon pairs and switching from sea file to air file type
for (var i = 0; i < lat_long_list_ny.length; i++)
{
	index = Math.floor(i/2) % (lat_long_list_ny.length/2)
	station_list_ny.push(station(lat_long_list_ny[i], index, station_type));
	sea = !sea;
	station_type = sea == true ? 'sea' : 'air';
}

for (var i = 0; i < lat_long_list_nc.length; i++)
{
	index = Math.floor(i/2) % (lat_long_list_nc.length/2)
	station_list_nc.push(station(lat_long_list_nc[i], index, station_type));
	sea = !sea;
	station_type = sea == true ? 'sea' : 'air';
}

var get_data = function(type)
{
	if (type == "ny"){
		return station_list_ny;
	}else{
		return station_list_nc;
	}
}