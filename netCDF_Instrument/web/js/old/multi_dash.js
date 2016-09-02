
$(function() {
	
	$.getScript( "./js/graphs.js" )
	  .done(function( script, textStatus ) {
	    console.log( 'success',textStatus );
	  })
	  .fail(function( jqxhr, settings, exception ) {
	    console.log('fail')
	});
	
	
	$.getScript( "https://maps.googleapis.com/maps/api/js?key=AIzaSyBKbkdjgPWlg8vSn-yDSHCp3ucmcm93bAQ" )
	  .done(function( script, textStatus ) {
		  
		  
		myLatLng = {lat: 40.900501251, lng: -73.352996826};
		map = new google.maps.Map(document.getElementById('multi_map'), {
			  center: myLatLng,
			  zoom: 8
		});
			
		//for now create a static list lats and lons, in future will be called from server based on input event parameters
		lat_long_list = [
		[41.579200744462896,-74.07520294189453],
		[40.70109939575195,-74.0156021118164],
		[40.79249572753906,-73.82828521728516],
		[40.9005012512207,-73.35299682617188],
		[41.01546859741211,-72.56101989746094],
		[40.65813980102539,-74.23070678710938],
		[40.80109939575195,-74.0156021118164],
		[40.89249572753906,-73.92828521728516],
		[41.0005012512207,-73.45299682617188],
		[41.11546859741211,-72.66101989746094]
		]
		
		//Iterate through static lat lons and create a marker for each
		for (var i = 0; i < lat_long_list.length; i++)
		{
			myLatLng = {lat: lat_long_list[i][0], lng: lat_long_list[i][1]};
		
			icon =  '../images/sea.png'
			type= 'sea';
			if (i > 4)
				{
					type = 'air'
					icon = '../images/air.png'
				}
			
			marker = new google.maps.Marker({
				position: myLatLng,
				label: '' + (i % 5 + 1),
				map: map,
				icon: icon
			});
			
			marker.toggle_state = 1;
			marker.toggle_index = i % 5;
			marker.instrument_type = type;
			marker.icon = icon;
			
			
			marker.change_state = function()
			{
				if (this.toggle_state == 1)
				{
					this.toggle_state = 0;
				}
				else
				{
					this.toggle_state = 1;
				}
			}
			
			marker.toggle_icon = function()
			{
				if (this.toggle_state == 1)
					{
					this.setIcon('images/' + this.instrument_type + '.png');
					}
				else
					{
					this.setIcon('images/' + this.instrument_type + '_not.png');
					}
			}
			
			marker.update_state = function()
			{
				if (this.instrument_type == 'sea')
					{
					toggle_state[0][this.toggle_index] =  this.toggle_state;
					}
				else
					{
					toggle_state[1][this.toggle_index] = this.toggle_state;
					}
			}
			
			marker.addListener('click', function(event) {
				
				//invert the toggle 
				this.change_state();
				this.toggle_icon();
				this.update_state();
				$('#graphForm').trigger('submit');
				//change the icon of the maker
				
			});
		}
	  })
	  .fail(function( jqxhr, settings, exception ) {
	    console.log('fail')
	});
	
	$('#start_date').datetimepicker();
	$('#end_date').datetimepicker();
	
	//store dash objects
	var dash_objects = [];
	
	//static state for now, all instrument on by default
	var toggle_state = [[1,1,1,1,1],[1,1,1,1,1]];
	var pairs = null;
	var state_data = null;
	var colors = ['red','green','blue','purple','orange'];
	
	var make_dash = function(id, contentId, contentType, method, color)
	{
		return {
			"id": id,
			"contentId": contentId,
			"contentType": contentType,
			"contentCreated": false,
			"expanded": false,
			"method": method,
			"color": color
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
		console.log(dash_object.contentType);
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
					console.log('path_data', data[i]['sea_stn'][0].toString() + '' + data[i]['air_stn'][0].toString())
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
						if (change == true && dash_object.expanded == false)
						{
							$('#' + dash_object.contentId).attr('width', '960px');
							$('#' + dash_object.contentId).attr('height', '440px');
							updateMultiGraph(graph_data,dash_object,colors,960,440,true,path_data);
							dash_object.expanded = true;
						}
						else if (change == true && dash_object.expanded == true)
						{
							$('#' + dash_object.contentId).attr('width', '440px');
							$('#' + dash_object.contentId).attr('height', '220px');
							updateMultiGraph(graph_data,dash_object,colors,440,220,true,path_data);
							dash_object.expanded = false;
						}
					 }
				 else
					 {
					 	var width = parseInt($('#' + dash_object.contentId).attr('width').substring(0,3));
					 	var height = parseInt($('#' + dash_object.contentId).attr('height').substring(0,3));
					 	console.log(width,height);
					 	updateMultiGraph(graph_data,dash_object,colors,width,height,true,path_data);
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
			console.log(height);
			$('#sidebar').css('height', parseInt(height.substring(0,height.length - 2)) + 500);
			var height2 = $('#mainGraph').css('height');
			$('#mainGraph').css('height', parseInt(height.substring(0,height.length - 2)) + 500);
			
			elem.parent().parent().animate({
			    height: "480px",
			    width: "960px"
			  }, 500, function() {
				
			    elem.text('Shrink');
			    find_dash(id, state_data);
			    elem.removeAttr('disabled');
			  });
		}
		else{
			
			var height = $('#sidebar').css('height');
			console.log(height);
			$('#sidebar').css('height', parseInt(height.substring(0,height.length - 2)) - 500);
			var height2 = $('#mainGraph').css('height');
			$('#mainGraph').css('height', parseInt(height.substring(0,height.length - 2)) - 500);
			
			elem.parent().parent().animate({
			    height: "260px",
			    width: "470px"
			  }, 500, function() {
				
			    elem.text('Expand');
			    find_dash(id, state_data);
			    elem.removeAttr('disabled');
			  });
		}
	
	});
	
	$('#graphForm').on('submit', function(event){
		event.preventDefault();
		$('.loading').show()
		
		pairs = get_pairs();
		var final_data = []
		var count = 0;
		for(var i = 0; i < pairs.length; i++)
		{
			console.log('pairs',pairs[i][0],pairs[i][1])
			$.ajax({
				type: 'POST',
				url: 'http://localhost:8080/single',
				data: {
					start_time: $('#start_date').val(),
					end_time: $('#end_date').val(),
					daylight_savings: $('#dst').val(),
					timezone: $('#timezone').val(),
					sea_file: pairs[i][0],
					baro_file: pairs[i][1]
				},
				datatype: 'JSON',
				error: function()
				{
					console.log('error');
				}
			})
			.done(function(data) {
				final_data.push(data);
				state_data = final_data;
				count++;
				console.log(count)
				if (count >= pairs.length)
					{
						$('.loading').hide()
						count = 0;
						for (var i = 0; i < dash_objects.length; i++){
							update_content(dash_objects[i],final_data, false);
						}	
					}
			});
		}
	})
	
	//Get pairs to send data requests to server
	var get_pairs = function()
	{
		var last_sea = -1;
		var last_air = -1;
		change = false;
		var pairs = [];
		
		for(var i = 0 ; i < toggle_state[0].length; i++)
			{
				if(toggle_state[0][i] == 1)
					{
						last_sea = i
						change = true;
					}
				if(toggle_state[1][i] == 1)
					{
						last_air = i;
						change = true;
					}
				
				if(last_sea != -1 && last_air != -1 &&
						change == true)
					{
						pairs.push([last_sea,last_air])
					}
				
				change = false;
			}
		
		return pairs;
	}
	
	var dash1 = make_dash('multi_raw','visualization1','water_level_graph','Unfiltered','blue');
	var dash2 = make_dash('multi_surge','visualization2','water_level_graph','Surge','green')
	var dash3 = make_dash('multi_wave','visualization3','water_level_graph','Wave','purple');
	var dash4 = make_dash('multi_baro','visualization4','water_level_graph','Air','red');
	
	dash_objects.push(dash1)
	dash_objects.push(dash2);
	dash_objects.push(dash3);
	dash_objects.push(dash4);
	
	$('button').removeAttr('disabled');
	
	//----------------------------Initialize the map and markers for each station----------////
	
	
	
	
});