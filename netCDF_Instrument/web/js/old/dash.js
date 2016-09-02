
$(function() {
	
	$.getScript( "./js/graphs.js" )
	  .done(function( script, textStatus ) {
	    console.log( 'success',textStatus );
	  })
	  .fail(function( jqxhr, settings, exception ) {
	    console.log('fail')
	});
	
	$('#start_date').datetimepicker();
	$('#end_date').datetimepicker();
	
	var dash_objects = [];
	
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
		case "map":
			console.log('map')
			var myLatLng = null
			if (dash_object.method == 'sea_pressure')
				{
				myLatLng = {lat: data['latitude'], lng: data['longitude']};
				}
			else{
				myLatLng = {lat: data['air_latitude'], lng: data['air_longitude']};
			}
			
			if (dash_object.contentCreated == false)
				{
					console.log('not_created');
					
	
					map = new google.maps.Map(document.getElementById(dash_object.contentId), {
					  center: myLatLng,
					  zoom: 14
					});
					
					marker = new google.maps.Marker({
						position: myLatLng,
						label: 'Instrument',
						map: map
					});
					
					dash_object.contentCreated = true;
				}
			else
				{
					
					map = new google.maps.Map(document.getElementById(dash_object.contentId), {
					  center: myLatLng,
					  zoom: 14
					});
					
					marker = new google.maps.Marker({
						position: myLatLng,
						label: 'Instrument',
						map: map
					});
					
					if (change == true && dash_object.expanded == false)
					{
						$('#' + dash_object.contentId).css({'width': '960px','height': '438px'});
						dash_object.expanded = true;
					}
					else if (change == true && dash_object.expanded == true)
					{
						$('#' + dash_object.contentId).css({'width': '470px','height': '218px'});
						dash_object.expanded = false;
					}
					google.maps.event.trigger(map, 'resize');
				}
			break;
		case "water_level_graph":
			
			//Get the appropriate graph data
			var graph_data = null
			switch(dash_object.method)
			{
			case "Unfiltered":
				graph_data = data['raw_data']; break;
			case "Surge":
				graph_data = data['surge_data']; break;
			case "Wave":
				graph_data = data['wave_data']; break;
			case "Air":
				graph_data = data['air_data']; break;
			}
			
			
			//If content not created, create, otherwise update
			if (dash_object.contentCreated == false)
				{
					makeGraph(graph_data,dash_object);
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
							updateGraph(graph_data,dash_object,960,440);
							dash_object.expanded = true;
						}
						else if (change == true && dash_object.expanded == true)
						{
							$('#' + dash_object.contentId).attr('width', '440px');
							$('#' + dash_object.contentId).attr('height', '220px');
							updateGraph(graph_data,dash_object,440,220);
							dash_object.expanded = false;
						}
					 }
				 else
					 {
					 	var width = parseInt($('#' + dash_object.contentId).attr('width').substring(0,3));
					 	var height = parseInt($('#' + dash_object.contentId).attr('height').substring(0,3));
					 	console.log(width,height);
					 	updateGraph(graph_data,dash_object,width,height);
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
		
		$.ajax({
			type: 'POST',
			url: 'http://localhost:8080/single',
			data: {
				start_time: $('#start_date').val(),
				end_time: $('#end_date').val(),
				daylight_savings: $('#dst').val(),
				timezone: $('#timezone').val(),
			},
			datatype: 'JSON',
			error: function()
			{
				console.log('error');
			}
		})
		.done(function(data) {
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
				    find_dash(id, data);
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
				    find_dash(id, data);
				    elem.removeAttr('disabled');
				  });
			}
			
			
		});
	
		
	});
	
	$('#graphForm').submit(function(event){
		event.preventDefault();
		console.log(dash_objects.length);
		$.ajax({
			type: 'POST',
			url: 'http://localhost:8080/single',
			data: {
				start_time: $('#start_date').val(),
				end_time: $('#end_date').val(),
				daylight_savings: $('#dst').val(),
				timezone: $('#timezone').val(),
			},
			datatype: 'JSON',
			error: function()
			{
				console.log('error');
			}
		})
		.done(function(data) {
			
			$('#sea_site').text(data['sea_stn'][0]);
			$('#sea_instrument').text(data['sea_stn'][1]);
			$('#air_site').text(data['air_stn'][0]);
			$('#air_instrument').text(data['air_stn'][1]);
			$('#sea_lat').text(data['latitude']);
			$('#sea_lon').text(data['longitude']);
			$('#air_lat').text(data['air_latitude']);
			$('#air_lon').text(data['air_longitude']);
			
			
			for (var i = 0; i < dash_objects.length; i++){
				update_content(dash_objects[i],data, false);
			}	
		});
		
	})
	
	var dash1 = make_dash('dash1','visualization1','water_level_graph','Unfiltered','blue');
	var dash2 = make_dash('dash2','map1','map','sea_pressure','blue');
	var dash3 = make_dash('dash3','visualization2','water_level_graph','Surge','green')
	var dash4 = make_dash('dash4','map2','map','air_pressure','blue');
	var dash5 = make_dash('dash5','visualization3','water_level_graph','Wave','purple');
	var dash6 = make_dash('dash6','visualization4','water_level_graph','Air','red');
	
	dash_objects.push(dash1);
	dash_objects.push(dash2);
	dash_objects.push(dash3);
	dash_objects.push(dash4);
	dash_objects.push(dash5);
	dash_objects.push(dash6);
	
});