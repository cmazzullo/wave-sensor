$(function(){
	
	$.ajax({
		type: 'GET',
		url: "http://idpgis.ncep.noaa.gov/arcgis/rest/services/NOAA/NOAA_Estuarine_Bathymetry/MapServer/legend?f=pjson",
		datatype: 'jsonp',
		success: function(data){
			
			data = JSON.parse(data);
			labels_high = [];
			labels_low = [];
			for (var i = 1; i < data['layers'].length; i++)
			{
				
				if (data['layers'][i].layerName.indexOf("Bathymetry") != -1)
				{
					legend = data['layers'][i].legend;
					labels_high.push(parseFloat(legend[0].label.replace("High : ", "")));
					labels_low.push(parseFloat(legend[2].label.replace("Low : ", "")));
				}
			}
			
			console.log(d3.min(labels_high) + ' - ' + d3.max(labels_high));
			console.log(d3.min(labels_low) + ' - ' + d3.max(labels_low));
		}
	})
	
})