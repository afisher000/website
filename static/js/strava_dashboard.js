function strava_dashboard(splits, activity, lineObj, scatterObj, mapObj, histObj) {

    // Conversions
    var mps_to_mpm = 0.0372823;
    var mps_to_mph = 2.2369362921;
    var split_to_miles = 0.0621371;
    var m_to_ft = 3.28084;
    var avg_timestep = activity['elapsed_time']/splits.length/60;

    // # Read out data from splits structure
    var distanceData = splits.map(item => item.split*split_to_miles);
    var hrData = splits.map(split => split.hr);
    var paceData = splits.map(item => 1/(item.speed*mps_to_mpm));
    var gradeData = splits.map(item => item.grade*100);
    var speedData =  splits.map(item => item.speed*mps_to_mph);
    var latData = splits.map(item => parseFloat(item.lat));
    var lngData = splits.map(item => parseFloat(item.lng));
    var elevationData = splits.map(item => item.altitude*m_to_ft)


    // # Get elements by ID
    var lineDiv = document.getElementById(lineObj.ID);
    var lineSelector = document.getElementById(lineObj.selector);

    var scatterDiv = document.getElementById(scatterObj.ID);
    var xSelector = document.getElementById(scatterObj.xSelector);
    var ySelector = document.getElementById(scatterObj.ySelector);
    var Checkbox = document.getElementById(scatterObj.checkbox);
    
    var mapDiv = document.getElementById(mapObj.ID);
    var histDiv = document.getElementById(histObj.ID);

    console.log('stop1');
    // # Call individual plot functions
    marker = plotMap(mapObj.ID, latData, lngData, elevationData);
    plotHistogram(histObj.ID, splits, activity);
    lineCallbackFunction(); 
    scatterCallbackFunction();


    // # Create event listeners
    lineSelector.addEventListener('change', lineCallbackFunction);
    xSelector.addEventListener('change', scatterCallbackFunction);
    ySelector.addEventListener('change', scatterCallbackFunction);
    Checkbox.addEventListener('change', scatterCallbackFunction);

    
    function hoverCallbackFunction(eventData) {
        var points = eventData.points;
        if (points.length>0){
            var closestIndex = points[0].pointIndex;
            updateScatterColor(lineDiv, closestIndex);
            marker.setLngLat([lngData[closestIndex], latData[closestIndex]]);
        }
    }

    function scatterCallbackFunction() {
        var xSelectedValue = xSelector.value;
        var ySelectedValue = ySelector.value;
        var CheckboxValue = Checkbox.checked;

        if (xSelectedValue === 'grade') {
            xData = gradeData;
            xLabel = 'Grade';
            xUnits = '%';
        } else if (xSelectedValue === 'distance') {
            xData = distanceData;
            xLabel = 'Distance';
            xUnits = 'mi';
        }

        if (ySelectedValue === 'speed') {
            yData = speedData;
            yLabel = 'Speed';
            yUnits = 'mph';
        } else if (ySelectedValue === 'heartrate') {
            yData = hrData;
            yLabel = 'Heart Rate';
            yUnits = 'bpm';
        } else if (ySelectedValue === 'pace') {
            yData = paceData;
            yLabel = 'Pace';
            yUnits = 'min/mi';
        }
        myScatterPlot(scatterObj.ID, xData, yData, xLabel, yLabel, xUnits, yUnits, CheckboxValue)
        scatterDiv.on('plotly_click', hoverCallbackFunction);
    }

    function lineCallbackFunction() {
        var selectedValue = lineSelector.value;

        xData = distanceData;
        if (selectedValue === 'speed') {
            yData = speedData;
            ytitle = 'Speed (mph)'
        } else if (selectedValue === 'heartrate') {
            yData = hrData;
            ytitle = 'HR (bpm)';
        } else if (selectedValue === 'speedGradeAdj') {
            yData = speedGradeAdjData;
            ytitle = 'Adj Speed (mph)';
        } else if (selectedValue === 'pace') {
            yData = paceData;
            ytitle = 'Pace (min/mi)';
        } else if (selectedValue === 'elevation') {
            yData = elevationData;
            ytitle = 'Elevation (ft)';
        } else if (selectedValue === 'grade') {
            yData = gradeData;
            ytitle = 'Grade (%)';
        }
        myLinePlot(lineObj.ID, xData, yData, ytitle);
        lineDiv.on('plotly_click', hoverCallbackFunction);

        // Update linecolor gradient on map
        marker = plotMap(mapObj.ID, latData, lngData, yData);
    }
}



function updateScatterColor(PlotlyDiv, nearestIdx) {
    var scatterTraceIndex = 0; // Assuming it's the first trace
    var scatterTrace = PlotlyDiv.data[0]; // Assuming it's the first trace
    var scatterColors = scatterTrace.marker.color;

    for (var i = 0; i < scatterColors.length; i++) {
        scatterColors[i] = (i === nearestIdx) ? 'red' : 'blue';
    }

    var updates = {
        'marker.color': [scatterColors],
        'marker.size': [scatterColors.map((color, i) => (i === nearestIdx) ? 10 : 6)], // Change size
        'marker.z': [scatterColors.map((color, i) => (i === nearestIdx) ? 5 : 1)] // Change z value
    };
    Plotly.restyle(PlotlyDiv, updates, [scatterTraceIndex]);
}

function myMatchedPlot(chartID, activity, dates, speeds) {
    var mps_to_mpm = 0.0372823;

    var paces = speeds.map(speed => 1/(speed*mps_to_mpm));
    var data = [
        {
            x:dates,
            y:paces,
            type:'scatter',
            mode:'markers',
            showlegend:false,
        },
        {
            x:[activity['start_date']],
            y:[1/(activity['average_speed']*mps_to_mpm)],
            type:'scatter', 
            mode:'markers',
            marker: {color: '#ff0000'},
            showlegend:false,
        }
    ];

    var tickvals = createArrayWithSteps(3, 12, .25);
    var ticktext = customPaceLabels(tickvals);
    var layout = {
        plot_bgcolor: 'transparent',
        paper_bgcolor: 'transparent',
        title: 'Matched Activities over Time',
        yaxis: { 
            title: 'Pace (mi/min)',
            tickmode: "array",
            tickvals: tickvals,
            ticktext: ticktext,
        },
        xaxis: { title: 'Date'},
        hovermode: 'closest',
        margin: {
            l: 50, // Left margin
            r: 0, // Right margin
            t: 50, // Top margin
            b: 50  // Bottom margin
        },
    };
        
    var config = {
        displayModeBar: false,
    }
    Plotly.newPlot(chartID, data, layout, config);
}

function plotMap(chartID, latData, lngData, colorData) {

    maxLat = calcMax(latData);
    minLat = calcMin(latData);
    maxLng = calcMax(lngData);
    minLng = calcMin(lngData);

    // # Create map
    const map = new mapboxgl.Map({
        container: chartID,
        style: 'mapbox://styles/mapbox/streets-v11',
        center: [maxLng/2+minLng/2, maxLat/2+minLat/2],
        zoom:13,
    });

    // # Add activity path on map
    var coordinates = latData.map((lat, index) => [lngData[index], lat]);
    map.on('load', function() {
        // Create an array of GeoJSON features, each with its own color property
        var lineFeatures = [];
        for (var i = 1; i < coordinates.length; i++) {
            var feature = {
                type: 'Feature',
                properties: {
                    color: colorData[i-1]/2+colorData[i]/2, // Assign the color based on colorData
                },
                geometry: {
                    type: 'LineString',
                    coordinates: [coordinates[i-1], coordinates[i]],
                },
            };
            lineFeatures.push(feature);
        }

        map.addLayer({
            id: 'line-plot',
            type: 'line',
            source: {
                type: 'geojson',
                data: {
                    type: 'FeatureCollection',
                    features: lineFeatures,
                    // type: 'Feature',
                    // properties: {colorvar: colorData},
                    // geometry: {
                    //     type: 'LineString',
                    //     coordinates: coordinates,
                    // },
                }
            },
            layout: {
                'line-join': 'round',
                'line-cap': 'round'
            },
            paint: {
                'line-color': [
                    'interpolate', ['linear'],
                    ['get', 'color'],
                    calcMin(colorData), 'blue', 
                    calcMax(colorData), 'red'
                ],
                'line-width': 5,
            },


            // paint: {
            //     'line-color': '#f44',
            //     'line-width': 5
            // }
        });
    });

    console.log(minLat);
    console.log(maxLat);
    bounds = [
        [minLng, minLat],
        [maxLng, maxLat],
    ];
    map.fitBounds(bounds, {padding:40});

    // # Create marker
    var marker = new mapboxgl.Marker({color:'#c00'})
    .setLngLat([lngData[lngData.length-1], latData[latData.length-1]]).addTo(map);


    var startMarker = new mapboxgl.Marker({color:'#0a0'})
        .setLngLat([lngData[lngData.length-1], latData[latData.length-1]]).addTo(map);


    return marker
}


function myLatLngPlot(chartID, xData, yData) {
    var initialScatterColors = new Array(xData.length).fill('blue'); // Initial colors
    var initialScatterSize = new Array(xData.length).fill(6); // Initial colors
    var initialScatterZ = new Array(xData.length).fill(1); // Initial colors
    var data = [{
        x: xData,
        y: yData,
        type: 'scatter',
        mode: 'markers',
        marker: {color: initialScatterColors, size:initialScatterSize, z:initialScatterZ},
        hoverinfo: 'none',
    }];

    var layout = {
        title:'overall title2',
        yaxis: { title: 'Longitude'},
        xaxis: { title: 'Latitude'},
        hovermode: 'closest',
    };
        
    var config = {
        displayModeBar: false,
    }
    Plotly.newPlot(chartID, data, layout, config);
}

function myLinePlot(chartID, xData, yData, ytitle) {

    var initialScatterColors = new Array(xData.length).fill('blue'); // Initial colors
    var initialScatterSize = new Array(xData.length).fill(6); // Initial colors
    var initialScatterZ = new Array(xData.length).fill(1); // Initial colors
    var data = [
        {
            x: xData,
            y: yData,
            type: 'scatter',
            mode: 'lines+markers',
            marker: {color: initialScatterColors, size:initialScatterSize, z:initialScatterZ},
            //hoverinfo: 'none',
        },
    ];

    // Define layout input
    var layout = {
        plot_bgcolor: 'transparent',
        paper_bgcolor: 'transparent',
        yaxis: { title: ytitle},
        xaxis: { title: 'Distance (mi)'},
        hovermode: 'closest',
        margin: {
            l: 50, // Left margin
            r: 0, // Right margin
            t: 0, // Top margin
            b: 50  // Bottom margin
        },
    };

        
    var config = {
        displayModeBar: false,
    }
    Plotly.newPlot(chartID, data, layout, config);

}

function myScatterPlot(chartID, xData, yData, xLabel, yLabel, xUnits, yUnits, CheckboxValue) {


    
    // Creating the histogram2dcontour trace
    var initialScatterColors = new Array(xData.length).fill('blue'); // Initial colors
    var initialScatterSize = new Array(xData.length).fill(6); // Initial colors
    var initialScatterZ = new Array(xData.length).fill(1); // Initial colors
    var data = [
        {
            x: xData,
            y: yData,
            type: 'scatter',
            mode: 'markers',
            marker: {color: initialScatterColors, size:initialScatterSize, z:initialScatterZ},
            showlegend: false,
            hoverinfo: 'none',
        }
    ];

    var layout = {
        plot_bgcolor: 'transparent',
        paper_bgcolor: 'transparent',
        xaxis: { title: `${xLabel} (${xUnits})`, range:[xMinValue, xMaxValue] },
        yaxis: { title: `${yLabel} (${yUnits})`, range:[yMinValue, yMaxValue]},
        margin: {
            l: 50, // Left margin
            r: 0, // Right margin
            t: 50, // Top margin
            b: 50  // Bottom margin
        },
        hovermode: 'closest',
    };

    if (CheckboxValue) {
        // Compute percentiles for scaling the axes (avoid outliers ruining limits)
        var xQ1 = calcQuartile(xData, 3);
        var xQ3 = calcQuartile(xData, 97);
        var yQ1 = calcQuartile(yData, 3);
        var yQ3 = calcQuartile(yData, 97);
        var xpad = 0.1*(xQ3-xQ1);
        var ypad = 0.1*(yQ3-yQ1);
        var xMinValue = xQ1-xpad;
        var xMaxValue = xQ3+xpad;
        var yMinValue = yQ1-ypad;
        var yMaxValue = yQ1-ypad;
        
        // Compute linear fit
        var [linearFit, slope] = linearRegression(xData, yData);

        // Add to data
        data.push(
            {
                x: xData,
                y: linearFit,
                mode: 'lines',
                type: 'scatter',
                showlegend: false,
                hoverinfo: 'none',
            }
        );

        // Add title
        layout.title = slope.toFixed(2) + ' ' + `${yUnits} / ${xUnits}`;
    }


    

    
    var config = {
        displayModeBar: false,
    }
    
    // Create the 2D density plot
    Plotly.newPlot(chartID, data, layout, config);
    }



    function plotHistogram(chartID, splits, activity) {
        // What is time per split on average?
        var dt = activity['elapsed_time']/splits.length/60;
    
        // Extracting data for x and y axes from the splits array
        var hrData = splits.map(split => split.hr);
        
        // Bin heart rate data
        const binRanges = [0,150,160,170,180,190,500]; // Define your bin ranges
        const binCounts = new Array(binRanges.length).fill(0);
    
        // Count heart rates in each bin
        hrData.forEach(rate => {
        for (let i = 0; i < binRanges.length - 1; i++) {
            if (rate >= binRanges[i] && rate < binRanges[i + 1]) {
            binCounts[i]++;
            break;
            }
        }
        });
    
        // Creating the histogram2dcontour trace
        var data = [
            {
                x: ['<149','150-159','160-169','170-179','180-189','>190'],
                y: binCounts.map(binCount => binCount*dt),
                type: 'bar',
                marker:{
                    color:['#0000ff', '#3200c8', '#640096', '#960064', '#c80032','ff0000'],
                },
                hoverinfo: 'none',
            }
        ];
        
        var layout = {
            plot_bgcolor: 'transparent',
            paper_bgcolor: 'transparent',
            yaxis: { title: 'Time (min)' },
            xaxis: { title: 'HeartRate (bpm)'},
            margin: {
                l: 50, // Left margin
                r: 0, // Right margin
                t: 20, // Top margin
                b: 50  // Bottom margin
            },
        };
        
        var config = {
            displayModeBar: false,
        }

        // Create the 2D density plot
        Plotly.newPlot(chartID, data, layout, config);
        }

function customPaceLabels(values) {
    return values.map(value => {
        var minutes = Math.floor(value); // Extract the minutes part
        var seconds = (value - minutes) * 60; // Extract the seconds part
        return minutes + ":" + seconds.toString().padStart(2, '0');
    });
}

function createArrayWithSteps(start, end, step) {
    const result = [];
    for (let i = start; i <= end; i += step) {
        result.push(i);
    }
    return result;
}