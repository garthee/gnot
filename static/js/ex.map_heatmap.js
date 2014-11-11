zoomLevel = 6;
function map_heatmap_draw() {
	var latitude = modules['map_heatmap']['variables']['latitude'],
		longitude = modules['map_heatmap']['variables']['longitude'],
		nfixed = Math.max(Math.min(4, Math.floor((zoomLevel-13)/2+3)),1),
		mdimension = flight.dimension(function(d){
			return [+(+d[latitude]).toFixed(nfixed), +(+d[longitude]).toFixed(nfixed)]; 
		}),
		mgroup = mdimension.group(),
		entries = mgroup.all();
	
	modules['map_heatmap']['crossfilter']={'dimension': mdimension, 'group': mgroup};
	
		$("#map_heatmap").remove();
		$("#svg-box-map_heatmap").append($('<div id="map_heatmap" style="width:960px; height:500px">'));

	    var clat = d3.median(entries, function(d){ 
	    	return  d.key[0];
	    });
	    var clong = d3.median(entries, function(d){ return d.key[1];});
		
  		map_heatmap = new google.maps.Map($('#map_heatmap')[0], {
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
  		google.maps.event.addListener(map_heatmap, 'zoom_changed', function() {
			var newZoomLevel = map_heatmap.getZoom();
			if (Math.abs(newZoomLevel - zoomLevel) > 1) {
				zoomLevel = newZoomLevel;
				map_heatmap_draw();
			}
		});
  		heatmap = new google.maps.visualization.HeatmapLayer({
    		radius: 15,
    		opacity: 1,
    		map: map_heatmap
  		});
	
	
	map_heatmap_update();
}
function map_heatmap_update() {
	var latitude = modules['map_heatmap']['variables']['latitude'],
		longitude = modules['map_heatmap']['variables']['longitude'],
		count = modules['map_heatmap']['variables']['count'],
		entries = modules['map_heatmap']['crossfilter']['group'].all();
	
	var taxiData = new google.maps.MVCArray();
  	heatmap.setData(taxiData);
  	
  	for (i = 0; i< entries.length; i++) {
  		var entry = entries[i];
		var latlong = new google.maps.LatLng(entry.key[0], entry.key[1]);
		if (entry.value>0) {
			try{
				taxiData.push({location: latlong, weight: entry.value });
			}
			catch (err){
				break;
			}
		}
  	}	
}
