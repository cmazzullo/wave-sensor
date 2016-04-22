
$(function() {
	
	$('#sidebar').css('min-height', '2800px');
	$('#mainGraph').css('min-height', '2800px');
	
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
		case "stat":
			
			//Get the appropriate graph data
			var graph_data = null
			switch(dash_object.method)
			{
			case "1":
				graph_data = data['H1/3']; break;
			case "2":
				graph_data = data['H10%']; break;
			case "3":
				graph_data = data['H1%']; break;
			case "4":
				graph_data = data['RMS']; break;
			case "5":
				graph_data = data['Median']; break;
			case "6":
				graph_data = data['Maximum']; break;
			case "7":
				graph_data = data['Average']; break;
			case "8":
				graph_data = data['T1/3']; break;
			case "9":
				graph_data = data['Average Z Cross']; break;
			case "10":
				graph_data = data['Mean Wave Period']; break;
			case "11":
				graph_data = data['Crest']; break;
			case "12":
				graph_data = data['Peak Wave']; break;
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
		case "main_stat":
			var graph_data = [data['wave_wl'],data['H1/3'],data['H10%'],data['H1%']]
			
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
			url: 'http://localhost:8080/statistics',
			data: {
				start_time: $('#start_date').val(),
				end_time: $('#end_date').val(),
				daylight_savings: $('#dst').val(),
				timezone: $('#timezone').val(),
				change: 'false'
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
			url: 'http://localhost:8080/statistics',
			data: {
				start_time: $('#start_date').val(),
				end_time: $('#end_date').val(),
				daylight_savings: $('#dst').val(),
				timezone: $('#timezone').val(),
				change: 'true'
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
	
	var main = make_dash('dash13','visualization13','main_stat','1','blue');
	var dash1 = make_dash('dash1','visualization1','stat','1','red');
	var dash2 = make_dash('dash2','visualization2','stat','2','red');
	var dash3 = make_dash('dash3','visualization3','stat','3','red');
	var dash4 = make_dash('dash4','visualization4','stat','4','red');
	var dash5 = make_dash('dash5','visualization5','stat','5','red');
	var dash6 = make_dash('dash6','visualization6','stat','6','red');
	var dash7 = make_dash('dash7','visualization7','stat','7','red');
	var dash8 = make_dash('dash8','visualization8','stat','8','blue');
	var dash9 = make_dash('dash9','visualization9','stat','9','blue');
	var dash10 = make_dash('dash10','visualization10','stat','10','blue');
	var dash11 = make_dash('dash11','visualization11','stat','11','blue');
	var dash12 = make_dash('dash12','visualization12','stat','12','blue');
	
	dash_objects.push(main);
	dash_objects.push(dash1);
	dash_objects.push(dash2);
	dash_objects.push(dash3);
	dash_objects.push(dash4);
	dash_objects.push(dash5);
	dash_objects.push(dash6);
	dash_objects.push(dash7);
	dash_objects.push(dash8);
	dash_objects.push(dash9);
	dash_objects.push(dash10);
	dash_objects.push(dash11);
	dash_objects.push(dash12);
	
	
});