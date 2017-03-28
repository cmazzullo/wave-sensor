	$.getScript( "./js/aesthetic/graph_legend.js" )
	  .done(function( script, textStatus ) {
	    console.log( 'success',textStatus );
	  })
	  .fail(function( jqxhr, settings, exception ) {
	    console.log('legend fail')
	});
	
	$.getScript( "./js/aesthetic/conrec.js" )
	  .done(function( script, textStatus ) {
	    console.log( 'success',textStatus );
	  })
	  .fail(function( jqxhr, settings, exception ) {
	    console.log('conrec fail')
	});

	//This is the graph creation for the single graph
	var makeGraph = function(data, dash_object)
	{
//		console.log(data)
//		console.log(dash_object.contentType)
//		console.log(dash_objct.method)
		//This is the fill data to be graphed
		var lineData = data;
		var xmin = find_min([data], true);
		var xmax = find_max([data], true);
		var ymin = find_min([data], false);
		var ymax = find_max([data], false);
		
		//add different margins for data based on data type
		if(dash_object.method == 'Air')
		{
			range_margin = .001
		}
		else
		{
			range_margin = .1
		}
		
		if(ymin < 0)
		{
			ymin = ymin * (1+range_margin)
		}
		else
		{
			ymin = ymin * (1-range_margin)
		}
	
		if (ymax < 0)
		{
			ymax = ymax * (1-range_margin)
		}
		else
		{
			ymax = ymax * (1+range_margin)
		}
		
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
	    .scaleExtent([1, 32])
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
		  .tickSubdivide(true),
		yAxis = d3.svg.axis()
		  .scale(yRange)
		  .tickSize(-1*(WIDTH - MARGINS.left - MARGINS.right),0,0)
		  .outerTickSize(0)
		  .orient('left')
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
		legend(vis, dash_object, null);
		
		//This applies the logo
		vis.append('svg:image')
			.attr('width', '150px')
			.attr('height', '100px')
			.attr('x',30)
			.attr('y', 30)
			.attr('class','usgs')
			.attr('xlink:href','./images/usgs.png')
			
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
		
//		if dash_object.
		//This is the y label for the graph
		vis.append('svg:text')
		.attr('class', 'ylabel')
		.attr('x', -265)
		.attr('y', 45)
		.attr('transform',"rotate(-90 20,40)")
		.attr('font-size', 11)
		.attr('font-family', 'Trebuchet MS')
		.text(dash_object.ylabel)
		
		//This calls the x axis and sets the position of all text in the x axis
		vis.append('svg:g')
		.attr('class', 'x_axis')
		.attr('transform', 'translate(0,' + (HEIGHT - MARGINS.bottom) + ')')
		.call(xAxis)
		.selectAll("text") 
		.attr("y", "7px");
		
		//The following creates a solid black line
		//for the right and left border
		vis.select('.x_axis')
		.append('svg:g')
		.attr('class', 'right-border')
		.attr('transform','translate(420,0)')
		.append('svg:line')
		.attr('x2',0)
		.attr('y2', -195)
		.attr('style',"stroke:rgb(0,0,0)")
		
		vis.select('.x_axis')
		.append('svg:g')
		.attr('class', 'left-border')
		.attr('transform','translate(50,0)')
		.append('svg:line')
		.attr('x2',0)
		.attr('y2', -195)
		.attr('style',"stroke:rgb(0,0,0)")
		
		//This removes the auto generated grey line border for the x axis
		vis.select('.x_axis')
		.selectAll("path") 
		.remove()
		
		//This calls the y axis and sets the position of all text in the y axis
		vis.append('svg:g')
		.attr('class', 'y_axis')
		.attr('transform', 'translate(' + (MARGINS.left) + ',0)')
		.call(yAxis)
		.selectAll("text") 
		.attr("x", "-3px");
		
		//This removes the auto generated grey line border for the y axis
		vis.select('.y_axis')
		.selectAll("path") 
		.remove()
		
		//The following creates solid black lines for the top and
		//bottom border of the y axis
		vis.select('.y_axis')
		.append('svg:g')
		.attr('class', 'top-border')
		.attr('transform','translate(0,165)')
		.append('svg:line')
		.attr('x2',370)
		.attr('y2', 0)
		.attr('style',"stroke:rgb(0,0,0)")
		
		vis.select('.y_axis')
		.append('svg:g')
		.attr('class', 'bottom-border')
		.attr('transform','translate(0,360)')
		.append('svg:line')
		.attr('x2',370)
		.attr('y2', 0)
		.attr('style',"stroke:rgb(0,0,0)")
		
		//This adjusts the color of the graph grid lines
		vis.selectAll('.tick')
		.selectAll('line')
		.attr('style', 'stroke:rgb(199,199,199)');
		
		//The following draws the line data to its respective position
		//in the SVG element
		var lineFunc = d3.svg.line()
		.x(function(d) {
		   return  xRange(d.x);
		})
		.y(function(d) {
		  return yRange(d.y);
		})
		.defined(function(d) { return (
				xRange(d.x) > MARGINS.left 
				&& xRange(d.x) < WIDTH - MARGINS.right
				&& yRange(d.y) < HEIGHT - MARGINS.bottom
				&& yRange(d.y) > MARGINS.top
		)
			})
		.interpolate('linear');
		
		//Get the x axis min
		var min = lineData[0].x
		
		//Used to animate an accordion like hiding of the data
		//when a new set of data replaces it
		var zeroFunc = d3.svg.line()
		.x(function(d) {
		  return xRange(min);
		})
		.y(function(d) {
		return yRange(d.y);
		})
		.interpolate('linear');
		
		//creates the graph data line
		vis.append('svg:path')
		.attr('class','main_path')
		.attr('stroke', dash_object.color)
		.attr('stroke-width', 2)
		.attr('opacity', .6)
		.attr('fill', 'none')
		.transition()
		.attr('d', zeroFunc(lineData))
		.transition()
		.duration(1000)
		.attr('d', lineFunc(lineData));
		
		//function to call when zooming or panning
		function zoomed() {
			
			//call x/y axis and adjust its text position
			  vis.select(".x_axis").call(xAxis)
			  .selectAll("text") 
				.attr("y", "7px")
			  vis.select(".y_axis").call(yAxis)
			  .selectAll("text") 
				.attr("x", "-3px");
			  
			  //adjust color of graph grid lines
			  vis.selectAll('.tick')
				.selectAll('line')
				.attr('style', 'stroke:rgb(199,199,199)')
				
			//remove auto generated grey borders of x/y axis
			  vis.select('.x_axis')
				.selectAll("path") 
				.remove()
				
			vis.select('.y_axis')
				.selectAll("path") 
				.remove()
				
			//redraw line data based on current position
			  vis.select('.main_path')
				.attr('d', lineFunc(lineData))
			}
	}
	
	//This is the update function for a single graph
	var updateGraph = function(data, dash_object, width, height, expand)
		{
			//fill datas for the graph
			var lineData = data;
			var xmin = find_min([data], true);
			var xmax = find_max([data], true);
			var ymin = find_min([data], false);
			var ymax = find_max([data], false);
			
			//add different margins based on data type
			if(dash_object.method == 'Air')
			{
				range_margin = .001
			}
			else
			{
				range_margin = .1
			}
			
			if(ymin < 0)
			{
				ymin = ymin * (1+range_margin)
			}
			else
			{
				ymin = ymin * (1-range_margin)
			}
		
			if (ymax < 0)
			{
				ymax = ymax * (1-range_margin)
			}
			else
			{
				ymax = ymax * (1+range_margin)
			}
			
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
		    .scaleExtent([1, 32])
		    .on("zoom", zoomed),
		    vis = d3.select('#' + dash_object.contentId).call(zoom),
			
		    //functions for automatically creating the x and y axis
			yAxis = d3.svg.axis()
		    .scale(yRange)
		    .tickSize(-1*(WIDTH - MARGINS.left - MARGINS.right),0,0)
			.orient('left')
			.tickSubdivide(true)
			.outerTickSize(0),
			xAxis = d3.svg.axis()
		    .scale(xRange)
		    .orient("bottom")
		    .ticks(3)
		    .tickSubdivide(true)
		    .tickFormat(d3.time.format("\n%m-%d-%Y"))
		    .tickSize(-1*(HEIGHT - MARGINS.top - MARGINS.bottom))
		    .outerTickSize(0);
			
			//updating the legend
			legend(vis, dash_object, width);
			
			//update the position of the x axis
			vis.select(".x_axis")
			.attr("transform", "translate(" + 0 + "," + (HEIGHT - MARGINS.bottom) + ")")
			.transition()
			.call(xAxis)
			.selectAll("text") 
			.attr("y", "7px");
			
			//update the position of the y axis
			vis.select('.y_axis')
			.transition()
			.call(yAxis)
			.selectAll("text") 
			.attr("x", "-3px");
			
			//change the color of the graph grid lines
			vis.selectAll('.tick')
			.selectAll('line')
			.attr('style', 'stroke:rgb(199,199,199)')
			
			//remove the automatic grey graph borders for the x/y axis
			vis.select('.x_axis')
			.selectAll("path") 
			.remove()
			
			vis.select('.y_axis')
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
	
					vis.select('.ylabel')
					.attr('x', -380)
					.attr('y', 45)
					.attr('font-size', 13)
					
					//reposition the usgs logo
					vis.select('.usgs')
					.transition()
					.attr('width', '225px')
					.attr('height', '115px')
					.attr('x', 50)
					.attr('y', 20)
					
					//reposition the right border
					vis.select('.right-border')
					.transition()
					.attr('transform','translate(940,0)')
					.selectAll('line')
					.transition()
					.attr('x2',0)
					.attr('y2', -395)
					.attr('style',"stroke:rgb(0,0,0)")
					
					//reposition the left border
					vis.select('.left-border')
					.transition()
					.attr('transform','translate(50,0)')
					.selectAll('line')
					.transition()
					.attr('x2',0)
					.attr('y2', -395)
					.attr('style',"stroke:rgb(0,0,0)")
					
					//reposition the top border
					vis.select('.top-border')
					.transition()
					.attr('transform','translate(0,165)')
					.selectAll('line')
					.transition()
					.attr('x2',890)
					.attr('y2', 0)
					
					//reposition the bottom border
					vis.select('.bottom-border')
					.transition()
					.attr('transform','translate(0,560)')
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
	
					vis.select('.ylabel')
					.attr('x', -265)
					.attr('y', 45)
					.attr('font-size', 13)
					
					vis.select('.usgs')
					.transition()
					.attr('width', '150px')
					.attr('height', '100px')
					.attr('x', 30)
					.attr('y', 30)
					
					vis.select('.right-border')
					.transition()
					.attr('transform','translate(420,0)')
					.selectAll('line')
					.attr('x2',0)
					.attr('y2', -195)
			
					vis.select('.left-border')
					.transition()
					.attr('transform','translate(50,0)')
					.selectAll('line')
					.attr('x2',0)
					.attr('y2', -195)
					
					vis.select('.top-border')
					.transition()
					.attr('transform','translate(0,165)')
					.selectAll('line')
					.transition()
					.attr('x2',370)
					.attr('y2', 0)
					
					vis.select('.bottom-border')
					.transition()
					.attr('transform','translate(0,360)')
					.selectAll('line')
					.transition()
					.attr('x2',370)
					.attr('y2', 0)
					
				
				}
			
			//The function that draws the graph data in the respective
			//area of the svg element
			var lineFunc = d3.svg.line()
			.x(function(d) {
			  return xRange(d.x);
			})
			.y(function(d) {
			  return yRange(d.y);
			})
			.defined(function(d){ return (xRange(d.x) > MARGINS.left 
					&& xRange(d.x) < WIDTH - MARGINS.right
					&& yRange(d.y) >= MARGINS.top
					&& yRange(d.y) <= HEIGHT - MARGINS.bottom
			)
				})
			.interpolate('linear');
			
			//min of x data
			var min = lineData[0].x
			
			//creates accordion like animation when new data is loaded
			var zeroFunc = d3.svg.line()
			.x(function(d) {
			  return xRange(min);
			})
			.y(function(d) {
			return yRange(d.y);
			})
			.interpolate('linear');
			
			//animation to drawing of graph data
			vis.select('.main_path')
			.transition()
			.attr('d', zeroFunc(lineData))
			.transition()
			.duration(1000)
			.attr('d', lineFunc(lineData))
			
			//function for when data is zoomed or panned
			function zoomed() {
				
				//adjust the axes and reposition their text
				vis.select(".x_axis").call(xAxis)
				  .selectAll("text") 
					.attr("y", "7px")
				  vis.select(".y_axis").call(yAxis)
				  .selectAll("text") 
					.attr("x", "-3px");
				
				//adjust color of all graph grid lines
				vis.selectAll('.tick')
					.selectAll('line')
					.attr('style', 'stroke:rgb(199,199,199)')
				  
				//remove automatic creation of grey lines
				  vis.select('.x_axis')
					.selectAll("path") 
					.remove()
					
				vis.select('.y_axis')
					.selectAll("path") 
					.remove()
					
				//redraw the graph data
				  vis.select('.main_path')
					.attr('d', lineFunc(lineData))
				}
		}
	
	var path_state = [];
	var multi_state_index = -1;
	//This is the graph creation for the single graph
	var makeMultiGraph = function(data, dash_object, colors, state, path_data)
	{
		var xmin = find_min(data, true);
		var xmax = find_max(data, true);
		var ymin = find_min(data, false);
		var ymax = find_max(data, false);
		
		//add different margins based on data type
		if(dash_object.method == 'Air')
		{
			range_margin = .001
		}
		else
		{
			range_margin = .1
		}
		
		if(ymin < 0)
		{
			ymin = ymin * (1+range_margin)
		}
		else
		{
			ymin = ymin * (1-range_margin)
		}
	
		if (ymax < 0)
		{
			ymax = ymax * (1-range_margin)
		}
		else
		{
			ymax = ymax * (1+range_margin)
		}
		
		var 
		WIDTH = 440,
		HEIGHT = 440,
		MARGINS = {
		  top: 165,
		  right: 20,
		  bottom: 80,
		  left: 50
		};
		
		//if single PSD use ordinal x scale, otherwise use datetime x scale
		if (dash_object.contentType == 'single_psd')
		{
			var xRange = d3.scale.linear().range([MARGINS.left, WIDTH - MARGINS.right])
			.domain([xmin, xmax]),
			xAxis = d3.svg.axis()
			  .scale(xRange)
			  .orient('bottom')
			  .tickSize(-1*(HEIGHT - MARGINS.top - MARGINS.bottom),0,0)
			  .outerTickSize(0)
			  .tickSubdivide(true);
		}
		else
		{
			var xRange = d3.time.scale().range([MARGINS.left, WIDTH - MARGINS.right])
			.domain([make_date(xmin), make_date(xmax)]),
			xAxis = d3.svg.axis()
			  .scale(xRange)
			  .orient('bottom')
			  .ticks(3)
			  .tickSize(-1*(HEIGHT - MARGINS.top - MARGINS.bottom),0,0)
			  .tickFormat(d3.time.format("\n%m-%d-%Y"))
			  .outerTickSize(0)
			  .tickSubdivide(true);
		}
		
		//y scale based on boundaries and y min/max
		var yRange = d3.scale.linear().range([HEIGHT - MARGINS.bottom, MARGINS.top])
		.domain([ymin,ymax]),
		
		//function for zoom behavior
		zoom = d3.behavior.zoom()
	    .x(xRange)
	    .y(yRange)
	    .scaleExtent([1, 32])
	    .on("zoom", zoomed),
	    vis = d3.select('#' + dash_object.contentId).call(zoom);
	    
		
		var yAxis = d3.svg.axis()
		  .scale(yRange)
		  .tickSize(-1*(WIDTH - MARGINS.left - MARGINS.right),0,0)
		  .outerTickSize(0)
		  .orient('left')
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
		
		
		
		//This applies the logo
		vis.append('svg:image')
			.attr('width', '150px')
			.attr('height', '100px')
			.attr('x',30)
			.attr('y', 30)
			.attr('class','usgs')
			.attr('xlink:href','./images/usgs.png')
			
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
		
		//This is the y label for the graph
		vis.append('svg:text')
		.attr('class', 'ylabel')
		.attr('x', -265)
		.attr('y', 45)
		.attr('transform',"rotate(-90 20,40)")
		.attr('font-size', 11)
		.attr('font-family', 'Trebuchet MS')
		.text(dash_object.ylabel)
		
		//This calls the x axis and sets the position of all text in the x axis
		vis.append('svg:g')
		.attr('class', 'x_axis')
		.attr('transform', 'translate(0,' + (HEIGHT - MARGINS.bottom) + ')')
		.call(xAxis)
		.selectAll("text") 
		.attr("y", "7px");
		
		//The following creates a solid black line
		//for the right and left border
		vis.select('.x_axis')
		.append('svg:g')
		.attr('class', 'right-border')
		.attr('transform','translate(420,0)')
		.append('svg:line')
		.attr('x2',0)
		.attr('y2', -195)
		.attr('style',"stroke:rgb(0,0,0)")
		
		vis.select('.x_axis')
		.append('svg:g')
		.attr('class', 'left-border')
		.attr('transform','translate(50,0)')
		.append('svg:line')
		.attr('x2',0)
		.attr('y2', -195)
		.attr('style',"stroke:rgb(0,0,0)")
		
		//This removes the auto generated grey line border for the x axis
		vis.select('.x_axis')
		.selectAll("path") 
		.remove()
		
		//This calls the y axis and sets the position of all text in the y axis
		vis.append('svg:g')
		.attr('class', 'y_axis')
		.attr('transform', 'translate(' + (MARGINS.left) + ',0)')
		.call(yAxis)
		.selectAll("text") 
		.attr("x", "-3px");
		
		//This removes the auto generated grey line border for the y axis
		vis.select('.y_axis')
		.selectAll("path") 
		.remove()
		
		//The following creates solid black lines for the top and
		//bottom border of the y axis
		vis.select('.y_axis')
		.append('svg:g')
		.attr('class', 'top-border')
		.attr('transform','translate(0,165)')
		.append('svg:line')
		.attr('x2',370)
		.attr('y2', 0)
		.attr('style',"stroke:rgb(0,0,0)")
		
		vis.select('.y_axis')
		.append('svg:g')
		.attr('class', 'bottom-border')
		.attr('transform','translate(0,360)')
		.append('svg:line')
		.attr('x2',370)
		.attr('y2', 0)
		.attr('style',"stroke:rgb(0,0,0)")
		
		//This adjusts the color of the graph grid lines
		vis.selectAll('.tick')
		.selectAll('line')
		.attr('style', 'stroke:rgb(199,199,199)');
		
		//The following draws the line data to its respective position
		//in the SVG element
		var lineFunc = d3.svg.line()
		.x(function(d) {
		   return  xRange(d.x);
		})
		.y(function(d) {
		  return yRange(d.y);
		})
		.defined(function(d) { return (xRange(d.x) >= MARGINS.left 
				&& xRange(d.x) <= WIDTH - MARGINS.right
				&& yRange(d.y) >= MARGINS.top
				&& yRange(d.y) <= HEIGHT - MARGINS.bottom
		
		)
			})
		.interpolate('linear');
		

		var min = xmin;
		
		//function for accordion like animation to the left
		var zeroFunc = d3.svg.line()
		.x(function(d) {
		  return xRange(min);
		})
		.y(function(d) {
		return yRange(d.y);
		})
		.interpolate('linear');
		
		//To update, (add and remove paths as needed if state is needed)
		if (state != null)
		{
			path_state.push(path_data);
		}
		
		for(var i = 0; i < data.length; i++)
		{
			vis.append('svg:path')
			.attr('class',path_data[i])
			.attr('stroke', colors[i])
			.attr('stroke-width', 2)
			.attr('opacity', .6)
			.attr('fill', 'none')
			.transition()
			.attr('d', zeroFunc(data[i]))
			.transition()
			.duration(1000)
			.attr('d', lineFunc(data[i]));
		}
		
		//This calls the legend
		multi_legend(vis, dash_object, null, path_data, colors);
		
		function zoomed() {
			//call x/y axis and adjust its text position
			  vis.select(".x_axis").call(xAxis)
			  .selectAll("text") 
				.attr("y", "7px")
			  vis.select(".y_axis").call(yAxis)
			  .selectAll("text") 
				.attr("x", "-3px");
			  
			  //adjust color of graph grid lines
			  vis.selectAll('.tick')
				.selectAll('line')
				.attr('style', 'stroke:rgb(199,199,199)')
				
			//remove auto generated grey borders of x/y axis
			  vis.select('.x_axis')
				.selectAll("path") 
				.remove()
				
			vis.select('.y_axis')
				.selectAll("path") 
				.remove()
				
			  for (var i =0; i < data.length; i++)
				{
				  vis.select('.'+path_data[i])
					.attr('d', lineFunc(data[i]))
				}
			}
		
		multi_state_index++;
		return multi_state_index;

	}
	
	
	
	//This is the update function for a single graph
	var updateMultiGraph = function(data, dash_object, colors, width, height, state, expand, path_data)
		{
			var xmin = find_min(data, true);
			var xmax = find_max(data, true);
			var ymin = find_min(data, false);
			var ymax = find_max(data, false);
			
			//apply different margins based on data type
			if(dash_object.method == 'Air')
			{
				range_margin = .001
			}
			else
			{
				range_margin = .1
			}
			
			if(ymin < 0)
			{
				ymin = ymin * (1+range_margin)
			}
			else
			{
				ymin = ymin * (1-range_margin)
			}
		
			if (ymax < 0)
			{
				ymax = ymax * (1-range_margin)
			}
			else
			{
				ymax = ymax * (1+range_margin)
			}
		
			var 
			WIDTH = width, //440,
			HEIGHT = height, //220,
			MARGINS = {
					  top: 165,
					  right: 20,
					  bottom: 80,
					  left: 50
					};
			
			//if single psd create x axis in ordinal scale, otherwise create x axis in datetime scale
			if (dash_object.contentType == 'single_psd')
			{
				var xRange = d3.scale.linear().range([MARGINS.left, WIDTH - MARGINS.right])
				.domain([xmin, xmax]),
				xAxis = d3.svg.axis()
				  .scale(xRange)
				  .orient('bottom')
				  .tickSize(-1*(HEIGHT - MARGINS.top - MARGINS.bottom),0,0)
				  .outerTickSize(0)
				  .tickSubdivide(true);
			}
			else
			{
				var xRange = d3.time.scale().range([MARGINS.left, WIDTH - MARGINS.right])
				.domain([make_date(xmin), make_date(xmax)]),
				xAxis = d3.svg.axis()
				  .scale(xRange)
				  .orient('bottom')
				  .ticks(3)
				  .tickSize(-1*(HEIGHT - MARGINS.top - MARGINS.bottom),0,0)
				  .tickFormat(d3.time.format("\n%m-%d-%Y"))
				  .outerTickSize(0)
				  .tickSubdivide(true);
			}
			var yRange = d3.scale.linear().range([HEIGHT - MARGINS.bottom, MARGINS.top])
			.domain([ymin,ymax]),
			
			zoom = d3.behavior.zoom()
		    .x(xRange)
		    .y(yRange)
		    .scaleExtent([1, 32])
		    .on("zoom", zoomed),
		    vis = d3.select('#' + dash_object.contentId).call(zoom),
			
			yAxis = d3.svg.axis()
		    .scale(yRange)
		    .tickSize(-1*(WIDTH - MARGINS.left - MARGINS.right),0,0)
			.orient('left')
			.tickSubdivide(true)
			.outerTickSize(0);
			
			//update the position of the x axis
			vis.select(".x_axis")
			.attr("transform", "translate(" + 0 + "," + (HEIGHT - MARGINS.bottom) + ")")
			.transition()
			.call(xAxis)
			.selectAll("text") 
			.attr("y", "7px");
			
			//update the position of the y axis
			vis.select('.y_axis')
			.transition()
			.call(yAxis)
			.selectAll("text") 
			.attr("x", "-3px");
			
			//change the color of the graph grid lines
			vis.selectAll('.tick')
			.selectAll('line')
			.attr('style', 'stroke:rgb(199,199,199)')
			
			//remove the automatic grey graph borders for the x/y axis
			vis.select('.x_axis')
			.selectAll("path") 
			.remove()
			
			vis.select('.y_axis')
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
					.text(dash_object.title)
					
					//reposition the xlabel and ylabel
					vis.select('.xlabel')
					.transition()
					.attr('x', WIDTH/2.0 - 25)
					.attr('y', 590)
					.attr('font-size', 13)
	
					vis.select('.ylabel')
					.attr('x', -380)
					.attr('y', 45)
					.attr('font-size', 13)
					
					//reposition the usgs logo
					vis.select('.usgs')
					.transition()
					.attr('width', '225px')
					.attr('height', '115px')
					.attr('x', 50)
					.attr('y', 20)
					
					//reposition the right border
					vis.select('.right-border')
					.transition()
					.attr('transform','translate(940,0)')
					.selectAll('line')
					.transition()
					.attr('x2',0)
					.attr('y2', -395)
					.attr('style',"stroke:rgb(0,0,0)")
					
					//reposition the left border
					vis.select('.left-border')
					.transition()
					.attr('transform','translate(50,0)')
					.selectAll('line')
					.transition()
					.attr('x2',0)
					.attr('y2', -395)
					.attr('style',"stroke:rgb(0,0,0)")
					
					//reposition the top border
					vis.select('.top-border')
					.transition()
					.attr('transform','translate(0,165)')
					.selectAll('line')
					.transition()
					.attr('x2',890)
					.attr('y2', 0)
					
					//reposition the bottom border
					vis.select('.bottom-border')
					.transition()
					.attr('transform','translate(0,560)')
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
					.text(dash_object.title)
					
					vis.select('.xlabel')
					.transition()
					.attr('x', WIDTH/2.0 - 25)
					.attr('y', 390)
					.attr('font-size', 13)
	
					vis.select('.ylabel')
					.attr('x', -265)
					.attr('y', 45)
					.attr('font-size', 13)
					
					vis.select('.usgs')
					.transition()
					.attr('width', '150px')
					.attr('height', '100px')
					.attr('x', 30)
					.attr('y', 30)
					
					vis.select('.right-border')
					.transition()
					.attr('transform','translate(420,0)')
					.selectAll('line')
					.attr('x2',0)
					.attr('y2', -195)
			
					vis.select('.left-border')
					.transition()
					.attr('transform','translate(50,0)')
					.selectAll('line')
					.attr('x2',0)
					.attr('y2', -195)
					
					vis.select('.top-border')
					.transition()
					.attr('transform','translate(0,165)')
					.selectAll('line')
					.transition()
					.attr('x2',370)
					.attr('y2', 0)
					
					vis.select('.bottom-border')
					.transition()
					.attr('transform','translate(0,360)')
					.selectAll('line')
					.transition()
					.attr('x2',370)
					.attr('y2', 0)
					
				
				}
			
			//The following draws the line data to its respective position
			//in the SVG element
			var lineFunc = d3.svg.line()
			.x(function(d) {
			  return xRange(d.x);
			})
			.y(function(d) {
			  return yRange(d.y);
			})
			.defined(function(d) { return (xRange(d.x) >= MARGINS.left 
					&& xRange(d.x) <= WIDTH - MARGINS.right
					&& yRange(d.y) >= MARGINS.top
					&& yRange(d.y) <= HEIGHT - MARGINS.bottom
			
			)
				})
			.interpolate('linear');
			
			//accordion like animation of data to the left
			var zeroFunc = d3.svg.line()
			.x(function(d) {
			  return xRange(xmin);
			})
			.y(function(d) {
			return yRange(d.y);
			})
			.interpolate('linear');
			
			//To update, (add and remove paths as needed if state is needed)
			if (state != null)
			{
				remove_path(vis, path_data, dash_object.state_index);
				add_path(vis, path_data, colors, dash_object.state_index);
			}
			
			multi_legend(vis, dash_object, width, path_data, colors);
			
			//update data and animate
			for (var i =0; i < data.length; i++)
			{
				vis.select('.'+path_data[i])
				.transition()
				.attr('d', zeroFunc(data[i]))
				.transition()
				.duration(1000)
				.attr('d', lineFunc(data[i]))
			}
			
			
			function zoomed() {
				//call x/y axis and adjust its text position
				  vis.select(".x_axis").call(xAxis)
				  .selectAll("text") 
					.attr("y", "7px")
				  vis.select(".y_axis").call(yAxis)
				  .selectAll("text") 
					.attr("x", "-3px");
				  
				  //adjust color of graph grid lines
				  vis.selectAll('.tick')
					.selectAll('line')
					.attr('style', 'stroke:rgb(199,199,199)')
					
				//remove auto generated grey borders of x/y axis
				  vis.select('.x_axis')
					.selectAll("path") 
					.remove()
					
				vis.select('.y_axis')
					.selectAll("path") 
					.remove()
				  
				  for (var i =0; i < data.length; i++)
					{
					  vis.select('.'+path_data[i])
						.attr('d', lineFunc(data[i]))
					}
				}
			
			
		}
	
	//color scale for psd contours
	psd_contour_colors = [
							'#000084',
							'#0000ed',
							'#0049ff',
							'#00a8ff',
							'#2cffca',
							'#77ff80',
							'#ceff29',
							'#ffc800',
							'#ff6800',
							'#fa0f00',
							'#890000'
	                      ]
	
	var color_bar = function(vis, z_range, z_fun)
	{
		// creates a fixed size color bar for PSD Contours graph
		var current_num = z_range[0];
		var index = 0;
		var bars_per_color = 3;
		var x = 350;
		var z_range_index = 0;
		var num_increase = z_range[z_range.length - 1] / 170.906
		
		while(current_num <= z_range[z_range.length - 1])
		{
			
			vis.append('svg:line')
			.attr('x1',x)
			.attr('x2',x)
			.attr('y1', 70)
			.attr('y2', 90)
			.attr('stroke',z_fun(current_num))
			
			x += 1;
			index += 1;
			
			//if current number equals a z range index apply PSD label and PSD label tick
			if (current_num >= z_range[z_range_index])
			{
				vis.append('svg:line')
				.attr('x1',x)
				.attr('x2',x)
				.attr('y1', 85)
				.attr('y2', 95)
				.attr('stroke','#000000')
				
						
			    var number = Math.round(z_range[z_range_index] * 100000) / 100000.0
				vis.append('svg:text')
				.attr('x', x)
				.attr('y', 100)
				.attr('font-size', 11)
				.attr('transform',"rotate(30 " + x + "," + 100 + ")")
				.attr('font-family', 'Trebuchet MS')
				.text(number)
				
				
				z_range_index += 1;
			}
			
			//if the index is greater than bars per color move to new color
			if (index >= bars_per_color)
			{
				index = 0;
				current_num += num_increase;
			}
			
			
		}
		//This applies the last PSD label tick
		vis.append('svg:line')
		.attr('x1',x-1)
		.attr('x2',x)
		.attr('y1', 85)
		.attr('y2', 95)
		.attr('stroke','#000000')
		
		//This applies the last PSD label
		var number = Math.round(z_range[z_range_index] * 100000) / 100000.0
		vis.append('svg:text')
		.attr('x', x-1)
		.attr('y', 100)
		.attr('font-size', 11)
		.attr('transform',"rotate(30 " + x + "," + 100 + ")")
		.attr('font-family', 'Trebuchet MS')
		.text(number)
		
		//This creates the border boundary of the color bar
		vis.append('svg:line')
		.attr('x1',350)
		.attr('x2',x)
		.attr('y1', 70)
		.attr('y2', 70)
		.attr('stroke','#000000')
		vis.append('svg:line')
		.attr('x1',350)
		.attr('x2',x)
		.attr('y1', 90)
		.attr('y2', 90)
		.attr('stroke','#000000')
		vis.append('svg:line')
		.attr('x1',350)
		.attr('x2',350)
		.attr('y1', 70)
		.attr('y2', 90)
		.attr('stroke','#000000')
		vis.append('svg:line')
		.attr('x1', x)
		.attr('x2', x)
		.attr('y1', 70)
		.attr('y2', 90)
		.attr('stroke','#000000')
		
		//This applies the label to the color bar
		vis.append('svg:text')
		.attr('x', 480)
		.attr('y', 60)
		.attr('font-size', 14)
		.attr('font-family', 'Trebuchet MS')
		.text("Power Spectral Density in m^2/hz")
		
		
		
		
	}
	
	var psd_graph = function(data, dash_object, psd_post)
	{
		
		//This is a white rectangle created in order to allow 
		//the image capture to have a white background
		
		//This is the fill data to be graphed
		var xmin = data['x_range'][0]
		var xmax = data['x_range'][1]
		var ymin = data['y_range'][0]
		var ymax = data['y_range'][1]
		
		//These are the dimensions of the graph
		var 
		WIDTH = 960,
		HEIGHT = 640,
		MARGINS = {
		  top: 165,
		  right: 20,
		  bottom: 80,
		  left: 50
		},
		
		//Establishes the horizontal and vertical boundaries for the graph data
		xRange = d3.time.scale().range([MARGINS.left, WIDTH - MARGINS.right])
		.domain([make_date(xmin), make_date(xmax)]),
		xRange2 = d3.time.scale().range([make_date(xmin), make_date(xmax)])
		.domain([MARGINS.left, WIDTH - MARGINS.right]),
		yRange = d3.scale.pow().exponent(-1).range([MARGINS.top, HEIGHT - MARGINS.bottom ])
		.domain([ymax, ymin]),
		yRange2 = d3.scale.pow().exponent(-1).range([MARGINS.top, HEIGHT - MARGINS.bottom ])
		.domain([ymin, ymax])
		zRange = d3.scale.linear().range(psd_contour_colors)
		.domain(data['z_range']);
	
		//creates ranges for use with contouring library
		var xDom = d3.range(make_date(xmin), make_date(xmax), 512000),
			yDom = d3.range(ymin,ymax,.02),
			zDom = d3.range(data['z_range'][0],data['z_range'][data['z_range'].length - 1],.1);
		
		var c = new Conrec;
		c.contour(data['z'], 0, xDom.length - 1, 0, yDom.length - 1, xDom, yDom, zDom.length, zDom);
		
		//This triggers the zoom behavior for the graph data
//		var zoom = d3.behavior.zoom()
//	    .x(xRange)
//	    .y(yRange)
//	    .scaleExtent([1, 32])
//	    .on("zoom", zoomed),
	    vis = d3.select('#' + dash_object.contentId),
	    //.call(zoom),
	    
	    //This calls the x and y axis for the graph
		xAxis = d3.svg.axis()
		  .scale(xRange)
		  .orient('bottom')
		  .ticks(3)
		  .tickSize(-1*(HEIGHT - MARGINS.top - MARGINS.bottom),0,0)
		  .tickFormat(d3.time.format("\n%m-%d-%Y \n%H:%M"))
		  .outerTickSize(0)
		  .tickSubdivide(true),
		yAxis = d3.svg.axis()
		  .scale(yRange)
		  .tickSize(-1*(WIDTH - MARGINS.left - MARGINS.right),0,0)
		  .tickValues([1, 2, 4, 9.8, 18])
		  .outerTickSize(0)
		  .orient('left')
		  .tickSubdivide(true);
		
		//This is a white rectangle created in order to allow 
		//the image capture to have a white background
		vis.append('svg:rect')
		.attr('class', 'background')
		.attr('width', 960)
		.attr('height', 636)
		.attr('style', 'fill:rgb(255,255,255)')
		.attr('x', 0)
		.attr('y', 0)
		.on('mouseover', mouseOut)
		
		//This applies base color for PSD contour background
		vis.append('svg:rect')
		.attr('class', 'graph_background')
		.attr('width', WIDTH - MARGINS.right - MARGINS.left)
		.attr('height', HEIGHT - MARGINS.top - MARGINS.bottom)
		.attr('style', 'fill:'+psd_contour_colors[0])
		.attr('x', MARGINS.left)
		.attr('y', MARGINS.top)
		
		//applies the color bar
		color_bar(vis, data['z_range'], zRange);

		//This applies the logo
		vis.append('svg:image')
			.attr('width', '225px')
			.attr('height', '115px')
			.attr('x', 50)
			.attr('y', 20)
			.attr('class','usgs')
			.attr('xlink:href','./images/usgs.png')
			
		//This is the title for the graph
		vis.append('svg:text')
		.attr('class','title')
		.attr('x', WIDTH/2.0 - 145)
		.attr('y', 155)
		.attr('font-size', 20)
		.attr('font-family', 'Trebuchet MS')
		.text(dash_object.title)
		
		//This is the x label for the graph
		vis.append('svg:text')
		.attr('class', 'xlabel')
		.attr('x', WIDTH/2.0 - 25)
		.attr('y', 590)
		.attr('font-size', 13)
		.attr('font-size', 11)
		.attr('font-family', 'Trebuchet MS')
		.text(dash_object.xlabel)
		
		//This is the y label for the graph
		vis.append('svg:text')
		.attr('class', 'ylabel')
		.attr('x', -380)
		.attr('y', 45)
		.attr('font-size', 13)
		.attr('transform',"rotate(-90 20,40)")
		.attr('font-family', 'Trebuchet MS')
		.text(dash_object.ylabel)
		
		
		
		//The following draws the line data to its respective position
		//in the SVG element
		var lineFunc = d3.svg.line()
		.x(function(d) {
		   return  xRange(d.x);
		})
		.y(function(d) {
		  return yRange(d.y);
		})
		.defined(function(d) { return (
				xRange(d.x) > MARGINS.left 
				&& xRange(d.x) < WIDTH - MARGINS.right
				&& yRange(d.y) < HEIGHT - MARGINS.bottom
				&& yRange(d.y) > MARGINS.top
		)
			})
		.interpolate('linear');

		//This applies the calculated contours
		vis.selectAll("path")
	    .data(c.contourList())
	    .enter().append("path")
	      .style("fill",function(d) { return zRange(d.level);})
	      //.style("stroke","black")
	      .attr("d", d3.svg.line()
	    	      .x(function(d) { return xRange(d.x); })
	    	      .y(function(d) { return yRange2(d.y); }));
		
		//This calls the x axis and sets the position of all text in the x axis
		vis.append('svg:g')
		.attr('class', 'x_axis')
		.attr('transform', 'translate(0,' + (HEIGHT - MARGINS.bottom) + ')')
		.call(xAxis)
		.selectAll("text") 
		.attr("y", "7px");
		
		//The following creates a solid black line
		//for the right and left border
		vis.select('.x_axis')
		.append('svg:g')
		.attr('class', 'right-border')
		.attr('transform','translate(940,0)')
		.append('svg:line')
		.attr('x2',0)
		.attr('y2', -395)
		.attr('style',"stroke:rgb(0,0,0)")

		vis.select('.x_axis')
		.append('svg:g')
		.attr('class', 'left-border')
		.attr('transform','translate(50,0)')
		.append('svg:line')
		.attr('x2',0)
		.attr('y2', -395)
		.attr('style',"stroke:rgb(0,0,0)")
		
		//This removes the auto generated grey line border for the x axis
		vis.select('.x_axis')
		.selectAll("path") 
		.remove()
		
		//This calls the y axis and sets the position of all text in the y axis
		vis.append('svg:g')
		.attr('class', 'y_axis')
		.attr('transform', 'translate(' + (MARGINS.left) + ',0)')
		.call(yAxis)
		.selectAll("text") 
		.attr("x", "-3px");
		
		//This removes the auto generated grey line border for the y axis
		vis.select('.y_axis')
		.selectAll("path") 
		.remove()
		
		//The following creates solid black lines for the top and
		//bottom border of the y axis
		vis.select('.y_axis')
		.append('svg:g')
		.attr('class', 'top-border')
		.attr('transform','translate(0,165)')
		.append('svg:line')
		.attr('x2',890)
		.attr('y2', 0)
		.attr('style',"stroke:rgb(0,0,0)")
		
		vis.select('.y_axis')
		.append('svg:g')
		.attr('class', 'bottom-border')
		.attr('transform','translate(0,560)')
		.append('svg:line')
		.attr('x2',890)
		.attr('y2', 0)
		.attr('style',"stroke:rgb(0,0,0)")
		
		//This adjusts the color of the graph grid lines
		vis.selectAll('.tick')
		.selectAll('line')
		.attr('style', 'stroke:rgb(199,199,199)');
		
		vis.append('svg:rect')
		.attr('width', WIDTH - MARGINS.right - MARGINS.left)
		.attr('height', HEIGHT - MARGINS.top - MARGINS.bottom)
		.attr('class', 'foreground')
		.attr('x', MARGINS.left)
		.attr('y', MARGINS.top)
		.attr('opacity', 0.0)
		.on('mouseover', mouseOver)
		.on('click', function(){
			x_coord = d3.mouse(this)[0];
			time = xRange2(x_coord);
			psd_post(0, time);
		})

		var graph_line = null;
		
		//Creates yelow line to help user identify where in graph the
		//single psd will be generated from
		function mouseOver(){
			
			var x_coord = d3.mouse(this)[0];
			
			if (graph_line == null)
			{
				vis.append('svg:line')
				.attr('class', 'graph_line')
				.attr('y1', MARGINS.top)
				.attr('y2', HEIGHT - MARGINS.bottom)
				.attr('x1', x_coord)
				.attr('x2', x_coord)
				.attr('stroke', 'yellow')
				.on('click', function(){
					x_coord = d3.mouse(this)[0];
					time = xRange2(x_coord);
					psd_post(0, time);
				})
				
				graph_line = 0;
				
				vis.select('.foreground')
				.on('mousemove', function(){
					
					var x_coord = d3.mouse(this)[0];
					
					vis.select('.graph_line')
					.transition()
					.attr('x1', x_coord)
					.attr('x2', x_coord)
				})
			}	
		}
		
		//removes the yellow line that assists the user
		function mouseOut(){
			
			console.log('mouseout')
			if (graph_line != null)
			{
				vis.select('.foreground')
				.on('mousemove', null);
				
				vis.select('.graph_line').remove();
				graph_line = null;
			}
			
			
		}
//		//function to call when zooming or panning
//		function zoomed() {
//			
//			//call x/y axis and adjust its text position
//			  vis.select(".x_axis").call(xAxis)
//			  .selectAll("text") 
//				.attr("y", "7px")
//			  vis.select(".y_axis").call(yAxis)
//			  .selectAll("text") 
//				.attr("x", "-3px");
//			  
//			  //adjust color of graph grid lines
//			  vis.selectAll('.tick')
//				.selectAll('line')
//				.attr('style', 'stroke:rgb(199,199,199)')
//				
//			//remove auto generated grey borders of x/y axis
//			  vis.select('.x_axis')
//				.selectAll("path") 
//				.remove()
//				
//			vis.select('.y_axis')
//				.selectAll("path") 
//				.remove()
//				
//			//redraw line data based on current position
//			  vis.select('.main_path')
//				.attr('d', lineFunc(lineData))
//			}
	}
	
	
	//Add path to state so that the path can be removed later on
	var add_path = function(vis, path_data, colors, state_index)
	{
		var new_paths = [];
		get_path_state_colors = false;
		for (var p = 0; p < path_data.length; p++)
		{
				new_paths.push(path_data[p]);
				
				vis.append('svg:path')
				.attr('class',path_data[p])
				.attr('stroke', colors[p])
				.attr('stroke-width', 2)
				.attr('opacity', .6)
				.attr('fill', 'none')
		}
		
		
		var tempstate = [];
		var found_null = false;
		var new_path_idx = 0;
			
		for (var k = 0; k < new_paths.length; k++)
		{
			path_state[state_index].push(new_paths[k]);
		}
	}
	
	//Look for paths that are not in the updated data and remove if necessary
	var remove_path = function(vis, path_data, state_index)
	{
		
		for (var i = 0; i < path_state[state_index].length; i++)
			{
					vis.select('.legend_line'+path_state[state_index][i])
					.remove();
					vis.select('.line_text'+path_state[state_index][i])
					.remove();
					
					
					vis.select('.'+path_state[state_index][i])
					.remove();
					path_state[state_index][i] = 'removed';
			}
	}
	
	var find_min = function(data, x)
	{
		min = null;
		for(var i = 0; i < data.length; i++)
		{
			if(x == true)
			{
				if (min == null)
				{
					min = data[i][0].x
				}
				else
				{
					if (data[i][0].x < min)
					{
						min = data[i][0].x;
					}
				}
			} else
			{
				for(var j =0; j < data[i].length; j++)
				{
					if (min == null)
					{
						min = data[i][j].y
					}
					else
					{
						if (data[i][j].y < min)
						{
							min = data[i][j].y;
						}
					}
				}
			}
		}
		return min;
	}
	
	var find_max = function(data,x)
	{
		max = null;
		for(var i = 0; i < data.length; i++)
		{
			if(x == true)
			{
				if (max == null)
				{
					max = data[i][data[i].length - 1].x
				}
				else
				{
					if (data[i][data[i].length - 1].x > max)
					{
						max = data[i][data[i].length - 1].x;
					}
				}
			} else
			{
				for(var j =0; j < data[i].length; j++)
				{
					if (max == null)
					{
						max = data[i][j].y
					}
					else
					{
						if (data[i][j].y > max)
						{
							max = data[i][j].y;
						}
					}
				}
			}
		}
		return max;
	}
	
	var make_date = function(date)
	{
		return new Date(date);
	}

	
	
