	$.getScript( "./js/aesthetic/graph_legend.js" )
	  .done(function( script, textStatus ) {
	    console.log( 'success',textStatus );
	  })
	  .fail(function( jqxhr, settings, exception ) {
	    console.log('legend fail')
	});

	//This is the graph creation for the single graph
	var makeWindGraph = function(data, dash_object)
	{
		
	//This is the fill data to be graphed
	var xmin = data['time'][0];
	var xmax = data['time'][data['time'].length - 1];
	var ymax = data['Wind_Max']
	
	//space for the sticks to rotate
	range_margin = .1;
	ymax = ymax * (1+range_margin)
	ymin = ymax * -1;

	//These are the dimensions of the graph
	var 
	WIDTH = 440,
	HEIGHT = 440,
	MARGINS = {
	  top: 165,
	  right: 20,
	  bottom: 80,
	  left: 50
	},
	//Establishes the horizontal and vertical boundaries for the graph data
	xRange = d3.time.scale().range([MARGINS.left, WIDTH - MARGINS.right])
	.domain([make_date(xmin), make_date(xmax)]),
	yRange = d3.scale.linear().range([HEIGHT - MARGINS.bottom, MARGINS.top])
	.domain([ymin,ymax]),
	
	//This triggers the zoom behavior for the graph data
	zoom = d3.behavior.zoom()
    .x(xRange)
    .y(yRange)
    .scaleExtent([.5, 32])
    .on("zoom", zoomed),
    vis = d3.select('#' + dash_object.contentId).call(zoom),
    
    //This calls the x and y axis for the graph
	xAxis = d3.svg.axis()
	  .scale(xRange)
	  .orient('bottom')
	  .ticks(3)
	  .tickSize(-1*(HEIGHT - MARGINS.top - MARGINS.bottom),0,0)
	  .tickFormat(d3.time.format("\n%m-%d-%Y"))
	  .outerTickSize(0)
	  .tickSubdivide(true);
	
	//This is a white rectangle created in order to allow 
	//the image capture to have a white background
	vis.append('svg:rect')
	.attr('class', 'background')
	.attr('width', 440)
	.attr('height', 415)
	.attr('style', 'fill:rgb(255,255,255)')
	.attr('x', 0)
	.attr('y', 0)
	
	//This calls the legend
	wind_legend(vis, dash_object, null, data['Wind_Max'], yRange);
	
	//This applies the logo
	vis.append('svg:image')
		.attr('width', '150px')
		.attr('height', '100px')
		.attr('x',30)
		.attr('y', 30)
		.attr('class','usgs')
		.attr('xlink:href','./images/usgs.png')
		
	vis.append('svg:image')
		.attr('width', '30px')
		.attr('height', '40px')
		.attr('x',50)
		.attr('y', 170)
		.attr('class','north')
		.attr('xlink:href','./images/north.png')
		
	//This is the title for the graph
	vis.append('svg:text')
	.attr('class','title')
	.attr('x', WIDTH/2.0 - 45)
	.attr('y', 155)
	.attr('font-size', 14)
	.attr('font-family', 'Trebuchet MS')
	.text(dash_object.title)
	
	//This is the x label for the graph
	vis.append('svg:text')
	.attr('class', 'xlabel')
	.attr('x', WIDTH/2.0 - 25)
	.attr('y', 395)
	.attr('size', '10pt')
	.attr('font-size', 11)
	.attr('font-family', 'Trebuchet MS')
	.text(dash_object.xlabel)
	
	
	//This calls the x axis and sets the position of all text in the x axis
	vis.append('svg:g')
	.attr('class', 'x_axis')
	.attr('transform', 'translate(0,' + (HEIGHT - MARGINS.bottom) + ')')
	.call(xAxis)
	.selectAll("text") 
	.attr("y", "7px");
	
	
	//This removes the auto generated grey line border for the x axis
	vis.select('.x_axis')
	.selectAll("path") 
	.remove()
	
	
	
	//The following creates solid black lines for the top and
	//bottom border of the y axis
	vis.append('svg:g')
	.attr('class', 'top-border')
	.attr('transform','translate(50,165)')
	.append('svg:line')
	.attr('x2',370)
	.attr('y2', 0)
	.attr('style',"stroke:rgb(0,0,0)")
	
	vis.append('svg:g')
	.attr('class', 'bottom-border')
	.attr('transform','translate(50,360)')
	.append('svg:line')
	.attr('x2',370)
	.attr('y2', 0)
	.attr('style',"stroke:rgb(0,0,0)")
	
	//This adjusts the color of the graph grid lines
	vis.selectAll('.tick')
	.selectAll('line')
	.attr('style', 'stroke:rgb(199,199,199)');
	
	make_stick_lines(vis, data, xRange, yRange);
	//The following draws the line data to its respective position
	//in the SVG element
//	var lineFunc = d3.svg.line()
//	.x(function(d) {
//	   return  xRange(d.x);
//	})
//	.y(function(d) {
//	  return yRange(d.y);
//	})
//	.defined(function(d) { return (
//			xRange(d.x) > MARGINS.left 
//			&& xRange(d.x) < WIDTH - MARGINS.right
//			&& yRange(d.y) < HEIGHT - MARGINS.bottom
//			&& yRange(d.y) > MARGINS.top
//	)
//		})
//	.interpolate('linear');
//	
//	//Get the x axis min
//	var min = lineData[0].x
//	
//	//Used to animate an accordion like hiding of the data
//	//when a new set of data replaces it
//	var zeroFunc = d3.svg.line()
//	.x(function(d) {
//	  return xRange(min);
//	})
//	.y(function(d) {
//	return yRange(d.y);
//	})
//	.interpolate('linear');
//	
//	//creates the graph data line
//	vis.append('svg:path')
//	.attr('class','main_path')
//	.attr('stroke', dash_object.color)
//	.attr('stroke-width', 2)
//	.attr('opacity', .6)
//	.attr('fill', 'none')
//	.transition()
//	.attr('d', zeroFunc(lineData))
//	.transition()
//	.duration(1000)
//	.attr('d', lineFunc(lineData));
	
	//function to call when zooming or panning
	function zoomed() {
		
		//call x/y axis and adjust its text position
		  vis.select(".x_axis").call(xAxis)
		  .selectAll("text") 
			.attr("y", "7px")
		  
		  
		  //adjust color of graph grid lines
		  vis.selectAll('.tick')
			.selectAll('line')
			.attr('style', 'stroke:rgb(199,199,199)')
			
		//remove auto generated grey borders of x/y axis
		  vis.select('.x_axis')
			.selectAll("path") 
			.remove()
			
		//redraw line data based on current position
			vis.selectAll('.stick_lines').remove();
			make_stick_lines(vis, data, xRange, yRange);
		}
	}

	//This is the update function for a single graph
	var updateWindGraph = function(data, dash_object, width, height, expand)
		{
			console.log(data);
			var xmin = data['time'][0];
			var xmax = data['time'][data['time'].length - 1]
			var ymax = data['Wind_Max']
			
			//space for the sticks to rotate
			range_margin = .1;
			ymax = ymax * (1+range_margin)
			ymin = ymax * -1;
			
			var 
			//dimensions and margins for the graph
			WIDTH = width, //440,
			HEIGHT = height, //220,
			MARGINS = {
					  top: 165,
					  right: 20,
					  bottom: 80,
					  left: 50
					},
			//range for horizontal and vertical portions of the graph
			xRange = d3.time.scale().range([MARGINS.left, WIDTH - MARGINS.right])
			.domain([make_date(xmin), make_date(xmax)]),
			yRange = d3.scale.linear().range([HEIGHT - MARGINS.bottom, MARGINS.top])
			.domain([ymin,ymax]),
			
			//zoom function on the graph
			zoom = d3.behavior.zoom()
		    .x(xRange)
		    .y(yRange)
		    .scaleExtent([.5, 1.5])
		    .on("zoom", zoomed),
		    
		    vis = d3.select('#' + dash_object.contentId).call(zoom);
			
			xAxis = d3.svg.axis()
		    .scale(xRange)
		    .orient("bottom")
		    .ticks(3)
		    .tickSubdivide(true)
		    .tickFormat(d3.time.format("\n%m-%d-%Y"))
		    .tickSize(-1*(HEIGHT - MARGINS.top - MARGINS.bottom))
		    .outerTickSize(0);
			
			//updating the legend
			wind_legend(vis, dash_object, width, data['Wind_Max'], yRange);
			
			//update the position of the x axis
			vis.select(".x_axis")
			.attr("transform", "translate(" + 0 + "," + (HEIGHT - MARGINS.bottom) + ")")
			.transition()
			.call(xAxis)
			.selectAll("text") 
			.attr("y", "7px");
			
			//change the color of the graph grid lines
			vis.selectAll('.tick')
			.selectAll('line')
			.attr('style', 'stroke:rgb(199,199,199)')
			
			//remove the automatic grey graph borders for the x/y axis
			vis.select('.x_axis')
			.selectAll("path") 
			.remove()
			
			
			//If the graph is expanded
			if (expand)
				{
					//*** reposition the white background of graph
					vis.select('.background')
					.transition()
					.attr('width', 960)
					.attr('height', 636)
					
					//reposition and resize the title
					vis.select('.title')
					.transition()
					.attr('font-size', 20)
					.attr('x', WIDTH/2.0 - 45)
					.attr('y', 155)
					
					//reposition the xlabel and ylabel
					vis.select('.xlabel')
					.transition()
					.attr('x', WIDTH/2.0 - 25)
					.attr('y', 590)
					.attr('font-size', 13)
					
					//reposition the usgs logo
					vis.select('.usgs')
					.transition()
					.attr('width', '225px')
					.attr('height', '115px')
					.attr('x', 50)
					.attr('y', 20)
					
					
					
					//reposition the top border
					vis.select('.top-border')
					.transition()
					.attr('transform','translate(50,165)')
					.selectAll('line')
					.transition()
					.attr('x2',890)
					.attr('y2', 0)
					
					//reposition the bottom border
					vis.select('.bottom-border')
					.transition()
					.attr('transform','translate(50,560)')
					.selectAll('line')
					.transition()
					.attr('x2',890)
					.attr('y2', 0)
					
				}
			else
				{
					//review comments above (identical) ***
					vis.select('.background')
					.transition()
					.attr('width', 440)
					.attr('height', 415)
				
					vis.select('.title')
					.transition()
					.attr('font-size', 14)
					.attr('x', WIDTH/2.0 - 45)
					.attr('y', 155)
					
					vis.select('.xlabel')
					.transition()
					.attr('x', WIDTH/2.0 - 25)
					.attr('y', 390)
					.attr('font-size', 13)
					
					vis.select('.usgs')
					.transition()
					.attr('width', '150px')
					.attr('height', '100px')
					.attr('x', 30)
					.attr('y', 30)
					
					
					
					vis.select('.top-border')
					.transition()
					.attr('transform','translate(50,165)')
					.selectAll('line')
					.transition()
					.attr('x2',370)
					.attr('y2', 0)
					
					vis.select('.bottom-border')
					.transition()
					.attr('transform','translate(50,360)')
					.selectAll('line')
					.transition()
					.attr('x2',370)
					.attr('y2', 0)
					
				
				}
			
			vis.selectAll('.stick_lines').remove();
			make_stick_lines(vis, data, xRange, yRange);
			
			
			//function for when data is zoomed or panned
			function zoomed() {
				
				//adjust the axes and reposition their text
				vis.select(".x_axis").call(xAxis)
				  .selectAll("text") 
					.attr("y", "7px")
				
				//adjust color of all graph grid lines
				vis.selectAll('.tick')
					.selectAll('line')
					.attr('style', 'stroke:rgb(199,199,199)')
				  
				//remove automatic creation of grey lines
				  vis.select('.x_axis')
					.selectAll("path") 
					.remove()
					
				
					//redraw line data based on current position
				vis.selectAll('.stick_lines').remove();
				make_stick_lines(vis, data, xRange, yRange);
				
				wind_legend(vis, dash_object, width, data['Wind_Max'], yRange);
			}
		}
	
	var make_stick_lines = function(vis, data, xRange, yRange)
	{
		for (var i = 0; i < data['Wind_Speed'].length; i++)
		{
			time = xRange(data['time'][i]);
			zero = yRange(0)
			speed = yRange(data['Wind_Speed'][i]);
			rotation = data['Wind_Direction'][i] * -1;
			
			vis.append('svg:line')
			.attr('class','stick_lines')
			.attr('x1',time)
			.attr('x2',time)
			.attr('y1', zero)
			.attr('y2', speed)
			.attr('stroke','blue')
			.attr('opacity', 0.5)
			.attr('transform',"rotate(" + rotation + " " + time + "," + zero + ")")
		}

	}
	
	var make_date = function(date)
	{
		return new Date(date);
	}