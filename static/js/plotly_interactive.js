function test_interactive(lineID, scatterID, selectedValue, splits) {
    // Parse data
    var mps_to_mph = 2.2369362921;
    var speedData = splits.map(item => item.speed*mps_to_mph);
    var distanceData = splits.map(item => item.split/10);
    var heartrateData = splits.map(item => item.hr);
    var latData = splits.map(item => item.lat);
    var lngData = splits.map(item => item.lng);
    var gradeData = splits.map(item => item.grade*100);

    var [linearFit, _speedByGrade, zeroGradeSpeed] = linearRegression(gradeData, speedData);
    var speedGradeAdjData = speedData.map((speed, index) => speed - linearFit[index] + zeroGradeSpeed);

    if (selectedValue === 'speed') {
        yData = speedData;
    } else if (selectedValue === 'heartrate') {
        yData = heartrateData;
    } else if (selectedValue === 'speedGradeAdj') {
        yData = speedGradeAdjData;
    }

    var initialScatterColors = new Array(latData.length).fill('blue'); // Initial colors
    var initialScatterSize = new Array(latData.length).fill(6); // Initial colors
    var initialScatterZ = new Array(latData.length).fill(1); // Initial colors
    var linedata = [
        {
            x: distanceData,
            y: yData,
            type: 'scatter',
            mode: 'lines+markers',
            marker: {color: initialScatterColors, size:initialScatterSize, z:initialScatterZ},
            //hoverinfo: 'none',
        },
    ];
    

    var scatterdata = [{
            x: lngData,
            y: latData,
            type: 'scatter',
            mode: 'markers',
            marker: {color: initialScatterColors, size:initialScatterSize, z:initialScatterZ},
            hoverinfo: 'none',
        }];
    
    // Define layout input
    var linelayout = {
        yaxis: { title: 'Speed (mph)'},
        xaxis: { title: 'Distance (km)'},
        hovermode: 'closest',
    };

    var scatterlayout = {
        title:"overall title2",
        yaxis: { title: 'Longitude'},
        xaxis: { title: 'Latitude'},
    };
    
    // Make plot
    Plotly.newPlot(lineID, linedata, linelayout);
    Plotly.newPlot(scatterID, scatterdata, scatterlayout);
}