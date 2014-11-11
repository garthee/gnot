function line2_draw() {
	var Xaxis = modules['line2']['variables']['Xaxis'],
		//volume = modules['line']['variables']['volume'],
		fields = modules['line2']['variables']['fields'],
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
	
	var num_bins = 100,
		maxX = d3.max(bigdata, function(d){return parseX(d[Xaxis]);}),
		minX = d3.min(bigdata, function(d){return parseX(d[Xaxis]);}),
		dxx = ((maxX-minX)/num_bins),
		groupint = function(d){return Math.floor(d / dxx) * dxx;},
		xunit = function(start,stop,step){return (stop-start)/dxx};
 
	

	
	$("#svg-box-line2").append($('<div id="svg-box-line2-line">'));
	$("#svg-box-line2").append($('<div id="svg-box-line2-volume">'));
	
	var moveChart = dc.compositeChart("#svg-box-line2-line"),
		volumeChart = dc.barChart("#svg-box-line2-volume"),
		mdimension = flight.dimension(function(d){ 
			return f =  parseX(d[Xaxis]);
		});
		if (type == 1) {
			var x = d3.scale.linear().domain([minX, maxX]);
		}else if (type == 3) {
			var x = d3.time.scale().domain([minX, maxX]); 
		}
	
		
		moveChart
        .width(960)
        .height(300)
        .transitionDuration(1000)
        .margins({top: 30, right: 50, bottom: 25, left: 40})
        .x(x)
        .xAxisLabel(Xaxis)
        .xUnits(xunit)
        .elasticY(true)
        
		var composits = [];
		var color =  d3.scale.category20();
		for (i = 0; i<fields.length; i++){
			var msgroup =  mdimension.group(function(d) { return groupint(d); }).reduce(
			        function (p, d) {
			            ++p.x;
			            p.total += +d[fields[i]];
			            p.avg = Math.round(p.total / p.x);
			            return p;
			        },
			        function (p, d) {
			            --p.x;
			            p.total -= +d[fields[i]];
			            p.avg = p.x ? Math.round(p.total / p.x) : 0;
			            return p;
			        },
			        function () {
			            return {x: 0, total: 0, avg: 0};
			        }
			    );
			var ch = dc.lineChart(moveChart)
	        	.dimension(mdimension)
	        	.group(msgroup, fields[i]);
			composits.push(ch);
		}			
	moveChart
        .compose(composits)
        .mouseZoomable(true)
        .brushOn(false)
    //    .rangeChart(volumeChart)
        .renderHorizontalGridLines(true)
        .legend(dc.legend().x(800).y(10).itemHeight(13).gap(5));
	

	
        

//		.title(function (d) {
//            var value = d.value.avg ? d.value.avg : d.value;
//            if (isNaN(value)) value = 0;
//            return d.key + "\n" + value;
//        });

		        
//	  volumeChart.width(960)
//	        .height(80)
//	        .margins({top: 0, right: 50, bottom: 20, left: 40})
//	        .dimension(mdimension)
//	        .group(mdimension.group(function(d) { return groupint(d); }))
//	        .centerBar(true)
//	        .gap(1)
//	        .x(x)
//	        .xUnits(xunit);
		
	moveChart.render();
	//volumeChart.render();
		
}		
		
	

function line2_update() {
	
}
