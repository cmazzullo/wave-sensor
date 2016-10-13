
$(function() {
	
	var sea_instrument = location.search.split('=')[1].split('&')[0]
	var air_instrument = location.search.split('=')[2]
	
	$.getScript( "./js/aesthetic/graphs.js" )
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
			title, xlabel, ylabel, order)
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
			"ylabel": ylabel,
			"order": order
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
		case "height_stat":
			
			//Get the appropriate graph data
			var graph_data = null;
			var path_data = ['original','upper_ci','lower_ci'];
			switch(dash_object.method)
			{
			case "H1/3":
				graph_data = [data['H1/3'],
				              data['upper_H1/3'],
				              data['lower_H1/3']]; break;
			case "H10%":
				graph_data = [data['H10%'],
				              data['upper_H10%'],
				              data['lower_H10%']]; break;
			case "H1%":
				graph_data = [data['H1%'],
				              data['upper_H1%'],
				              data['lower_H1%']]; break;
			case "RMS":
				graph_data = [data['RMS'],
				              data['upper_RMS'],
				              data['lower_RMS']]; break;
			case "Median":
				graph_data = [data['Median'],
				              data['upper_Median'],
				              data['lower_Median']]; break;
			case "Maximum":
				graph_data = [data['Maximum'],
				              data['upper_Maximum'],
				              data['lower_Maximum']]; break;
			case "Average":
				graph_data = [data['Average'],
				              data['upper_Average'],
				              data['lower_Average']]; break;
			}
			
			//If content not created, create, otherwise update
			if (dash_object.contentCreated == false)
			{
				dash_object.state_index = makeMultiGraph(graph_data,dash_object,dash_object.color, true, path_data);
				dash_object.contentCreated = true;
			}
		else
			{
			//If dash tile is expanded, change width and height, otherwise just update
			 if (change == true)
				 {
					if (dash_object.expanded == false)
					{
						$('#' + dash_object.contentId).attr('width', '960px');
						$('#' + dash_object.contentId).attr('height', '640px');
						updateMultiGraph(graph_data,dash_object,dash_object.color,960,640,true,!dash_object.expanded,path_data);
						dash_object.expanded = true;
					}
					else if ( dash_object.expanded == true)
					{
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
		case "period_stat":
			var graph_data = null;
			switch(dash_object.method)
			{
			case "T1/3":
				graph_data = data['T1/3']; break;
				
			case "Average Z Cross":
				graph_data = data['Average Z Cross']; break;
				
			case "Mean Wave Period":
				graph_data = data['Mean Wave Period']; break;
				
			case "Crest":
				graph_data = data['Crest']; break;
				
			case "Peak Wave":
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
							$('#' + dash_object.contentId).attr('height', '640px');
							updateGraph(graph_data,dash_object,960,640,true);
							dash_object.expanded = true;
						}
						else if (change == true && dash_object.expanded == true)
						{
							$('#' + dash_object.contentId).attr('width', '440px');
							$('#' + dash_object.contentId).attr('height', '440px');
							updateGraph(graph_data,dash_object,440,440, false);
							dash_object.expanded = false;
						}
					 }
				 else
					 {
					 	var width = parseInt($('#' + dash_object.contentId).attr('width').substring(0,3));
					 	var height = parseInt($('#' + dash_object.contentId).attr('height').substring(0,3));
					 	updateGraph(graph_data,dash_object,width,height,dash_object.expanded);
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
			    find_dash(id, master_data);
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
			    find_dash(id, master_data);
			    elem.removeAttr('disabled');
			  });
		}
	});
	
	$('#graphForm').submit(function(event){
		event.preventDefault();
		show_load();
		ajax_post(0);
	})
	
	var ajax_post = function(post_errors)
	{
		if (post_errors < 5)
		{
			$.ajax({
				type: 'POST',
				url: 'http://localhost:8080/statistics',
				data: {
					start_time: $('#start_date').val(),
					end_time: $('#end_date').val(),
					daylight_savings: $('#dst').val(),
					timezone: $('#timezone').val(),
					sea_file: sea_instrument,
					baro_file: air_instrument,
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
	
	var dash1 = make_dash('dash1','visualization1','height_stat','H1/3',
			['blue','green','red'],
			['Original Estimate', 'Upper 95% Confidence Bound',
			 'Lower 95% Confidence Bound'],
			"Significant Wave Height","Time in GMT","Significant Wave Height in Feet");
	var dash2 = make_dash('dash2','visualization2','height_stat','H10%',
			['blue','green','red'],
			['Original Estimate', 'Upper 95% Confidence Bound',
			 'Lower 95% Confidence Bound'],
			"Top Ten Percent Wave Height","Time in GMT","Top Ten Percent Wave Height in Feet");
	var dash3 = make_dash('dash3','visualization3','height_stat','H1%',
			['blue','green','red'],
			['Original Estimate', 'Upper 95% Confidence Bound',
			 'Lower 95% Confidence Bound'],
			 "Top One Percent Wave Height","Time in GMT","Top One Percent Wave Height in Feet");
	var dash4 = make_dash('dash4','visualization4','height_stat','RMS',
			['blue','green','red'],
			['Original Estimate', 'Upper 95% Confidence Bound',
			 'Lower 95% Confidence Bound'],
			"RMS Wave Height","Time in GMT","RMS Wave Height in Feet");
	var dash5 = make_dash('dash5','visualization5','height_stat','Median',
			['blue','green','red'],
			['Original Estimate', 'Upper 95% Confidence Bound',
			 'Lower 95% Confidence Bound'],
			"Median Wave Height","Time in GMT","Median Wave Height in Feet");
	var dash6 = make_dash('dash6','visualization6','height_stat','Maximum',
			['blue','green','red'],
			['Original Estimate', 'Upper 95% Confidence Bound',
			 'Lower 95% Confidence Bound'],
			"Maximum Wave Height","Time in GMT","Maximum Wave Height in Feet");
	var dash7 = make_dash('dash7','visualization7','height_stat','Average',
			['blue','green','red'],
			['Original Estimate', 'Upper 95% Confidence Bound',
			 'Lower 95% Confidence Bound'],
			"Average Wave Height","Time in GMT","Average Wave Period in Seconds");
	var dash8 = make_dash('dash8','visualization8','period_stat','T1/3',
			'blue', 'Significant Wave Period',
			"Significant Wave Period","Time in GMT","Significant Wave Period in Seconds");
	var dash9 = make_dash('dash9','visualization9','period_stat','Average Z Cross',
			'blue', 'Average Zero Up Crossings Period',
			"Average Zero Up Crossings Period","Time in GMT","Average Zero Up Crossings Period in Seconds");
	var dash10 = make_dash('dash10','visualization10','period_stat','Mean Wave Period',
			'blue', 'Mean Wave Period',
			"Mean Wave Period","Time in GMT","Mean Wave Period in Seconds");
	var dash11 = make_dash('dash11','visualization11','period_stat','Crest',
			'blue', 'Crest Wave Period',
			"Crest Wave Period","Time in GMT","Crest Wave Period in Seconds");
	var dash12 = make_dash('dash12','visualization12','period_stat','Peak Wave',
			'blue', 'Peak Wave Period',
			"Peak Wave Period","Time in GMT","Peak Wave Period in Seconds");
	
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
	
	setTimeout(function(){
		$('#graphForm').trigger('submit');
	}, 1000);
	
	var hide_load = function() { $('#slideLoad').slideUp(); }
	var show_load = function() { $('#slideLoad').slideDown(); }
	
});