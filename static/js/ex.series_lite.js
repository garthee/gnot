function series_lite_draw(data, config) {
	$("#svg-box-series_lite").find("svg").remove();
	
	date = config['variables']['date'];
	date = config['variables']['date'];
	var margin = {top : 20, right : 40, bottom : 30, left : 60},
		width = 960;
		height = 600;
	
	d3.select('#svg-box-series_lite').append("svg:svg").attr("height", height).attr("width", width);
	
	function isNumber(n) {
		return !isNaN(parseFloat(n)) && isFinite(n);
	}	
	var str2int = function(d){return +d;};
	var month2int = function(d){ d = d.split(/[- :]/); return (new Date(d[0], d[1]-1, 0));};
	var date2int = function(d){ d = d.split(/[- :]/); return (new Date(d[0], d[1]-1, d[2]));};
	var time2int = function(d){ d = d.split(/[- :]/);  return new Date(d[0], d[1]-1, d[2], d[3], d[4], d[5]);};

	nv.addGraph(function() {
	
	  	var chart = nv.models.lineWithFocusChart()
	  		.width(width)
			.height(height)
			.margin(margin)
	 		.color(d3.scale.category10().range());
	
  		
		// identify x axis
		var parseX = str2int, XisInt = 1
		if (!isNumber(data[0][date])){
			var lx = data[0][date].split(/[- :]/).length;
			if (lx >= 6)
				parseX = time2int;
			else if (lx >= 3)
				parseX = date2int;
			else if (lx >= 2)
				parseX = month2int;
			XisInt = 0;
		} 	
		
		var fdata = [], js = [], ds = 0;
  		for (i = 0; i < keys.length; i++){
  			if (keys[i] != date){
  				fdata[keys[i]] = {key:keys[i], values:[]};
  				js.push(i);
  			}
  			else {
  				ds = i;
  			}
  		}
		for (i=0; i < data.length; i++) {
	        var row = data[i];
			var d = parseX(row[keys[ds]]);
	        for (j=0; j < js.length; j++) {
	            if (row[keys[js[j]]] != '') {
	            	fdata[keys[js[j]]]["values"].push({ x: d, y: +row[keys[js[j]]] });
	        	}
	       }
	    }
		
		if (XisInt) {
			chart.xAxis.tickFormat(d3.format(',f'));
			chart.x2Axis.tickFormat(d3.format(',f'));
		}
		else {
			chart.xAxis.tickFormat(function(d) { 
				return d3.time.format("%Y-%m-%d")(new Date(d)); 
			});
			chart.x2Axis.tickFormat(function(d) { 
				return d3.time.format("%Y-%m-%d")(new Date(d)); 
			});
		}
		var fdata = Object.keys(fdata).map(function(key){return fdata[key]; });
 		
	 	d3.select('#svg-box-series_lite svg')
	      .datum(fdata)
	      .transition().duration(500)
	      .call(chart);
	
	 	nv.utils.windowResize(chart.update);
	 	return chart;
	});
}