	//This is the graph creation for the single graph
	var makeGraph = function(data, dash_object)
	{
		var lineData = data;
		
		var 
		WIDTH = 440,
		HEIGHT = 220,
		MARGINS = {
		  top: 20,
		  right: 20,
		  bottom: 20,
		  left: 50
		},
		xRange = d3.time.scale().range([MARGINS.left, WIDTH - MARGINS.right])
		.domain([d3.min(lineData, function(d) {
		  return (make_date(d.x));
		}), d3.max(lineData, function(d) {
		  return (make_date(d.x));
		})]),
		yRange = d3.scale.linear().range([HEIGHT - MARGINS.top, MARGINS.bottom])
		.domain([d3.min(lineData, function(d) {
		  return (d.y);
		}), d3.max(lineData, function(d) {
		  return (d.y);
		})]),
		
		zoom = d3.behavior.zoom()
	    .x(xRange)
	    .y(yRange)
	    .scaleExtent([1, 32])
	    .on("zoom", zoomed),
	    vis = d3.select('#' + dash_object.contentId).call(zoom),
	    
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
		
		vis.append('svg:g')
		.attr('class', 'x_axis')
		.attr('transform', 'translate(0,' + (HEIGHT - MARGINS.bottom) + ')')
		.call(xAxis);
		
		vis.append('svg:g')
		.attr('class', 'y_axis')
		.attr('transform', 'translate(' + (MARGINS.left) + ',0)')
		.call(yAxis);
		
		var lineFunc = d3.svg.line()
		.x(function(d) {
		   return  xRange(d.x);
		})
		.y(function(d) {
		  return yRange(d.y);
		})
		.defined(function(d) { return (xRange(d.x) >= MARGINS.left 
				&& xRange(d.x) <= WIDTH - MARGINS.right
				&& yRange(d.y) >= MARGINS.bottom
				&& yRange(d.y) <= HEIGHT - MARGINS.top
		
		)
			})
		.interpolate('linear');
		

		var min = lineData[0].x
		
		var zeroFunc = d3.svg.line()
		.x(function(d) {
		  return xRange(min);
		})
		.y(function(d) {
		return yRange(d.y);
		})
		.interpolate('linear');
		
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
		
		function zoomed() {
			  vis.select(".x_axis").call(xAxis);
			  vis.select(".y_axis").call(yAxis);
			  vis.select('.main_path')
				.attr('d', lineFunc(lineData))
			}

	}
	
	//This is the update function for a single graph
	var updateGraph = function(data, dash_object, width, height)
		{
			var lineData = data;
			
			var 
			WIDTH = width, //440,
			HEIGHT = height, //220,
			MARGINS = {
			  top: 20,
			  right: 20,
			  bottom: 20,
			  left: 50
			},
			xRange = d3.time.scale().range([MARGINS.left, WIDTH - MARGINS.right])
			.domain([d3.min(lineData, function(d) {
			  return (make_date(d.x));
			}), d3.max(lineData, function(d) {
			  return (d.x);
			})]),
			yRange = d3.scale.linear().range([HEIGHT - MARGINS.top, MARGINS.bottom])
			.domain([d3.min(lineData, function(d) {
			  return (d.y);
			}), d3.max(lineData, function(d) {
			  return (d.y);
			})]),
			
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
			.outerTickSize(0),
			xAxis = d3.svg.axis()
		    .scale(xRange)
		    .orient("bottom")
		    .ticks(3)
		    .tickSubdivide(true)
		    .tickFormat(d3.time.format("\n%m-%d-%Y"))
		    .tickSize(-1*(HEIGHT - MARGINS.top - MARGINS.bottom))
		    .outerTickSize(0);
			
			vis.select(".x_axis")
			.attr("transform", "translate(" + 0 + "," + (HEIGHT - MARGINS.bottom) + ")")
			.transition()
			.call(xAxis);
			
			vis.select('.y_axis')
			.transition()
			.call(yAxis);
			
			var lineFunc = d3.svg.line()
			.x(function(d) {
			  return xRange(d.x);
			})
			.y(function(d) {
			  return yRange(d.y);
			})
			.defined(function(d) { return (xRange(d.x) >= MARGINS.left 
					&& xRange(d.x) <= WIDTH - MARGINS.right
					&& yRange(d.y) >= MARGINS.bottom
					&& yRange(d.y) <= HEIGHT - MARGINS.top
			
			)
				})
			.interpolate('linear');
			
			var min = lineData[0].x
			
			var zeroFunc = d3.svg.line()
			.x(function(d) {
			  return xRange(min);
			})
			.y(function(d) {
			return yRange(d.y);
			})
			.interpolate('linear');
			
			
			vis.select('.main_path')
			.transition()
			.attr('d', zeroFunc(lineData))
			.transition()
			.duration(1000)
			.attr('d', lineFunc(lineData))
			
		
			
			function zoomed() {
				  vis.select(".x_axis").call(xAxis);
				  vis.select(".y_axis").call(yAxis);
				  vis.select('.main_path')
					.attr('d', lineFunc(lineData))
				}
		}
	
	//This is the graph creation for the single graph
	var makeMultiGraph = function(data, dash_object, color)
	{
		var xmin = find_min(data, true);
		var xmax = find_max(data, true);
		var ymin = find_min(data, false);
		var ymax = find_max(data, false);
		
		console.log(ymin +'' + ymax);
		
		var 
		WIDTH = 440,
		HEIGHT = 220,
		MARGINS = {
		  top: 20,
		  right: 20,
		  bottom: 20,
		  left: 50
		},
		xRange = d3.time.scale().range([MARGINS.left, WIDTH - MARGINS.right])
		.domain([make_date(xmin), make_date(xmax)]),
		yRange = d3.scale.linear().range([HEIGHT - MARGINS.top, MARGINS.bottom])
		.domain([ymin,ymax]),
		
		zoom = d3.behavior.zoom()
	    .x(xRange)
	    .y(yRange)
	    .scaleExtent([1, 32])
	    .on("zoom", zoomed),
	    vis = d3.select('#' + dash_object.contentId).call(zoom),
	    
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
		
		vis.append('svg:g')
		.attr('class', 'x_axis')
		.attr('transform', 'translate(0,' + (HEIGHT - MARGINS.bottom) + ')')
		.call(xAxis);
		
		vis.append('svg:g')
		.attr('class', 'y_axis')
		.attr('transform', 'translate(' + (MARGINS.left) + ',0)')
		.call(yAxis);
		
		var lineFunc = d3.svg.line()
		.x(function(d) {
		   return  xRange(d.x);
		})
		.y(function(d) {
		  return yRange(d.y);
		})
		.defined(function(d) { return (xRange(d.x) >= MARGINS.left 
				&& xRange(d.x) <= WIDTH - MARGINS.right
				&& yRange(d.y) >= MARGINS.bottom
				&& yRange(d.y) <= HEIGHT - MARGINS.top
		
		)
			})
		.interpolate('linear');
		

		var min = xmin;
		
		var zeroFunc = d3.svg.line()
		.x(function(d) {
		  return xRange(min);
		})
		.y(function(d) {
		return yRange(d.y);
		})
		.interpolate('linear');
		
		for(var i = 0; i < data.length; i++)
		{
			vis.append('svg:path')
			.attr('class','main_path' + (i+1))
			.attr('stroke', color[i])
			.attr('stroke-width', 2)
			.attr('opacity', .6)
			.attr('fill', 'none')
			.transition()
			.attr('d', zeroFunc(data[i]))
			.transition()
			.duration(1000)
			.attr('d', lineFunc(data[i]));
		}
		
		function zoomed() {
			  vis.select(".x_axis").call(xAxis);
			  vis.select(".y_axis").call(yAxis);
			  for (var i =0; i < data.length; i++)
				{
				  vis.select('.main_path' + (i+1))
					.attr('d', lineFunc(data[i]))
				}
			}

	}
	
	//This is the update function for a single graph
	var updateMultiGraph = function(data, dash_object, width, height)
		{
			var xmin = find_min(data, true);
			var xmax = find_max(data, true);
			var ymin = find_min(data, false);
			var ymax = find_max(data, false);
		
			var 
			WIDTH = width, //440,
			HEIGHT = height, //220,
			MARGINS = {
			  top: 20,
			  right: 20,
			  bottom: 20,
			  left: 50
			},
			xRange = d3.time.scale().range([MARGINS.left, WIDTH - MARGINS.right])
			.domain([make_date(xmin), make_date(xmax)]),
			yRange = d3.scale.linear().range([HEIGHT - MARGINS.top, MARGINS.bottom])
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
			.outerTickSize(0),
			xAxis = d3.svg.axis()
		    .scale(xRange)
		    .orient("bottom")
		    .ticks(3)
		    .tickSubdivide(true)
		    .tickFormat(d3.time.format("\n%m-%d-%Y"))
		    .tickSize(-1*(HEIGHT - MARGINS.top - MARGINS.bottom))
		    .outerTickSize(0);
			
			vis.select(".x_axis")
			.attr("transform", "translate(" + 0 + "," + (HEIGHT - MARGINS.bottom) + ")")
			.transition()
			.call(xAxis);
			
			vis.select('.y_axis')
			.transition()
			.call(yAxis);
			
			var lineFunc = d3.svg.line()
			.x(function(d) {
			  return xRange(d.x);
			})
			.y(function(d) {
			  return yRange(d.y);
			})
			.defined(function(d) { return (xRange(d.x) >= MARGINS.left 
					&& xRange(d.x) <= WIDTH - MARGINS.right
					&& yRange(d.y) >= MARGINS.bottom
					&& yRange(d.y) <= HEIGHT - MARGINS.top
			
			)
				})
			.interpolate('linear');
			
			
			
			var zeroFunc = d3.svg.line()
			.x(function(d) {
			  return xRange(xmin);
			})
			.y(function(d) {
			return yRange(d.y);
			})
			.interpolate('linear');
			
			for (var i =0; i < data.length; i++)
			{
				vis.select('.main_path' + (i+1))
				.transition()
				.attr('d', zeroFunc(data[i]))
				.transition()
				.duration(1000)
				.attr('d', lineFunc(data[i]))
			}
			
			
			function zoomed() {
				  vis.select(".x_axis").call(xAxis);
				  vis.select(".y_axis").call(yAxis);
				  
				  for (var i =0; i < data.length; i++)
					{
					  vis.select('.main_path' + (i+1))
						.attr('d', lineFunc(data[i]))
					}
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
