function scatter_draw() {
	
	var Xaxis = modules['scatter']['variables']['Xaxis'],
		Yaxis = modules['scatter']['variables']['Yaxis'],
		Group = modules['scatter']['variables']['Group'],
		mdimension = flight.dimension(function(d){ return [+d[Xaxis], +d[Yaxis], d[Group]];}),
		mgroup = mdimension.group(),
		shapes = ['circle', 'square','diamond', 'cross', 'triangle-down', 'triangle-up'],
		margin = {top: 40, right: 20, bottom: 50, left: 90},
		width = 960,
		height = 400,
		scatterchart = nv.models.scatterChart();

	scatterchart.showDistX(true).showDistY(true)
		.width(width)
		.height(height)
		.margin(margin)
		.color(d3.scale.category10().range());

	scatterchart.tooltipContent(function(key, xVal, yVal, e, chart) {
		return '<h3>' + key + '</h3>';
	});
	scatterchart.dispatch.on('stateChange', function(e) { ('New State:', JSON.stringify(e)); });

	$("#svg-box-scatter").find("svg").remove();
	d3.select("#svg-box-scatter").append("svg:svg").attr("height", height).attr("width", width);

	if (types[Xaxis] == 3)
        scatterchart.xAxis.tickFormat(function(d) { return d3.time.format('%d-%m-%y')(new Date(d))});
	else
        scatterchart.xAxis.tickFormat(d3.format('.2f')).axisLabel(Xaxis);

	if (types[Yaxis] == 3)
        scatterchart.yAxis.tickFormat(function(d) { return d3.time.format('%d-%m-%y')(new Date(d))});
	else
        scatterchart.yAxis.tickFormat(d3.format('.2f')).axisLabel(Yaxis);





	modules['scatter']['crossfilter']={'dimension': mdimension, 'group': mgroup};
	modules['scatter']['chart'] = scatterchart;
	
	nv.utils.windowResize(scatterchart.update);
	
	scatter_update();
}

function scatter_update() {

	var scatterchart = modules['scatter']['chart'],
		scatter_data = {},
		data = modules['scatter']['crossfilter']['group'].all();
	
	data.forEach(function(d,i){
		if (d.value > 0) {
			if (!(d.key[2] in scatter_data)) {
				scatter_data[d.key[2]] = {key:d.key[2], values:[]};
			}
			scatter_data[d.key[2]].values.push({x:d.key[0], y:d.key[1], size:d.value});
		}
	});
	
	d3.select('#svg-box-scatter svg')
		.datum(d3.keys(scatter_data).sort().map(function (d){return scatter_data[d];}))
		.transition().duration(500)
		.call(scatterchart);
	
}
