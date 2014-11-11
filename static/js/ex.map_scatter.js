zoomLevel = 6;
function map_scatter_draw() {
	var latitude = modules['map_scatter']['variables']['latitude'],
		longitude = modules['map_scatter']['variables']['longitude'],
		size = modules['map_scatter']['variables']['size'],
		group = modules['map_scatter']['variables']['group'],
		text = modules['map_scatter']['variables']['text'];
	if (text == 'none'){
		var mdimension = flight.dimension(function(d){
			return [+d[latitude], +d[longitude], Math.abs(+d[size]), d[group]]; 
		});
	}
	else{
		var mdimension = flight.dimension(function(d){
			return [+d[latitude], +d[longitude],  Math.abs(+d[size]), d[group], d[text]]; 
		});
	}
	var	mgroup = mdimension.group(),
		entries = mgroup.all();
	
	modules['map_scatter']['crossfilter']={'dimension': mdimension, 'group': mgroup};
	
		$("#map_scatter").remove();
		$("#svg-box-map_scatter").append($('<div id="map_scatter" style="width:960px; height:500px">'));

	    var clat = d3.median(entries, function(d){ return  d.key[0];}),
	    	clong = d3.median(entries, function(d){ return d.key[1];});
		
  		map_scatter = new google.maps.Map($('#map_scatter')[0], {
    		zoom: zoomLevel,
    		panControl: false,
			overviewMapControl:true,
			streetViewControl:false,
    		zoomControl: true,
    		zoomControlOptions: {
      			style: google.maps.ZoomControlStyle.SMALL,
      			position: google.maps.ControlPosition.RIGHT_TOP
    		},
    		center: new google.maps.LatLng(clat, clong),
    		mapTypeId: google.maps.MapTypeId.ROADMAP,
    		styles: [{'stylers': [{'saturation': -80},{'lightness': -10}]}]
		});
		google.maps.event.addListener(map_scatter, 'zoom_changed', function() {
			var newZoomLevel = map_scatter.getZoom();
			if (Math.abs(newZoomLevel - zoomLevel) > 1) {
				zoomLevel = newZoomLevel;
			}
		});

	map_scatter_update();
}
function map_scatter_update() {
	var r_normalization = 20000,
		colors = d3.scale.category10(),
		entries = modules['map_scatter']['crossfilter']['group'].all(),
		maxk = d3.max(entries, function(d){return d.value>0 ? d.key[2]: -Number.MAX_VALUE;});
	
  	for (i = 0; i< entries.length; i++) {
  		var entry = entries[i],
  			latlong = new google.maps.LatLng(entry.key[0], entry.key[1]);
  		
		if (entry.value>0) {
			var name = (entry.key.length > 4) ? entry.key[4]: '',
				color =  (modules['map_scatter']['variables']['group'] == 'all') ?  '#00b9e7': colors(entry.key[3]);
			addCircle(map_scatter, entry.key[0], entry.key[1], entry.key[2]*r_normalization/(maxk), name, color );
		}
  	}	
  	
  	if (modules['map_scatter']['variables']['group'] != 'all') {
  		
	  	$('#map_scatter').append('<div id="map_scatter-legend" style="background: #eee; padding:5px;"></div>')
	  	for (i = 0; i<colors.rangeExtent().length; i++){
	  		key = colors.domain()[i];
	  		$('#map_scatter-legend').append(
	  			'<div>'
	  			+ '<div style="float:left;margin-right:5px;width:12px;height:12px;border-radius:50%;display:block;background:'+colors(key)+';"></div>'
	  			+ '<div style="float:left;">'+ key + '</div>'
	  			+ '</div>');
	  	}
	  	map_scatter.controls[google.maps.ControlPosition.LEFT_TOP].push(document.getElementById('map_scatter-legend'));
  	}
}

function addCircle(map_scatter, lat, lon, r, name, color){
	// Add circle overlay and bind to marker
	var circle = new google.maps.Circle({
		map: map_scatter,
		center: new google.maps.LatLng(lat, lon),
	 	strokeColor: color,
    	strokeOpacity: 0.8,
    	strokeWeight: 2,
    	fillColor: color,
    	fillOpacity: 0.35,
    	radius: r
	});
 	// Create marker  		
	if (name && name.length>0){
		var marker = new google.maps.Marker({
			map: map_scatter,
			position: new google.maps.LatLng(lat, lon),
			title: name
		});
		circle.bindTo('center', marker, 'position');
	}
}
	