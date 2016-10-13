
$(function() {
	
	$.getScript( "./js/aesthetic/wind_graph.js" )
	  .done(function( script, textStatus ) {
	    console.log( 'success',textStatus );
	  })
	  .fail(function( jqxhr, settings, exception ) {
	    console.log('fail')
	});
	
	$('#start_date').datetimepicker();
	$('#end_date').datetimepicker();
	
	var dash_objects = [];
	var master_data = null;
	
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
	}
	
	$('.expand').click(function(){
		
		var elem = $(this)
		elem.attr('disabled','disabled');
		var width = parseInt($(this).parent().parent().css('width'));
		var id = $(this).parent().parent().prop('id');
		
		
		if (width < 900)
		{
//			var height = $('#sidebar').css('height');
//			console.log(height);
//			$('#sidebar').css('height', parseInt(height.substring(0,height.length - 2)) + 600);
//			var height2 = $('#mainGraph').css('height');
//			$('#mainGraph').css('height', parseInt(height.substring(0,height.length - 2)) + 600);
			
			elem.parent().parent().animate({
			    height: "680px",
			    width: "960px"
			  }, 500, function() {
				
			    elem.text('Shrink');
			    find_dash(id, master_data);
			    elem.removeAttr('disabled');
			  });
		}
		else{
			
//			var height = $('#sidebar').css('height');
//			console.log(height);
//			$('#sidebar').css('height', parseInt(height.substring(0,height.length - 2)) - 600);
//			var height2 = $('#mainGraph').css('height');
//			$('#mainGraph').css('height', parseInt(height.substring(0,height.length - 2)) - 600);
			
			elem.parent().parent().animate({
			    height: "460px",
			    width: "470px"
			  }, 500, function() {
				
			    elem.text('Expand');
			    find_dash(id, master_data);
			    elem.removeAttr('disabled');
			  });
		}
	});
	
	$('#graphForm').submit(function(event){
		event.preventDefault();
		
		ajax_post(0);
	})
	
	var ajax_post = function(post_errors)
	{
		if (post_errors < 5)
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
					ajax_post(post_errors + 1);
				}
			})
			.done(function(data) {
				master_data = data;
				
				console.log(master_data);
				for (var i = 0; i < dash_objects.length; i++){
					update_content(dash_objects[i],data, false);
				}	
			});
		}
		else
		{
			console.log('error');
		}
	}
	
	var dash1 = make_dash('dash1','visualization1','water_level_graph','Unfiltered','blue',"Unfiltered Water Level",
			"Raw Water Level","Time in GMT","Water Level in Feet");
	
	dash_objects.push(dash1);
	
	
	setTimeout(function(){
		$('#graphForm').trigger('submit');
	}, 1000);
	
});