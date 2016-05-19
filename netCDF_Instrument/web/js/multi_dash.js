
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
	var toggle_state = null;
	
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
					makeMultiGraph(graph_data,dash_object,['red','green','blue','purple']);
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
							updateMultiGraph(graph_data,dash_object,960,440);
							dash_object.expanded = true;
						}
						else if (change == true && dash_object.expanded == true)
						{
							$('#' + dash_object.contentId).attr('width', '440px');
							$('#' + dash_object.contentId).attr('height', '220px');
							updateMultiGraph(graph_data,dash_object,440,220);
							dash_object.expanded = false;
						}
					 }
				 else
					 {
					 	var width = parseInt($('#' + dash_object.contentId).attr('width').substring(0,3));
					 	var height = parseInt($('#' + dash_object.contentId).attr('height').substring(0,3));
					 	console.log(width,height);
					 	updateMultiGraph(graph_data,dash_object,width,height);
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
			url: 'http://localhost:8080/multi',
			data: {
				start_time: $('#start_date').val(),
				end_time: $('#end_date').val(),
				daylight_savings: $('#dst').val(),
				timezone: $('#timezone').val(),
				toggle_state: toggle_state
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
			url: 'http://localhost:8080/multi',
			data: {
				start_time: $('#start_date').val(),
				end_time: $('#end_date').val(),
				daylight_savings: $('#dst').val(),
				timezone: $('#timezone').val(),
				toggle_state: toggle_state
			},
			datatype: 'JSON',
			error: function()
			{
				console.log('error');
			}
		})
		.done(function(data) {
			
			for (var i = 0; i < dash_objects.length; i++){
				update_content(dash_objects[i],data, false);
			}	
		});
		
	})
	
	var dash1 = make_dash('dash1','visualization1','water_level_graph','Unfiltered','blue');
	var dash2 = make_dash('dash3','visualization2','water_level_graph','Surge','green')
	var dash3 = make_dash('dash5','visualization3','water_level_graph','Wave','purple');
	var dash4 = make_dash('dash6','visualization4','water_level_graph','Air','red');
	
	dash_objects.push(dash1);
	dash_objects.push(dash2);
	dash_objects.push(dash3);
	dash_objects.push(dash4);
	
	var update_toggle_state = function(tstate)
	{
		//First check to see which sea pressure sensors were added/removed
		for (var i = 0; i < tstate[0].length; i++)
			{
			   if (tstate[0][i] == 1 && toggle_state[0][i] == 0)
				   {
				  
				   }
			   if (tstate[0][i] == 0 && toggle_state[0][i] == 1)
				   {
				   
				   }
			}
		
		//Check what air pressure sensors were added - removed
		for (var i = 0; i < tstate[1].length; i++)
		{
		   if (tstate[1][i] == 1 && toggle_state[1][i] == 0)
			   {
			   		
			   }
		   if (tstate[1][i] == 0 && toggle_state[1][i] == 1)
			   {
			   
			   }
		}
	}
	
	
});