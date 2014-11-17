function series_update(){
	var Xaxis = modules['series']['variables']['Xaxis'],
		Yaxis = modules['series']['variables']['fields'],
		graph = modules['series']['graph'];
	
    series = _get_series(Yaxis);
    for (i=0; i<graph.series.length; i++){
    	graph.series[i].data = series[i].data;
    }
    
    
	graph.update();
}

function _get_series(Yaxis){
	var palette = new Rickshaw.Color.Palette( { scheme: 'munin' } ),
		series = [],
		currData = [],
		data = [];

	for (j=0; j < Yaxis.length; j++) {
		currData.push([]);
		data[j] = modules['series']['crossfilter']['group'][j].all();
	}


	for (j=0; j < Yaxis.length; j++) {
		for (i=0; i < data[j].length; i++) {
	        if (data[j][i].value.avg > 0) {
	        	currData[j].push({x: (data[j][i].key).getTime()/1000, y: data[j][i].value.avg });
	    	}
	   }
	}

	for (j=0; j < Yaxis.length; j++) {
	    series.push({
			color: palette.color(),
			data: currData[j],
			name: Yaxis[j]
		})
	}
	
	return series;
}
function series_draw() {	    


	var Xaxis = modules['series']['variables']['Xaxis'],
		Yaxis = modules['series']['variables']['fields'];

	var	mdimension = flight.dimension(function(d){ return d[Xaxis];}),
		msgroup = [];
	for (j=0; j< Yaxis.length; j++){
		msgroup[j] = mdimension.group().reduce(
		        function (p, d) {
		            ++p.x;
		            p.total += +d[Yaxis[j]];
		            p.avg = Math.round(p.total / p.x);
		            return p;
		        },
		        function (p, d) {
		            --p.x;
		            p.total -= +d[Yaxis[j]];
		            p.avg = p.x ? Math.round(p.total / p.x) : 0;
		            return p;
		        },
		        function () {
		            return {x: 0, total: 0, avg: 0};
		        }
		    );
	}
	modules['series']['crossfilter']={'dimension': mdimension, 'group': msgroup};


	
	var sidePanelHtml = '<div class="side-container" id="side-container-4"  >\
		<form id="side_panel">\
			<section>\
				<div id="renderer_form" class="toggler">\
					<input type="radio" name="renderer" id="area" value="area" >\
					<label for="area">area</label>\
					<input type="radio" name="renderer" id="bar" value="bar">\
					<label for="bar">bar</label>\
					<input type="radio" name="renderer" id="line" value="line" checked="">\
					<label for="line">line</label>\
					<input type="radio" name="renderer" id="scatter" value="scatterplot">\
					<label for="scatter">scatter</label>\
				</div>\
			</section>\
			<section>\
				<div id="offset_form">\
					<label for="stack">\
						<input type="radio" name="offset" id="stack" value="zero" >\
						<span>stack</span>\
					</label>\
					<label for="stream">\
						<input type="radio" name="offset" id="stream" value="wiggle">\
						<span>stream</span>\
					</label>\
					<label for="pct">\
						<input type="radio" name="offset" id="pct" value="expand">\
						<span>pct</span>\
					</label>\
					<label for="value">\
						<input type="radio" name="offset" id="value" value="value" checked="">\
						<span>value</span>\
					</label>\
				</div>\
				<div id="interpolation_form">\
					<label for="cardinal">\
						<input type="radio" name="interpolation" id="cardinal" value="cardinal" checked="">\
						<span>cardinal</span>\
					</label>\
					<label for="linear">\
						<input type="radio" name="interpolation" id="linear" value="linear">\
						<span>linear</span>\
					</label>\
					<label for="step">\
						<input type="radio" name="interpolation" id="step" value="step-after">\
						<span>step</span>\
					</label>\
				</div>\
			</section>\
			<section>\
				<h6>Smoothing</h6>\
				<div id="smoother" class="ui-slider ui-slider-horizontal ui-widget ui-widget-content ui-corner-all"><a class="ui-slider-handle ui-state-default ui-corner-all" href="#" style="left: 0%;"></a></div>\
			</section>\
			<section><h6>Legend</h6><div id="series-legend"></div></section>\
		</form>\
	</div>';
	
	$("#side-container-4").remove();
	$("#side-container").append(sidePanelHtml);
	$("#svg-box-series-svg").remove();
	$("#svg-box-series").append($('<div id="svg-box-series-svg">'));

	var graph = new Rickshaw.Graph( {
		element: document.getElementById("svg-box-series-svg"),
		width: 960,
		height: 500,
		renderer: 'line',
		stroke: true,
		preserve: true,
		min:'auto',
		series: _get_series(Yaxis)
	});
			
	
		
	var legend = new Rickshaw.Graph.Legend( {
		graph: graph,
		element: document.getElementById('series-legend')
	
	} );
	
	var shelving = new Rickshaw.Graph.Behavior.Series.Toggle( {
		graph: graph,
		legend: legend
	} );
	
	var order = new Rickshaw.Graph.Behavior.Series.Order( {
		graph: graph,
		legend: legend
	} );
	
	var highlighter = new Rickshaw.Graph.Behavior.Series.Highlight( {
		graph: graph,
		legend: legend
	} );
	
	var smoother = new Rickshaw.Graph.Smoother( {
		graph: graph,
		element: $('#smoother')
	} );
	
	var ticksTreatment = 'glow';
		
	if (types[Xaxis] == 3) {
		var xAxis = new Rickshaw.Graph.Axis.Time( {
			graph: graph,
			ticksTreatment: ticksTreatment,
			timeFixture: new Rickshaw.Fixtures.Time.Local()
		});
		var hoverDetail = new Rickshaw.Graph.HoverDetail( {
			graph: graph,
			xFormatter: function(x) {return new Date(x * 1000).toString();}
		});
	}
	else {
        var xAxis = new Rickshaw.Graph.Axis.X( {
			graph: graph,
			ticksTreatment: ticksTreatment,
			tickFormat: Rickshaw.Fixtures.Number.formatKMBT
		});
		var hoverDetail = new Rickshaw.Graph.HoverDetail( {
			graph: graph,
			xFormatter: function(x) {return x;}
		});
	}
	xAxis.render();
	
	var yAxis = new Rickshaw.Graph.Axis.Y( {
		graph: graph,
		tickFormat: Rickshaw.Fixtures.Number.formatKMBT,
		ticksTreatment: ticksTreatment
	});
	yAxis.render();
	
	var controls = new RenderControls( {
		element: document.getElementById('side_panel'),
		graph: graph
	} );
	
	modules['series']['graph'] = graph;	
	modules['series']['xAxis'] = xAxis;
	modules['series']['yAxis'] = yAxis;
    
	
	graph.render();
}

