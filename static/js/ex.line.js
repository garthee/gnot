function line_draw() {
	var Xaxis = modules['line']['variables']['Xaxis'],
		fields = modules['line']['variables']['fields'],
		chart = nv.models.lineWithFocusChart(),
		margin = {top: 40, right: 20, bottom: 50, left: 90},
		width = 960,
		height = 400,
		sr = bigdata[0],
		str2str = function(d){return d;},
		str2int = function(d){return +d;},
		month2int = function(d){ d = d.split(/[- :]/); return (new Date(d[0], d[1]-1, 0));},
		date2int = function(d){ d = d.split(/[- :]/); return (new Date(d[0], d[1]-1, d[2]));},
		time2int = function(d){ d = d.split(/[- :]/);  return new Date(d[0], d[1]-1, d[2], d[3], d[4], d[5]);},
		isNumber = function (n) { return !isNaN(parseFloat(n)) && isFinite(n);},
		parseX = str2int, 
		type = 1;
		
	if (!isNumber(sr[Xaxis])){
		var lx = sr[Xaxis].split(/[- :]/).length;
		if (lx >=6){
			parseX = time2int;
			type = 3;
		}
		else if (lx >= 3) {
			parseX = date2int;
			type = 3;
		}
		else if (lx >= 2) {
			parseX = month2int;
			type = 3;
		}
	}
		
	var	mdimension = flight.dimension(function(d){ 
			var f =  [parseX(d[Xaxis])];
			for (i = 0; i<fields.length; i++){
				f.push(+d[fields[i]]);
			}
			return f;
		}),
		mgroup = mdimension.group();
	modules['line']['crossfilter']={'dimension': mdimension, 'group': mgroup};
	
	if (type == 1) {
		chart.xAxis.tickFormat(d3.format(',f'));
	}
	else{
		chart.xAxis.tickFormat(function(d) { 
			return d3.time.format("%Y-%m-%d")(new Date(d)); 
		});	
	}
	chart.yAxis.tickFormat(d3.format(',.2f'));
	chart.y2Axis.tickFormat(d3.format(',.2f'));
	chart.margin(margin).height(height).width(width);
	modules['line']['chart'] = chart;
	modules['line']['fields'] = fields;


	$("#svg-box-line").find("svg").remove();
	d3.select("#svg-box-line").append("svg:svg").attr("height", height).attr("width", width);

	line_update();
}

function line_update() {
	nv.addGraph(function() {
		var chart = modules['line']['chart'],
			line_data = {},
			data = modules['line']['crossfilter']['group'].all();
		
		fields = modules['line']['fields'];
		for (i=0; i<fields.length; i++){
			line_data[fields[i]] = {key:fields[i], values:[]};
		}
		data.forEach(function(d,i){
			if (d.value > 0) {
				for (i=0; i<fields.length; i++){
					line_data[fields[i]].values.push({x:d.key[0], y:d.key[i+1]});
				}
			}
		});
		
		d3.select('#svg-box-line svg')
	      .datum(d3.keys(line_data).sort().map(function (d){return line_data[d];}))
	      .transition().duration(500)
	      .call(chart);
	
		  nv.utils.windowResize(chart.update);
		
		  return chart;
	});	
}
