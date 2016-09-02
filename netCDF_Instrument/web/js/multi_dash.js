
$(function() {
	
	$.getScript( "./js/graphs.js" )
	  .done(function( script, textStatus ) {
	    console.log( 'success',textStatus );
	  })
	  .fail(function( jqxhr, settings, exception ) {
	    console.log('fail')
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
				$('#pair_bar').animate({
					left: "-=267"
				}, 1000, function(){
					expanding = false;
					expand = !expand;
				});
			}
			else
			{
				$('#pair_bar').animate({
					left: "+=267"
				}, 1000, function(){
					expanding = false;
					expand = !expand;
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
	var map = null;
	var stations = null;
	
	$.getScript( "https://maps.googleapis.com/maps/api/js?key=AIzaSyBKbkdjgPWlg8vSn-yDSHCp3ucmcm93bAQ" )
	  .done(function( script, textStatus ) {
		  
		myLatLng = {lat: 40.900501251, lng: -73.352996826};
		map = new google.maps.Map(document.getElementById('multi_map'), {
			  center: myLatLng,
			  zoom: 9
		});
		
		map.addListener('dragend', function(event) {
			//query for available data within lat/lon bounds of map
			bounds = map.getBounds();
			stations = query_server([bounds.f.f,bounds.f.b], [bounds.b.f,bounds.b.b]);
			apply_markers(map, stations);
			update_pair_dropdowns();
		});
		
		map.addListener('zoom_changed', function(event) {
			//query for available data within lat/lon bounds of map
			bounds = map.getBounds();
			stations = query_server([bounds.f.f,bounds.f.b], [bounds.b.f,bounds.b.b]);
			apply_markers(map, stations);
			update_pair_dropdowns();
		});
		
		//need to get query thredds script because the encased methods
		//will run before it is loaded
		$.getScript( "./js/query_thredds.js" )
		  .done(function( script, textStatus ) {
			//This portion is only run onceconsole.log('success qthredds');
			
			setTimeout( function(){
				var bounds = map.getBounds();
				
				stations = query_server([bounds.f.f,bounds.f.b], [bounds.b.f,bounds.b.b]);
				apply_markers(map, stations);
			}, 1500);
		  })
		  .fail(function( jqxhr, settings, exception ) {
		    console.log('fail qthredds')
		});
		
	  })
	  .fail(function( jqxhr, settings, exception ) {
	    console.log('fail')
	});

	var sea_index = 1;
	var air_index = 1;

	var apply_markers = function(map, data)
	{
		if(markers.length > 0)
		{
			clear_markers();
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
			if (data[i].type == 'air')
			{
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
					icon = './images/air_' + colors[color_index] + '.png';
				}
				else
				{
					icon = './images/air.png'
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
					icon = './images/sea_' + colors[color_index] + '.png';
				}
				else
				{
					icon = './images/sea.png'
				}
				
				sea_index++;
			}
			
			//create marker
			marker = new google.maps.Marker({
				position: myLatLng,
				label: '' + index,
				map: map,
				icon: icon
			});
			
			//set the marker properties
			marker.toggle_state = 1;
			marker.toggle_index = index;
			marker.instrument_type = data[i].type;
			marker.station_id = data[i].station_id;
			marker.icon = icon;
			
			//function for changing the icon
			marker.set_icon = function(color)
			{
				if (color == null)
				{
					this.setIcon('images/' + this.instrument_type + '.png');
				}
				else
				{
					this.setIcon('images/' + this.instrument_type + '_' + color + '.png');
				}
				
			}
			
			markers.push(marker);
		}
	}
	
	var clear_markers = function(map)
	{
		for (var i = 0; i < markers.length; i++)
		{
			markers[i].setMap(null);
		}
		markers = []
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
	
	var make_pair = function(pair_id, sea_id, air_id, color_index)
	{
		return {
			"pair_id": pair_id,
			"sea_id": sea_id,
			"air_id": air_id,
			"color": color_index
		}
	}
	
	var add_pair = function(pair_id, sea_id, air_id, color_index)
	{
		pairs.push(make_pair(pair_id, sea_id, air_id, color_index));
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
		}
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
	
	var final_data = []
	var count = 0;
	var current_pairs = null;
	var current_colors = null;
	
	$('#graphForm').on('submit', function(event){
		event.preventDefault();
		
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
						dash_objects[i].color = current_colors;
						update_content(dash_objects[i],final_data, false);
					}		
				}
			});
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
	
	dash_objects.push(dash1)
	dash_objects.push(dash2);
	dash_objects.push(dash3);
	dash_objects.push(dash4);
	
	$('button').removeAttr('disabled');
	
	//----------------------------Initialize the map and markers for each station----------////

});