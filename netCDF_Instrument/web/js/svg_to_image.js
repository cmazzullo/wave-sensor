var made_image = false;
$('.image').click(function(){
	
	console.log('time to party!');
	var svgElements= $(this).parent().parent().find('svg');
	
	var canvas, xml;
	//replace all svgs with a temp canvas
	svgElements.each(function () {
	    
	    canvas = document.createElement("canvas");
	    canvas.id = "screenShotTempCanvas";
	    //convert SVG into a XML string
	    xml = (new XMLSerializer()).serializeToString(this);

	    // Removing the name space as IE throws an error
	    xml = xml.replace(/xmlns=\"http:\/\/www\.w3\.org\/2000\/svg\"/, '');

	    //draw the SVG onto a canvas
	    canvg(canvas, xml);
	    $(canvas).insertAfter(this);
	    $(canvas).hide()
	    //hide the SVG element
	    
	    setTimeout(function() {
		    convertCanvasToImage(canvas, function(image)
		    		{
		    			if (made_image == false)
		    			{
		    				made_image = true;
		    				image.src = image.src.replace('data:image/png', 'data:application/octet-stream');
		    				$('body').append('<a style="color:black;display:none" href="' + image.src 
		    						+'" download="sample.png" id="image_link">Test</a>');
		    				var a = document.getElementById("image_link");
		    				a.click();		    				
		    			}
		    		}) }, 1000);
	    
	    
			setTimeout(function(){
				made_image = false;
				$('#image_link').remove();
				$('#screenShotTempCanvas').remove();
				canvas = null;
				xml = null;
			}, 1000);
	    
	});
});


	
var convertCanvasToImage = function(canvas, callback) {
		  var image = new Image();
		  image.onload = function(){
		    callback(image);
		  }
		  image.src = canvas.toDataURL("image/png");
		}

	
	  
	//After your image is generated revert the temporary changes
