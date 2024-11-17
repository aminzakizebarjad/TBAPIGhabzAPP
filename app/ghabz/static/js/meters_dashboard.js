let dataChart;


function updateTemperature(temp,time) {
    const newEntry = { time: time.toLocaleTimeString(), value: parseFloat(temp) };

    dataChart.data.datasets.push(newEntry.value);
    dataChart.data.labels.push(newEntry.time);
    dataChart.update();
}


function plotData(period) {
    console.log('Now send get me data reqest')
    const meter = document.getElementById('meterSelect').value;
    if (!meter) {
        alert('Please select a meter first.');
        return;
    }
    jQuery.noConflict();
    // $.get(`/api/meter_data?meter=${meter}&period=${period}`, function(data) {
    $.get(`/api/get_meter_data_realtime?meter=${meter}&period=${period}`, function(data) {
        // Prepare the chart data
        const labels = data.map(item => item.datetime); // Use actual datetime from the data
        const new_data = data.map(item => item.daily_value)

        const chartData = {
            labels: labels,
            datasets: [{
                label: `Usage for ${meter} (${period})`,
                data: new_data, //data,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderWidth: 2,
                fill: true
            }]
        };

        // If the chart already exists, destroy it before creating a new one
        if (dataChart) {
            dataChart.destroy();
        }

        // Create a new chart
        const ctx = document.getElementById('dataChart').getContext('2d');
        dataChart = new Chart(ctx, {
            type: 'bar', // You can change this to 'bar', 'pie', etc.
            data: chartData,
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                    }
                }
            }
        });
    }).fail(function() {
        alert('Error fetching data. Please try again.');
    });

    const plot_area = document.getElementById('plotArea'); // Get the element by ID
    plot_area.classList.add('card'); // Add the class
    plot_area.classList.add('custom-card')

    const prediction_button = document.getElementById('predictButton');
    prediction_button.classList.remove('invisible')
    prediction_button.classList.add('visible')
}


function makePrediction() {
    const meter = document.getElementById('meterSelect').value;
    if (!meter) {
        alert('Please select a meter first.');
        return;
    }

    const predictionButton = document.getElementById('predictButton');
    const loadingSpinner = document.getElementById('loadingSpinner');

    // Disable the button and show the loading spinner
    predictionButton.disabled = true;
    loadingSpinner.style.display = 'block';

    jQuery.noConflict();
    $.post(`/api/make_prediction?meter=${meter}`, function(data) {
        // Hide the loading spinner and re-enable the button
        loadingSpinner.style.display = 'none';
        predictionButton.disabled = false;

        // Display prediction data as a new plot
        plotPrediction(data.prediction);
    }, 'json').fail(function() {
        alert('Error making prediction. Please try again.');
        
        // Hide the loading spinner and re-enable the button
        loadingSpinner.style.display = 'none';
        predictionButton.disabled = false;
    });
}

// last prediction function
// function makePrediction() {
//     const meter = document.getElementById('meterSelect').value;
//     if (!meter) {
//         alert('Please select a meter first.');
//         return;
//     }
//     console.log('Hi now going for the prediction work')
//     console.log(meter)

//     jQuery.noConflict();
//     $.post(`/api/make_prediction?meter=${meter}`, function(data) {
//         // Display prediction data as a new plot
//         console.log(`Prediction data for ${meter}:`, data.prediction);
//         plotPrediction(data.prediction);
//     }, 'json').fail(function() {
//         alert('Error making prediction. Please try again.');
//     });
// }





// function makePrediction() {
//     const meter = document.getElementById('meterSelect').value;
//     if (!meter) {
//         alert('Please select a meter first.');
//         return;
//     }
    
//     console.log('Hi now going for the prediction work');
//     console.log(meter);
    
//     const url = `/api/make_prediction?meter=${meter}`;

//     fetch(url, {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//         }
//     })
//     .then(response => {
//         if (!response.ok) {
//             throw new Error('Network response was not ok');
//         }
//         return response.json();
//     })
//     .then(data => {
//         console.log(`Prediction data for ${meter}:`, data.prediction);
//         plotPrediction(data.prediction);
//     })
//     .catch(error => {
//         alert('Error making prediction. Please try again.');
//         console.error('There was a problem with the fetch operation:', error);
//     });
// }




function plotPrediction(predictionData) {
    const meter = document.getElementById('meterSelect').value;
    
    // Prepare the prediction chart data
    // const labels = Array.from({length: predictionData.length}, (_, i) => `Predicted Day ${i + 1}`);
    const lastLabel = dataChart.data.labels[dataChart.data.labels.length - 1];
    const lastDate = new Date(lastLabel);
    
    const newLabels = predictionData.map((_, i) => {
        // Increment the last timestamp by 1 hour for each predicted data point
        const date = new Date(lastDate);
        date.setHours(lastDate.getHours() + (i + 1)); // Increment by i + 1 hours
        return date.toLocaleString(); // Convert to string format
    });

    console.log("HEHE")
    console.log(dataChart)
    console.log("HOHO")
       
    // Add the new labels to the existing dataset
    dataChart.data.labels.push(...newLabels);
    const existingData = dataChart.data.datasets[0].data;

    // Append new data, while changing the color conditionally
    const newDatasetData = existingData.concat(predictionData);
    dataChart.data.datasets[0].data = newDatasetData;

    // Update colors for the new data points
    const newColors = newDatasetData.map((_, index) => {
        return index < existingData.length ? 
            'rgba(75, 192, 192, 1)' : // Original color for old data
            'rgba(255, 99, 132, 1)';  // New color for predicted data
    });

    // Update chart's dataset color (this assumes a single dataset with color set for individual data points)
    dataChart.data.datasets[0].borderColor = newColors;
    dataChart.data.datasets[0].backgroundColor = newColors.map(color => color.replace('1)', '0.2)')); // Lighten the color for background
    
    // Add segment property for new data points (dotted line)
    dataChart.data.datasets[0].segment = {
        borderColor: 'rgba(255, 99, 132, 1)', // Color for new data line
        borderDash: [5, 5] // Dotted line pattern (5px dash, 5px gap)
    };
    
    // Update the chart with the new data
    dataChart.update();
   
}


document.addEventListener('DOMContentLoaded', function() {
    // const meterSelect = document.getElementById('meterSelect');

    // // Fetch data from the API when the page loads
    // fetch('/meters') // Replace with your API endpoint
    //     .then(response => {
    //         if (!response.ok) {
    //             throw new Error('Network response was not ok');
    //         }
    //         return response.json();
    //     })
    //     .then(data => {
    //         // Clear existing options except for the placeholder
    //         meterSelect.innerHTML = '<option value="">-- Choose a Meter --</option>';

    //         // Assuming the API returns an array of meter objects
    //         data.forEach(meter => {
    //             const newOption = document.createElement('option');
    //             newOption.value = meter.id; // Assuming 'id' is the value
    //             newOption.textContent = meter.name; // Assuming 'name' is the display text
    //             meterSelect.appendChild(newOption);
    //         });
    //     })
    //     .catch(error => {
    //         console.error('There was a problem with the fetch operation:', error);
    //     });
});
