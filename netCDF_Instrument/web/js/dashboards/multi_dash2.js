
$(function() {
	
	$.getScript( "./js/query/query_thredds.js", 
			function() {
			$.getScript( "./js/query/dummy_data.js")  
			.then(function(){
		
				var bounds = map.getBounds();
				
				stations = query_server([bounds._southWest['lat'],bounds._northEast['lat']], 
				    	[bounds._northEast['lng'],bounds._southWest['lng']])
					
				apply_markers(map,stations);
			});
		});
	
	$.getScript( "./js/aesthetic/graphs.js" )
	  .done(function( script, textStatus ) {
	    console.log( 'success',textStatus );
	  })
	  .fail(function( jqxhr, settings, exception ) {
	    console.log('graph fail')
	});
	
	$.getScript( "./js/aesthetic/wind_graph.js" )
	  .done(function( script, textStatus ) {
	    console.log( 'success',textStatus );
	  })
	  .fail(function( jqxhr, settings, exception ) {
	    console.log('graph fail')
	});
	
	window_width = $(window).width();  
	$('#pair_bar').css('left', (window_width - 52) + 'px');
	
	var expand = false;
	var expanding = false;
	
	$('#pair_label').click(function(){
		if (expanding == false)
		{
			expanding = true;
			if (expand == false)
			{
				$('#layers_label').fadeToggle();
				$('#layers').hide();
				
				$('#pair_bar').animate({
					left: "-=267"
				}, 1000, function(){
					expanding = false;
					expand = !expand;
				});
			}
			else
			{
				$('#layers_label').fadeToggle();
				
				
				$('#pair_bar').animate({
					left: "+=267"
				}, 1000, function(){
					expanding = false;
					expand = !expand;
					$('#layers').show();
				});
			}
		}
	})
	
	$('#layers_label').click(function(){
		if (expanding == false)
		{
			expanding = true;
			if (expand == false)
			{
				$('#pair_label').fadeToggle(function(){
					$('#layers_label').css({'margin-top': '0px'});
				});
				$('#pairs').hide();
				
				$('#pair_bar').animate({
					left: "-=267"
				}, 1000, function(){
					expanding = false;
					expand = !expand;
				});
			}
			else
			{
				$('#pair_label').fadeToggle();
				
				
				$('#layers_label').css({'margin-top': '-25px'})
				
				$('#pair_bar').animate({
					left: "+=267"
				}, 1000, function(){
					expanding = false;
					expand = !expand;
					$('#pairs').show();
				});
			}
		}
	})
	
	$( window ).resize(function() {
		window_width = $(window).width();  
		if (expand == false)
		{
			$('#pair_bar').css('left', (window_width - 52) + 'px');
		}
		else
		{
			$('#pair_bar').css('left', (window_width - 319) + 'px');
		}
	 
	});
	
	var markers = [];
	var stations = null;
	var paths = [];
	  
	var map = L.map('multi_map').setView([40.900501251, -73.352996826], 9);
	
	
	
	L.esri.basemapLayer("NationalGeographic").addTo(map);
//	L.tileLayer.wms("http://idpgis.ncep.noaa.gov/arcgis/services/NOAA/NOAA_Estuarine_Bathymetry/MapServer/WMSServer?", {
//	    layers: '1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,'
//	    	+ '30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,'
//	    	+ '60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,'
//	    	+ '92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,'
//	    	+ '118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,'
//	    	+ '142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,'
//	    	+ '166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,'
//	    	+ '190,191,192,193,194,195,196,197,198,199,200,201,203,202,204,',
//	    	format: 'image/png',
//	        transparent: true,})
//	.addTo(map)
//	
//	$.getJSON('./data/east.geojson', function (data) {
//		
//		
//		var myStyle = {
//			    "color": "#0085ff",
//			    "weight": 1,
//			    "opacity": 0.99
//			};
//		
//		layer = L.geoJSON(data, {style: myStyle}).addTo(map);
//		
//	});
	
	
	
	
	
	//need to get query thredds script because the encased methods
	//will run before it is loaded
	
	var sea_index = 1;
	var air_index = 1;

	var apply_markers = function(map, data)
	{
		if(markers.length > 0)
		{
			clear_markers(map);
		}
	
		sea_index = 1;
		air_index = 1;
		
		//add markers for each data entry from server
		for (var i = 0; i < data.length; i++)
		{
			//get lat lon
			myLatLng = {lat: data[i].lat, lng: data[i].lon};
			
			icon =  './images/sea.png'
				
			//initialize with sea pressure station options
			type= 'sea';
			index = sea_index;
			color_index = -1;
			
			var icon_type = 'sea'
			if (data[i].type == 'air')
			{
				icon_type = 'air'
				for (var j = 0; j < color_air.length; j++)
				{
					if (data[i].station_id == color_air[j])
					{
						color_index = j;
						break;
					}
				}
				//swap for air pressure station options
				type = 'air'
					
				if(color_index != -1)
				{
					icon = 'air_' + colors[color_index];
				}
				else
				{
					icon = 'air'
				}
				
				index = air_index;
				air_index++;
			}
			else
			{
				for (var j = 0; j < color_sea.length; j++)
				{
					if (data[i].station_id == color_sea[j])
					{
						color_index = j;
						break;
					}
				}
				
				if(color_index != -1)
				{
					icon = 'sea_' + colors[color_index];
				}
				else
				{
					icon = 'sea'
				}
				
				sea_index++;
			}
			
			var myIcon = L.divIcon({
				className: 'my-div-icon',
				iconAnchor: L.point(20, 20),
				html: '<span class="' + icon + ' ' + icon_type + 'icon">' + index + '</span>'
				});
			
			marker = L.marker([data[i].lat, data[i].lon], {icon: myIcon})
			.addTo(map);
			
			//set the marker properties
			marker.toggle_state = 1;
			marker.toggle_index = index;
			marker.instrument_type = data[i].type;
			marker.station_id = data[i].station_id;
			marker.icon = icon;
			
			markers.push(marker);
		}
		
		var myIcon = L.divIcon({
			className: 'my-div-icon',
			iconAnchor: L.point(20, 20),
			html: '<span class="windicon">W</span>'
			});
		
		var marker = L.marker([40.6433333, -73.2633333], {icon: myIcon})
		.addTo(map);
	}
	
	var check_exists = function(sea_id, air_id)
	{
		for (var i = 0; i < paths.length; i++)
		{
			if (paths[i].sea_id == sea_id && paths[i].air_id == air_id)
			{
				return true;
			}
		}
		return false;
	}
	
	var apply_paths = function(map)
	{
		if (paths.length > 0)
		{
			clear_paths(map);
		}
		
		for(var i = 0; i < pairs.length; i++)
		{
			if(pairs[i] != null)
			{
				if(check_exists(pairs[i].sea_id, pairs[i].air_id) == false)
				{
					lat_lng1 = get_marker('sea', pairs[i].sea_id).getLatLng();
					lat_lng2 = get_marker('air', pairs[i].air_id).getLatLng();
					temp_path = L.polyline( [lat_lng1,lat_lng2], {
						color: colors[pairs[i].color],
						weight: 5
					} ).addTo(map);
					
					temp_path.sea_id = pairs[i].sea_id;
					temp_path.air_id = pairs[i].air_id;
					
					paths.push(temp_path);
				};
			}
		}
	}
	
	var clear_markers = function(map)
	{
		for (var i = 0; i < markers.length; i++)
		{
			map.removeLayer(markers[i]);
		}
		markers = []
	}
	
	var clear_paths = function(map)
	{
		for (var i = 0; i < paths.length; i++)
		{
			map.removeLayer(paths[i]);
		}
		paths = []
	}
	
	var update_pair_dropdowns = function()
	{
		$('.sea_pair').each(function(){
			
			var current_val = parseInt($(this).val());
			var html = '';
			$(this).empty();
			
			for(var i = 0; i < sea_index - 1; i++)
			{
				if(i == current_val)
				{
					html = html + '<option selected value="' + markers[2*i].station_id + '">' + (i+1) + '</option>'
				}
				else
				{
					html = html + '<option value="' + markers[2*i].station_id + '">' + (i+1) + '</option>'
				}
			}
					
			$(this).append(html)
			$(this).trigger('change');
		})
		
		$('.air_pair').each(function(){
			
			var current_val = parseInt($(this).val());
			var html = '';
			$(this).empty();
			for(var i = 0; i < air_index - 1; i++)
			{
				if(i == current_val)
				{
					html = html + '<option selected value="' + markers[2*i+1].station_id + '">' + (i+1) + '</option>'
				}
				else
				{
					html = html + '<option value="' + markers[2*i+1].station_id + '">' + (i+1) + '</option>'
				}
			}
				
			$(this).append(html);	
			$(this).trigger('change');
		})
	}
	
	$('#start_date').datetimepicker();
	$('#end_date').datetimepicker();
	
	//store dash objects
	var dash_objects = [];
	
	var pairs = [];
	var state_data = null;
	var colors = ['red','green','blue','purple','orange'];
	var color_pair = [-1,-1,-1,-1,-1]
	var color_sea = [-1,-1,-1,-1,-1]
	var color_air = [-1,-1,-1,-1,-1]
	
	var make_dash = function(id, contentId, contentType, method, color, legendLabel,
			title, xlabel, ylabel)
	{
		return {
			"id": id,
			"contentId": contentId,
			"contentType": contentType,
			"contentCreated": false,
			"expanded": false,
			"method": method,
			"color": color,
			"legendLabel": legendLabel,
			"title": title,
			"xlabel": xlabel,
			"ylabel": ylabel
		}
	}
	
	var make_pair = function(pair_id, sea_id, air_id, color_index, station_id)
	{
		return {
			"pair_id": pair_id,
			"sea_id": sea_id,
			"air_id": air_id,
			"color": color_index,
		}
	}
	
	var make_path = function(sea_id, air_id)
	{
		return{
			"sea_id" : sea_id,
			"air_id" : air_id
		}
	}
	
	var get_marker = function(type, id)
	{
		for (var i = 0; i < markers.length; i++)
		{
			if(markers[i].instrument_type == type && markers[i].station_id == id)
			{
				return markers[i];
			}
		}
	}
	
	var add_pair = function(pair_id, sea_id, air_id, color_index, station_id)
	{
		pairs.push(make_pair(pair_id, sea_id, air_id, color_index, station_id));
	}
	
	//function for changing the instrument for an added pair
	var change_pair = function (pair_id, sea_air, value)
	{
		for (var i = 0; i < pairs.length; i++)
		{
			if (pairs[i] != null && pair_id == pairs[i].pair_id)
			{
				if (sea_air == "sea")
				{
					pairs[i].sea_id = value;
				}
				else
				{
					pairs[i].air_id = value;
				}
			}
		}
	}
	
	var remove_pair = function(pair_id)
	{
		for (var i = 0; i < pairs.length; i++)
		{
			if (pairs[i] != null && pair_id == pairs[i].pair_id)
			{
				pairs[i] = null;
			}
		}
	}
	
	var find_dash = function(id, data)
	{
		for (var i = 0; i < dash_objects.length; i++)
		{
			if (dash_objects[i].id == id)
			{
				update_content(dash_objects[i], data, true)
			}
		}
	}
	
	var update_content = function(dash_object, data, change)
	{
		switch(dash_object.contentType)
		{
		
		case "water_level_graph":
			
			//Get the appropriate graph data
			var graph_data = []
			var path_data = []
			switch(dash_object.method)
			{
			case "Unfiltered":
				for (var i = 0; i < data.length; i ++)
				{
					graph_data.push(data[i]['raw_data']);
					path_data.push(data[i]['sea_stn'][0].toString() + '' + data[i]['air_stn'][0].toString());
				}
				break;
			case "Surge":
				for (var i = 0; i < data.length; i ++)
				{
					graph_data.push(data[i]['surge_data']);
					path_data.push(data[i]['sea_stn'][0].toString() + '' + data[i]['air_stn'][0].toString());
				}
				break;
			case "Wave":
				for (var i = 0; i < data.length; i ++)
				{
					graph_data.push(data[i]['wave_data']);
					path_data.push(data[i]['sea_stn'][0].toString() + '' + data[i]['air_stn'][0].toString());
				}
				break;
			case "Air":
				for (var i = 0; i < data.length; i ++)
				{
					graph_data.push(data[i]['air_data']);
					path_data.push(data[i]['sea_stn'][0].toString() + '' + data[i]['air_stn'][0].toString());
				}
				break;
			}
			
			//If content not created, create, otherwise update
			if (dash_object.contentCreated == false)
				{
					dash_object.state_index = makeMultiGraph(graph_data,dash_object,colors, true, path_data);
					dash_object.contentCreated = true;
				}
			else
				{
				//If dash tile is expanded, change width and height, otherwise just update
				 if (change == true)
					 {
						if (dash_object.expanded == false)
						{
							console.log('about to expand');
							$('#' + dash_object.contentId).attr('width', '960px');
							$('#' + dash_object.contentId).attr('height', '640px');
							updateMultiGraph(graph_data,dash_object,dash_object.color,960,640,true,!dash_object.expanded,path_data);
							dash_object.expanded = true;
						}
						else if ( dash_object.expanded == true)
						{
							console.log('about to shrink');
							$('#' + dash_object.contentId).attr('width', '440px');
							$('#' + dash_object.contentId).attr('height', '440px');
							updateMultiGraph(graph_data,dash_object,dash_object.color,440,440,true,!dash_object.expanded,path_data);
							dash_object.expanded = false;
						}
					 }
				 else
					 {
					 	var width = parseInt($('#' + dash_object.contentId).attr('width').substring(0,3));
					 	var height = parseInt($('#' + dash_object.contentId).attr('height').substring(0,3));
					 	updateMultiGraph(graph_data,dash_object,dash_object.color,width,height,true,dash_object.expanded,path_data);
					 }
				}
			break;
			case "wind":
			
			//Get the appropriate graph data
			var graph_data = data;
			
			
			//If content not created, create, otherwise update
			if (dash_object.contentCreated == false)
				{
					makeWindGraph(graph_data,dash_object);
					dash_object.contentCreated = true;
				}
			else
				{
				//If dash tile is expanded, change width and height, otherwise just update
				 if (change == true)
					 {
						if (change == true && dash_object.expanded == false)
						{
							$('#' + dash_object.contentId).attr('width', '960px');
							$('#' + dash_object.contentId).attr('height', '640px');
							updateWindGraph(graph_data,dash_object,960,640,true);
							dash_object.expanded = true;
						}
						else if (change == true && dash_object.expanded == true)
						{
							$('#' + dash_object.contentId).attr('width', '440px');
							$('#' + dash_object.contentId).attr('height', '440px');
							updateWindGraph(graph_data,dash_object,440,440, false);
							dash_object.expanded = false;
						}
					 }
				 else
					 {
					 	var width = parseInt($('#' + dash_object.contentId).attr('width').substring(0,3));
					 	var height = parseInt($('#' + dash_object.contentId).attr('height').substring(0,3));
					 	updateWindGraph(graph_data,dash_object,width,height,dash_object.expanded);
					 }
				}
			break;
		}
		hide_load();
	}
	
	$('.expand').click(function(){
		
		var elem = $(this)
		elem.attr('disabled','disabled');
		var width = parseInt($(this).parent().parent().css('width'));
		var id = $(this).parent().parent().prop('id');
		
		var graph_data = [];
		var count = 0;
		
		if (width < 900)
		{
			var height = $('#sidebar').css('height');
			$('#sidebar').css('height', parseInt(height.substring(0,height.length - 2)) + 600);
			var height2 = $('#mainGraph').css('height');
			$('#mainGraph').css('height', parseInt(height.substring(0,height.length - 2)) + 600);
			
			elem.parent().parent().animate({
			    height: "680px",
			    width: "960px"
			  }, 500, function() {
				
			    elem.text('Shrink');
			    find_dash(id, state_data);
			    elem.removeAttr('disabled');
			  });
		}
		else{
			
			var height = $('#sidebar').css('height');
			$('#sidebar').css('height', parseInt(height.substring(0,height.length - 2)) - 600);
			var height2 = $('#mainGraph').css('height');
			$('#mainGraph').css('height', parseInt(height.substring(0,height.length - 2)) - 600);
			
			elem.parent().parent().animate({
			    height: "460px",
			    width: "470px"
			  }, 500, function() {
				
			    elem.text('Expand');
			    find_dash(id, state_data);
			    elem.removeAttr('disabled');
			  });
		}
	
	});
	
	$('.wind_expand').click(function(){
		
		var elem = $(this)
		elem.attr('disabled','disabled');
		var width = parseInt($(this).parent().parent().css('width'));
		var id = $(this).parent().parent().prop('id');
		
		var graph_data = [];
		var count = 0;
		
		if (width < 900)
		{
			var height = $('#sidebar').css('height');
			$('#sidebar').css('height', parseInt(height.substring(0,height.length - 2)) + 600);
			var height2 = $('#mainGraph').css('height');
			$('#mainGraph').css('height', parseInt(height.substring(0,height.length - 2)) + 600);
			
			elem.parent().parent().animate({
			    height: "680px",
			    width: "960px"
			  }, 500, function() {
				
			    elem.text('Shrink');
			    find_dash(id, wind_data);
			    elem.removeAttr('disabled');
			  });
		}
		else{
			
			var height = $('#sidebar').css('height');
			$('#sidebar').css('height', parseInt(height.substring(0,height.length - 2)) - 600);
			var height2 = $('#mainGraph').css('height');
			$('#mainGraph').css('height', parseInt(height.substring(0,height.length - 2)) - 600);
			
			elem.parent().parent().animate({
			    height: "460px",
			    width: "470px"
			  }, 500, function() {
				
			    elem.text('Expand');
			    find_dash(id, wind_data);
			    elem.removeAttr('disabled');
			  });
		}
	
	});
	
	var final_data = []
	var count = 0;
	var current_pairs = null;
	var current_colors = null;
	
	$('#graphForm').on('submit', function(event){
		event.preventDefault();
		
		show_load();
		current_pairs = [];
		current_colors = [];
		for (var i = 0; i < pairs.length; i++)
		{
			if (pairs[i] != null)
			{
				final_data.push(null);
				current_pairs.push(pairs[i]);
				current_colors.push(colors[pairs[i].color]);
				console.log('color ' + colors[pairs[i].color]);
			}
		}
		
		final_data = []
		count = 0;
		
		for(var i = 0; i < current_pairs.length; i++)
		{
			ajax_post(current_pairs[i], 0, i)
		}
		wind_ajax_post(0);
	})
	
	var ajax_post = function(pairs, post_errors, order)
	{
		if (post_errors < 5)
		{
			$.ajax({
				type: 'POST',
				url: 'http://localhost:8080/single',
				data: {
					start_time: $('#start_date').val(),
					end_time: $('#end_date').val(),
					daylight_savings: $('#dst').val(),
					timezone: $('#timezone').val(),
					sea_file: pairs.sea_id,
					baro_file: pairs.air_id,
					multi: 'True'
				},
				datatype: 'JSON',
				error: function()
				{
					console.log('error');
					ajax_post(pairs, post_errors + 1, order);
				}
			})
			.done(function(data) {
				console.log('success');
				final_data[order] = data
				state_data = final_data;
				count++;
				
				if (count >= current_pairs.length)
				{
					count = 0;
					for (var i = 0; i < dash_objects.length; i++){
						if (i != 4)
						{
							dash_objects[i].color = current_colors;
							update_content(dash_objects[i],final_data, false);
						}
					}		
				}
			});
		}
	}
	
	var wind_ajax_post = function(wind_post_errors)
	{
		if (wind_post_errors < 5)
		{
			$.ajax({
				type: 'POST',
				url: 'http://localhost:8080/wind',
				data: {
					start_time: $('#start_date').val(),
					end_time: $('#end_date').val(),
					daylight_savings: $('#dst').val(),
					timezone: $('#timezone').val(),
					sea_file: 4,
					baro_file: 4,
				},
				datatype: 'JSON',
				error: function()
				{
					console.log('try again');
					wind_ajax_post(wind_post_errors + 1);
				}
			})
			.done(function(data) {
				
				wind_data = data;
				update_content(dash_objects[4],data, false);
				
			});
		}
		else
		{
			console.log('error');
		}
	}

	
	var pair_index = 0;
	var pair_count = 0;
	var pairs = [];
	
	$('#add_pair').click(function(){
		
		if (pair_count < 5)
		{
			//assign the first available color and get the color index
			var color_index = -1;
			for(var i = 0; i < color_pair.length; i++)
			{
				if(color_pair[i] == -1)
				{
					color_pair[i] = pair_index;
					color_index = i;
					break;
				}
			}
			
			//if the sea color is not assigned, assign station id
			if(color_sea[color_index] == -1)
			{
				color_sea[color_index] = markers[0].station_id;
			}
			
			//if the air color is not assigned, assign station id
			if(color_air[color_index] == -1)
			{
				color_air[color_index] = markers[1].station_id;
			}
			
			//add pair to the store
			add_pair(pair_index, markers[0].station_id, markers[1].station_id, color_index);
			
			//apply paths based on pairs
			apply_paths(map);
			
			//apply new colors to markers
			apply_markers(map, stations);
			
			//add the html
			var html = '<tr class="pair_data' + pair_index + ' first"><td colspan="4"><b><u>Stations</u></b></td></tr>'
			html = html + '<tr class="pair_data' + pair_index + '">'
			html = html + '<td>Sea Station</td><td><select class="sea_pair ' + pair_index + '">';
			for (var i = 0; i < sea_index-1; i++)
			{
				html = html + '<option value="' + markers[i*2].station_id + '">' + (i+1) + '</option>'
			}
			html = html + '</select></td><td>Air Station</td><td><select class="air_pair ' + pair_index + '">'
			for (var i = 0; i < air_index-1; i++)
			{
				html = html + '<option value="' + markers[i*2+1].station_id + '">' + (i+1) + '</option>'
			}
			html = html + '</select></td></tr>'
			html = html + '<tr class="pair_data' + pair_index + '"><td>Sea <img style="height: 10px; width: 10px" src="./images/sea_' + colors[color_index] + '.png"/></td>'
			html = html + '<td>Air <img style="height: 10px; width: 10px" src="./images/sea_' + colors[color_index] + '.png"/></td>'
			html = html + '<td>Graph <img style="height: 10px; width: 10px" src="./images/sea_' + colors[color_index] + '.png"/></td></tr>'
			html = html + '<tr class="pair_data' + pair_index + '"><td><b><u>Details</u></b></td></tr>'
			html = html + '<tr class="pair_data' + pair_index + '">'
			html = html + '<td><a class="data_link" href="http://localhost:8080/single_data?s=0&b=0">Single</a></td>'
			html = html + '<td><a class="data_link" href="http://localhost:8080/stat_data?s=0&b=0">Statistics</a></td>'
			html = html + '<td></td><td style="text-align:right">'
			html = html + '<a class="data_link" href="http://localhost:8080/spectra_data?s=0&b=0">Spectra</a></td>'
			html = html + '</tr><tr class="pair_data' + pair_index + ' last"><td colspan="4" style="text-align:right">'
			html = html + '<button id="'+ pair_index + '" class="remove_pair">Remove</button></td></tr>';
				
			$('#pairs').append(html);
			
			
			pair_index++;
			pair_count++;
		}
	});
	
	var last_sea = null;
	$('body').on('change', '.sea_pair', function(){
		
		selector_class = $(this).attr('class').split(' ')[1];
		var val = $(this).val();
		last_sea = val;
		
		$('.pair_data' + selector_class).find('.data_link').each(function(){
			var href1 = $(this).attr('href').split('?');
			var href2 = href1[1].split('&')[1];
			var final_href = href1[0] + '?s=' + val + '&' + href2;
			$(this).attr('href', final_href);
		})
		
		index = -1;
		for(var i = 0; i < color_pair.length; i++)
		{
			if (color_pair[i] == selector_class)
			{
				index = i;
			}
		}
		
		//Set up
		if (color_sea[index] != -1)
		{
			color_sea[index] = val;
		}
		
		change_pair(selector_class, "sea", val);
		
		apply_paths(map);
		apply_markers(map, stations);
	})
	
	var last_air = null;
	$('body').on('change', '.air_pair', function(){
		selector_class = $(this).attr('class').split(' ')[1];
		var val = $(this).val();
		
		$('.pair_data' + selector_class).find('.data_link').each(function(){
			var href = $(this).attr('href').split('&');
			var final_href = href[0] + '&b=' + val
			$(this).attr('href', final_href);
		})
		
		index = -1;
		for(var i = 0; i < color_pair.length; i++)
		{
			if (color_pair[i] == selector_class)
			{
				index = i;
			}
		}
		
		//Set up
		if (color_air[index] != -1)
		{
			color_air[index] = val;
		}
		
		change_pair(selector_class, "air", val);
		
		apply_paths(map);
		apply_markers(map, stations);
	})
	
	$('body').on('click', '.remove_pair', function(){
		var button_class = $(this).attr('id');
		
		console.log('removing pair ' + button_class);
		remove_pair(button_class);
		
		color_index = -1;
		for(var i = 0; i < color_pair.length; i++)
		{
			if (color_pair[i] == button_class)
			{
				color_index = i;
				color_pair[i] = -1;
				break;
			}
		}
		
		$('.pair_data'+ button_class).remove();
		
		
		color_sea[color_index] = -1;
		color_air[color_index] = -1;
		
		apply_markers(map, stations);
		pair_count--;
	})
	
	var dash1 = make_dash('multi_raw','visualization1','water_level_graph','Unfiltered',null,
			["","","","",""],
			"Raw Water Level","Time in GMT","Water Level in Feet");
	var dash2 = make_dash('multi_surge','visualization2','water_level_graph','Surge',null,
			["","","","",""],
			"Surge Water Level","Time in GMT","Water Level in Feet");
	var dash3 = make_dash('multi_wave','visualization3','water_level_graph','Wave',null,
			["","","","",""],
			"Wave Water Level","Time in GMT","Water Level in Feet");
	var dash4 = make_dash('multi_baro','visualization4','water_level_graph','Air',null,
			["","","","",""],
			"Atmospheric Pressure","Time in GMT","Pressure in Inches of Hg");
	var dash5 = make_dash('wind','visualization5','wind','Air','blue',
			["","","","",""],
			"Wind Speed and Direction","Time in GMT","");
	
	dash_objects.push(dash1);
	dash_objects.push(dash2);
	dash_objects.push(dash3);
	dash_objects.push(dash4);
	dash_objects.push(dash5);
	
	$('button').removeAttr('disabled');
	
	var hide_load = function() { $('#slideLoad').slideUp(); }
	var show_load = function() { $('#slideLoad').slideDown(); }
	
	//----------------------------Initialize the map and markers for each station----------////

});