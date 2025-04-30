document.getElementById('prediction-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const cropType = document.getElementById('crop-type').value;
    const soilType = document.getElementById('soil-type').value;
    const temperature = document.getElementById('temperature').value;
    const humidity = document.getElementById('humidity').value;
    const moisture = document.getElementById('moisture').value;
    const resultContainer = document.getElementById('result');

    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            crop_type: cropType,
            soil_type: soilType,
            temperature: temperature,
            humidity: humidity,
            moisture: moisture
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            resultContainer.innerHTML = `<p>Error: ${data.error}</p>`;
        } else {
            let resultHTML = `
                <h3>Fertilizer Recommendation</h3>
                <p><strong>Primary Fertilizer:</strong> ${data.primary_fertilizer}</p>
                <p><strong>Confidence:</strong> ${data.confidence}%</p>
                <h4>Top Predictions:</h4>
                <ul>
                    ${data.top_predictions.map(pred => 
                        `<li>${pred.fertilizer}: ${pred.probability}%</li>`
                    ).join('')}
                </ul>
            `;
            resultContainer.innerHTML = resultHTML;
        }
    })
    .catch(error => {
        resultContainer.innerHTML = `<p>Error: ${error.message}</p>`;
    });
});