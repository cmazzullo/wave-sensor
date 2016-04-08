<!DOCTYPE html>
<meta charset="utf-8">
<style>

body {
margin:0px 50px;
}



.bar {
  fill: steelblue;
}

.x_axis text, .y_axis text {
  font: 10px sans-serif;
}

#visualization{
cursor: pointer
}

.x_axis path, .y_axis path,
.x_axis line, .y_axis line {
  fill: none;
  stroke: #CCC;
  /*shape-rendering: crispEdges;*/
}

#header {
background-color: #007150;
height: 150px;
border: 1px solid black;
}

#sidebar{
float: left;
background-color: #d9d9d9;
margin-right: 50px;
min-height: 700px;
padding: 20px;
border: 1px solid black;
border-top: none;
}

#mainGraph
{
border-right:1px solid black;
border-bottom:1px solid black;
min-height: 700px;
padding: 20px;
background-color: #e9e9e9;
}

#main_logo{
margin: 20px 40px;
}

.dash_tile{
display: inline-block;
float: left;
margin-left: 20px;
border: black 2px solid;
background-color: white;
height:260px;
width: 470px;
padding: 0px;
margin-bottom: 20px;
}

.dash_title{
background-color: #dcdcdc;
padding-top: 10px;
padding-bottom: -3px;
font-weight: bold;
height: 30px;
padding-left: 10px;
border-bottom: 2px solid black;
}

.dash_content{
width: 470px;
height: 218px;
margin: auto;
display:block;
}
</style>
<div id="header">
<img id="main_logo" src="wavelab.png" />
</div>
<div id="sidebar">

<form id="graphForm">
<table>
<tr><td>Start Time:</td><td><input type="text" id="start_date" value="1453503600000"/></td></tr>
<tr><td>End Time:</td><td><input type="text" id="end_date" value="1453817939750"/></td></tr>
<tr><td></td><td><button>Submit</button></td></tr>
</table>
</form>
</div>

<div id="mainGraph">

<div class="dash_tile">
<div class="dash_title">Raw Instrument Data <button class="expand">Expand</button></div>
<svg id="visualization" width="440" height="220"></svg>
</div>

<div class="dash_tile">
<div class="dash_title">Instrument Location <button class="expand">Expand</button></div>
<div id="map" class="dash_content"></div>
</div>

<div class="dash_tile">
<div class="dash_title">Raw Instrument Data <button class="expand">Expand</button></div>
<svg id="visualization" width="440" height="220"></svg>
</div>

<div class="dash_tile">
<div class="dash_title">Instrument Location <button class="expand">Expand</button></div>
<div id="map" class="dash_content"></div>
</div>

</div>

<script src="https://code.jquery.com/jquery-1.12.0.min.js"></script>
<script src="https://d3js.org/d3.v3.min.js" charset="utf-8"></script>
<script async defer
      src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBKbkdjgPWlg8vSn-yDSHCp3ucmcm93bAQ">
</script>
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
			
	var made_graph = false;
	
	$('.expand').click(function(){
		
		var elem = $(this)
		var width = parseInt($(this).parent().parent().css('width'));
		if (width < 900)
			{
			$(this).parent().parent().animate({
			    height: "480px",
			    width: "960px"
			  }, 1000, function() {
			    elem.text('Shrink');
			  });
			}
		else{
			$(this).parent().parent().animate({
			    height: "260px",
			    width: "470px"
			  }, 1000, function() {
			    elem.text('Expand');
			  });
		}
		
	});
	
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
			if (made_graph == false)
				{
					var myLatLng = {lat: data['latitude'], lng: data['longitude']};

					map = new google.maps.Map(document.getElementById('map'), {
					  center: myLatLng,
					  zoom: 14
					});
					
					marker = new google.maps.Marker({
						position: myLatLng,
						label: 'Instrument',
						map: map
					});
					
					
					makeGraph(data['data']);
					made_graph = true;
				}
			else
				{
					updateGraph(data['data']);
				}
				
		});
		
	})
	
	
	
	var updateGraph = function(data)
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
		xRange = d3.scale.linear().range([MARGINS.left, WIDTH - MARGINS.right])
		.domain([d3.min(lineData, function(d) {
		  return (d.x);
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
	    vis = d3.select('#visualization').call(zoom),
		
		xAxis = d3.svg.axis()
	    .scale(xRange)
	    .orient("bottom")
	    .ticks(6)
	    .tickSize(-1*(HEIGHT - MARGINS.top - MARGINS.bottom))
	    .outerTickSize(0),

		yAxis = d3.svg.axis()
	    .scale(yRange)
	    .tickSize(-1*(WIDTH - MARGINS.left - MARGINS.right),0,0)
		.orient('left')
		.tickSubdivide(true)
		.outerTickSize(0);
		
		
		
		vis.select(".x_axis")
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
	
	var makeGraph = function(data)
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
		xRange = d3.scale.linear().range([MARGINS.left, WIDTH - MARGINS.right])
		.domain([d3.min(lineData, function(d) {
		  return (d.x);
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
	    vis = d3.select('#visualization').call(zoom),
	    
		xAxis = d3.svg.axis()
		  .scale(xRange)
		  .orient('bottom')
		  .ticks(6)
		  .tickSize(-1*(HEIGHT - MARGINS.top - MARGINS.bottom),0,0)
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
		.attr('stroke', 'blue')
		.attr('stroke-width', 2)
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
	
	
});
</script>