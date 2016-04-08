<!DOCTYPE html>
<meta charset="utf-8">
<style>

.bar {
  fill: steelblue;
}

.axis text {
  font: 10px sans-serif;
}

.axis path,
.axis line {
  fill: none;
  stroke: #000;
  shape-rendering: crispEdges;
}



</style>
<svg id="visualization" width="1000" height="500"></svg>

<form id="graphForm">
<ul>
<li>Start Time: <input type="text" id="start_date" /></li>
<li>End Time: <input type="text" id="end_date" /></li>
<li><button>Submit</button>
</ul>
</form>
<script src="https://code.jquery.com/jquery-1.12.0.min.js"></script>
<script src="https://d3js.org/d3.v3.min.js" charset="utf-8"></script>
<script>
$(function() {

	/*$.ajax({
		type: 'GET',
		url: 'http://localhost:8080/get',
		datatype: 'JSON',
		error: function()
		{
			console.log('error');
		}
	})
	.done(function(data) {
			makeGraph(data['data']);
	});*/
			
			
	$('#graphForm').submit(function(event){
		event.preventDefault();
		$.ajax({
			type: 'POST',
			url: 'http://localhost:8080/newGraph',
			data: {
				start_time: $('#start_date').val(),
				end_time: $('#end_date').val()
			},
			datatype: 'JSON',
			error: function()
			{
				console.log('error');
			}
		})
		.done(function(data) {
				makeGraph(data['data']);
		});
		
	})
	
	var makeGraph = function(data)
	{
		var lineData = data;
		
		var vis = d3.select('#visualization'),
		WIDTH = 1000,
		HEIGHT = 500,
		MARGINS = {
		  top: 20,
		  right: 20,
		  bottom: 20,
		  left: 50
		},
		xRange = d3.scale.linear().range([MARGINS.left, WIDTH - MARGINS.right])
		.domain([d3.min(lineData, function(d) {
		  return d.x;
		}), d3.max(lineData, function(d) {
		  return d.x;
		})]),
		yRange = d3.scale.linear().range([HEIGHT - MARGINS.top, MARGINS.bottom])
		.domain([d3.min(lineData, function(d) {
		  return d.y;
		}), d3.max(lineData, function(d) {
		  return d.y;
		})]),
		xAxis = d3.svg.axis()
		  .scale(xRange)
		  .tickSize(5)
		  .tickSubdivide(true),
		yAxis = d3.svg.axis()
		  .scale(yRange)
		  .tickSize(5)
		  .orient('left')
		  .tickSubdivide(true);
		
		vis.append('svg:g')
		.attr('class', 'x axis')
		.attr('transform', 'translate(0,' + (HEIGHT - MARGINS.bottom) + ')')
		.call(xAxis);
		
		vis.append('svg:g')
		.attr('class', 'y axis')
		.attr('transform', 'translate(' + (MARGINS.left) + ',0)')
		.call(yAxis);
		
		var lineFunc = d3.svg.line()
		.x(function(d) {
		  return xRange(d.x);
		})
		.y(function(d) {
		  return yRange(d.y);
		})
		.interpolate('linear');
		
		vis.append('svg:path')
		.attr('d', lineFunc(lineData))
		.attr('stroke', 'blue')
		.attr('stroke-width', 2)
		.attr('fill', 'none');
		
	}
	
	
});
</script>