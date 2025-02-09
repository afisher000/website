function strava_analysis_dashboard(heatmapObj, histObj){

    // Conversions


    // Read from structures


    // Add 



    // Get elements by ID
    var heatmapDiv = document.getElementById(heatmapObj.ID)
    var histWindowSelector = document.getElementById(histObj.window)
    var histYSelector = document.getElementById(histObj.ySelector)



    // Create event listeners
    histWindowSelector.addEventListener('change', histCallbackFunction)
    histYSelector.addEventListener('change', histCallbackFunction)

    
    // Call plotting functions
    // plotAnalysisHeatmap(heatmapObj)
    plotAnalysisHistogram(histObj);


    // Callback functions
    function histCallbackFunction(eventData) {
        plotAnalysisHistogram(histObj);
    }



}

function calculateMovingSum(values, windowSize) {
    const movingSum = [];

    // Can't average until have enough data
    for (let i = 0; i < windowSize - 2; i++) {
        const sum = values.slice(0, i).reduce((acc, num) => acc+num, 0);
        movingSum.push(sum);
    }

    // Compute averaging
    for (let i = windowSize - 1; i < values.length; i++) {
        const sum = values.slice(i - windowSize + 1, i + 1).reduce((acc, num) => acc + num, 0);
        // const average = sum / windowSize;
        movingSum.push(sum);
    }

    return movingSum;
}

function fillMissingDays(data) {
    // Get date limits
    const endDate = new Date(Object.keys(data).slice(0)[0]);  
    const startDate = new Date(Object.keys(data).slice(-1)[0]);  

    // Create list of dates
    const dates = [];
    let currentDate = new Date(startDate);

    while (currentDate <= endDate) {
        dates.push(currentDate.toISOString().split('T')[0]);
        currentDate.setDate(currentDate.getDate() + 1);
    }

    // Create list of data
    const values = {};
    for (const date of dates) {

        if (data[date] !== undefined) {
            values[date] = parseFloat(data[date]);
        } else {
            values[date] = 0;
        }
    }
    return values



}

function plotAnalysisHistogram(histObj) {
    var histYSelection = document.getElementById(histObj.ySelector).value
    console.log(histYSelection);
    var histData, dates, values;


    if (histYSelection==='distance') {
        histData = fillMissingDays(histObj.distances)
        console.log(histData);
        dates = Object.keys(histData);
        values = Object.values(histData);

        yData = values.map(item => item/1609.34);
        yTitle = 'Distance (mi)';

    } else if (histYSelection==='time') {
        histData = fillMissingDays(histObj.times)
        dates = Object.keys(histData);
        values = Object.values(histData);
        yData = values.map(item => item/3600);
        yTitle = 'Time (hr)';
    }

    // Create histogram
    const data = [{
        x: dates,
        y: yData,
        type: 'bar',
        hoverinfo: 'skip',
    }];
    
    const layout = {
        plot_bgcolor: 'transparent',
        paper_bgcolor: 'transparent',
        xaxis: {
            title: 'Date',
        },
        yaxis: {
            title: yTitle
        },
        showlegend: false,
        hovermode: 'none', // Disable hover mode completely
        margin: {
            l: 60, // Left margin
            r: 50, // Right margin
            t: 10, // Top margin
            b: 60  // Bottom margin
        },
    };

    // Optionally apply moving averages
    var histWindow = parseFloat(document.getElementById(histObj.window).value)
    if (histWindow>0) {
        const movingSum = calculateMovingSum(yData, histWindow)
        data.push({
            x: dates,
            y: movingSum,
            type: 'scatter',
            mode: 'lines',
            yaxis: 'y2',
            hoverinfo: 'skip',
        })

        layout.yaxis2 = {
            title: 'Moving Sum',
            overlaying: 'y',
            side:'right',
            range: [0, calcMax(movingSum)],
        }
    }
    

    // Make Plot
    var config = {
        displayModeBar: false,
    }
    Plotly.newPlot(heatmapObj.ID, data, layout, config);

}

function plotAnalysisHeatmap(heatmapObj) {
    const heatmapData = fillMissingDays(heatmapObj.data)

    // const today = new Date();
    const startDate = new Date(Object.keys(heatmapData).slice(0)[0]);  
    const endDate = new Date(Object.keys(heatmapData).slice(-1)[0]);  
    const daysUntilSaturday = 6-endDate.getDay();


    num_weeks = Math.ceil((endDate-startDate) / (1000*60*60*24*7));

    const matrix = Array.from({ length: 7 }, () => Array(4).fill(0));
    const days = ['Sat', 'Fri', 'Thu', 'Wed', 'Tue', 'Mon', 'Sun'];
    const weeks = [];
    var cellDateStr = '';
    for (let jweek = 0; jweek < num_weeks; jweek++) {

        for (let jday = 0; jday < 7; jday++) {
            // Get date string for cell
            const cellDate = new Date(endDate);
            cellDate.setDate(endDate.getDate() + daysUntilSaturday - num_weeks*7 + 7*jweek + (6-jday) + 1);
            cellDateStr = cellDate.toISOString().split('T')[0];

            if (heatmapData.hasOwnProperty(cellDateStr)) {
                matrix[jday][jweek] = heatmapData[cellDateStr];
            } else {
                matrix[jday][jweek] = 0;
            }
        }
        weeks.push(cellDateStr);

    }

    // Truncate to max value of 3
    const truncatedMatrix = matrix.map(row => row.map(value => Math.min(value, 3)));



    const data = [{
        z: truncatedMatrix,
        x: weeks,
        y: days,
        type: 'heatmap',
        colorscale: 'Magma',
        showlegend: false,
        hoverinfo: 'none',
    }];

    const layout = {
        plot_bgcolor: 'transparent',
        paper_bgcolor: 'transparent',
        title: 'Strava Activity',
        xaxis: {side: 'bottom' }
    }

    var config = {
        displayModeBar: false,
    }

    Plotly.newPlot(heatmapObj.ID, data, layout, config);
}