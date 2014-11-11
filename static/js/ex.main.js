function dashboard_draw(data, config) {
				
		var chartNames = ['barChart', 'rowChart', 'pieChart'];
		
		config['DchartTypes'] = [];
		for (j=0; j<keys.length; j++){
			var strhtml = '<span class="select-charts">Pick a different <span class="dropdown">'
				+ '<a id="dropdown-chart-' + j + '" role="button" data-toggle="dropdown" href="#"> chart <span class="caret"></span></a>'
				+ '<ul class="dropdown-menu" role="menu" aria-labelledby="dropdown-chart-' + j + '" id="ex-dashboard-chart-' + j + '"></ul>'
				+ '</span></span>';
		
			$("#svg-box-dashboard")
				.append($('<div id="'+keys[j]+'-dchart">')
					.append($('<div class="title">')
						.append(keys[j])
						.append(' | Current filter: <span class="filter"></span>'
							+' | <a class="reset" href="javascript:reset(' + j + ');dc.redrawAll();">reset</a>'
							+ strhtml)));
			for (i = 0; i < chartNames.length; i++) {
				$('#ex-dashboard-chart-' + j).append($('<li>').append($('<a href="#">').append(chartNames[i])));
			}
			config['DchartTypes'][j] = "barChart";
		}
		
		
		$(".select-charts .dropdown .dropdown-menu li a").click(function(){
			iid = $(this).parent().parent().attr('id');
			iid = iid.split('-'); iid = iid[3];
			config['DchartTypes'][iid] = $(this).text();
			var oldbar = charts[iid],
				chart = dc[$(this).text()]("#"+keys[iid]+"-dchart"),
				bar = draw_charts(chart, $(this).text(), oldbar.dimension(), oldbar.group(), oldbar.x(), oldbar.xUnits());
				
			dc.renderAll();
		});
		
		$('#dashboard-side-container-m').html('<p id="totals"><span class="filter-count"></span> selected out of <span class="total-count"></span> records.</p>');
		
		var num_bins = 100;
		
		var charts = [],
			flight = crossfilter(data),
	  		all = flight.groupAll(),
	  		flightId = flight.dimension(function(d){return +d[0]-1;}),
			flightIds = flightId.group();
	
		// crossfilter
		var formatNumber = d3.format(".2f%");
		
		dc.dataCount("#totals").dimension(flight).group(all);
		
	  	var str2str = function(d){return d;},
	  		str2int = function(d){return +d;},
	  		month2int = function(d){ d = d.split(/[- :]/); return (new Date(d[0], d[1]-1, 0));},
	  		date2int = function(d){ d = d.split(/[- :]/); return (new Date(d[0], d[1]-1, d[2]));},
	  		time2int = function(d){ d = d.split(/[- :]/);  return new Date(d[0], d[1]-1, d[2], d[3], d[4], d[5]);};
			isNumber = function (n) { return !isNaN(parseFloat(n)) && isFinite(n);};
	
			var createChart = function(j, keys) {
				var k = keys[j], parseX = str2int, type = 1; // type1:int,type2:str,type3:date
				if (!isNumber(sr[keys[j]])){
					var lx = sr[keys[j]].split(/[- :]/).length;
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
					else {
						parseX = str2str;
						type = 2;
						config['DchartTypes'][j] = 'pieChart';
					}
				}
				
				var maxX = parseX(sr[k]), minX = parseX(sr[k]);
				for (i = 1; i < data.length; i++){
					maxX  = Math.max(maxX, parseX(data[i][k]));
					minX  = Math.min(minX, parseX(data[i][k]));
				}
				var dxx = ((maxX-minX)/num_bins),
					groupint = function(d){return Math.floor(d / dxx) * dxx;},
					xunit = function(start,stop,step){return (stop-start)/dxx},
				 	chartID = "#"+keys[j]+"-dchart",
					row = flight.dimension(function(d) { return parseX(d[k]); });
				if (type == 1) {
					group = row.group(function(d) { return groupint(d); });
					x = d3.scale.linear().domain([minX, maxX]);
				}else if (type == 3) {
					group = row.group(function(d) { return groupint(d); });
					x = d3.time.scale().domain([minX, maxX]); 
				}else if (type == 2){
					group = row.group();
					xunit = dc.units.ordinal;
					x = d3.scale.ordinal();
				}
				
				if (group.size() < 5) {
					config['DchartTypes'][j] = 'rowChart';
				}
				else if (group.size() < 15) {
					config['DchartTypes'][j] = 'pieChart';
				}
				var bar = dc[config['DchartTypes'][j]](chartID);
			 	return draw_charts(bar, config['DchartTypes'][j], row, group, x, xunit); 
				
			}
		var sr = data[0];
	  	for (j = 0; j < keys.length; j++){
	  		var cbar = createChart(j, keys);
			charts.push(cbar);
	  	}
	  	
	dc.renderAll();
	
	window.reset = function(i) {
	    charts[i].filter(null);
	};
	
	
	function draw_charts(chart, type, dimension, group, x, xunit) {
		switch(type){
//			case:
//				.width(990) // (optional) define chart width, :default = 200
//		        .height(250)  // (optional) define chart height, :default = 200
//		        .transitionDuration(1500) // (optional) define chart transition duration, :default = 750
//		        .margins({top: 10, right: 50, bottom: 30, left: 40})
//		        .dimension(yearlyDimension)
			case 'rowChart':
				chart.height(150).width(478)
		        .margins({top: 20, left: 10, right: 10, bottom: 20})
		        .label(function (d) {return d.key;})
		        .title(function (d) {return d.value;})
		        .elasticX(true).xAxis().ticks(4);
				break;
			case 'pieChart':
				chart.slicesCap(8).innerRadius(30).radius(70).transitionDuration(500)
				.height(150).width(478).legend(dc.legend())
				.title(function (d) {return d.value;});
				break;
			default:
				chart.height(150).width(960)
		        .margins({top: 10, right: 10, bottom: 30, left: 50})
		        .centerBar(true)
		        .gap(0.5)
		        .elasticY(true);
				break;
		}
		
		return chart.dimension(dimension).group(group).xUnits(xunit).x(x);
	}
}