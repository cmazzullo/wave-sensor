
//This will eventually not be necessary as the code
//will be querying a thredds server
$.getScript( "./js/dummy_data.js" )
  .done(function( script, textStatus ) {
    console.log( 'success d data', textStatus );
    
  })
  .fail(function( jqxhr, settings, exception ) {
    console.log('fail d data')
});

var query_server = function(lats, lons)
{
//		$.ajax({
//			type: 'POST',
//			url: 'http://localhost:8080/dummy_post',
//			data: {
//				lats: lats,
//				lons: lons
//			},
//			datatype: 'JSON',
//			success: function(){
			var stations = get_data();
			var data = []
			for (var i = 0; i < stations.length; i++)
			{
				if(parseFloat(stations[i].lat) >= parseFloat(lats[0]) && parseFloat(stations[i].lat) <= parseFloat(lats[1])
				&& parseFloat(stations[i].lon) <= parseFloat(lons[0]) && parseFloat(stations[i].lon) >= parseFloat(lons[1]))
				{
					data.push(stations[i]);
				}
			}
//				
			return data;
//			}
//		})
}
