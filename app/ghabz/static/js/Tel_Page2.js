
async function scrollToBottom() {
    await page.evaluate(async () => {
        const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
        for (let i = 0; i < document.body.scrollHeight; i += 100) {
            window.scrollTo(0, i);
            await delay(100);
        }
    });
}

async function fetchWithForm(link, formData) {
    try {
        const response = await fetch(link, {
            method: "POST",
            body: formData,
        });
        const result = await response.json();
        return result;
    } catch (error) {
        console.error("Error:", error);
    }
}

document.addEventListener("DOMContentLoaded", function () {

    // let myChart;
    function hideDynamicText() {
        errorDiv.hidden = true;
        startErrorDiv.hidden = true;
        stopErrorDiv.hidden = true;
    }

    const errorDiv = document.getElementById("error-division");
    const startErrorDiv = document.getElementById("error-start-time-division");
    const stopErrorDiv = document.getElementById("error-stop-time-division");
    const meterKind = document.getElementById("meter_kind_selection");
    const meterName = document.getElementById("meter_place_selection");
    meterName.hidden = true;
    const submitButt = document.getElementById("submit-butt");
    const spinner = document.getElementById("spinner");


    let numberOfCharts = 0; // Total number of charts
    const chartsPerPage = 15; // Number of charts per page
    const chartsPerRow = 3; // Number of charts per row
    let totalPages = 0;
    const chartType = 'line'; // Use only line charts
    const chartContainer = document.getElementById('chartContainer');
    const pagination = document.getElementById('pagination');
    // const submitButton = document.getElementById('submit-butt');
    // const meterSelect = document.getElementById('meter_kind_selection');

    let currentPage = 1;


    // meterName.addEventListener("input", hideDynamicText);
    // startTime.addEventListener("input", hideDynamicText);
    // endTime.addEventListener("input", hideDynamicText);

    meterKind.addEventListener("change", function () {
        console.log(meterKind.value);
        hideDynamicText();

        // Clear all charts and reset variables
        chartContainer.innerHTML = ''; // Remove all charts
        pagination.innerHTML = ''; // Clear pagination
        currentPage = 1; // Reset current page
        num = 0; // Reset the num counter
        numberOfCharts = 0; // Reset the number of charts
        totalPages = 0; // Reset total pages

        const meterNameSelect = document.getElementById("meter_place_selection");

        while (meterNameSelect.options.length > 1) {
            meterNameSelect.remove(1);
        }

        if (meterKind.value === "None") {
            meterNameSelect.disabled = true;
        } else {
            meterNameSelect.disabled = false;
            const formData = new FormData();
            formData.append("meterKind", meterKind.value);
            fetchWithForm(meter_name_API_url, formData).then(result => {
                console.log(result);
                numberOfCharts = 0;
                for (const opt of Object.keys(result)) {
                    var option = document.createElement("option");
                    option.text = result[opt][0];
                    option.value = opt;
                    // console.log(opt);
                    meterNameSelect.add(option);
                    numberOfCharts = numberOfCharts + 1;
                    totalPages = Math.ceil((numberOfCharts*3) / chartsPerPage);
                }
            });
        }
    });
    // console.log(numberOfCharts)
    // const totalPages = Math.ceil(numberOfCharts / chartsPerPage);
    // console.log(totalPages)
    submitButt.addEventListener("click", function () {
        submitButt.hidden = true;
        spinner.hidden = false;
        numberOfCharts = numberOfCharts*3
        // console.log(numberOfCharts)
        // console.log(totalPages)
        hideDynamicText();

        const formData = new FormData();

        formData.append("meterKind", meterKind.value);
        fetchWithForm(get_all_charts_data_API_url, formData).then(response => {
            console.log(response);
            submitButt.hidden = false;
            spinner.hidden = true;
            var chartneeded0 = response['data_daybyday']
            var chartneeded1 = response['data_hourbyhour']
            var chartneeded2 = response['times_separated']
            var chartneeded3 = response['days_separated']
            var chartneeded4 = response['daysName']
            const chartTitle = []
            const rowTitles = []
            const chartlabels0 = []
            const chartlabelsmain = []
            const chartlabelsmain2 = []
            const chartlabels2 = []
            const chartdatas0 = []
            const chartdatas1 = []
            const chartdatas2 = []
            for (let op = 1; op < (numberOfCharts+1); op++){
                if (op % 3 == 1){
                    chartTitle.push('روز اخیر')
                } else if(op % 3 == 2){
                    chartTitle.push('هفته اخیر')
                } else if(op % 3 == 0){
                    chartTitle.push('ماه اخیر')
                }
            }
            for (const n of Object.keys(chartneeded1)){
                rowTitles.push(n)
            }
            for (const n of Object.keys(chartneeded2)) {
                const currentHour = chartneeded2[n];
                const nextHour = chartneeded2[(parseInt(n) + 1).toString()];

                if (nextHour !== undefined) {
                    const label = `${currentHour} - ${nextHour}`;
                    chartlabels0.push(label);
                }
            }
            for (const j of Object.keys(chartneeded3)){
                chartlabelsmain.push(chartneeded3[j])
            }
            chartlabelsmain.pop()

            for (const k of Object.keys(chartneeded4)){
                chartlabelsmain2.push(chartneeded4[k])
            }
            chartlabelsmain2.pop()
            for (let i = 0; i < chartlabelsmain.length; i++) {
                chartlabels2.push(chartlabelsmain[i] + chartlabelsmain2[i]);
            }
            const chartlabels1 = chartlabels2.slice(-7);
            for (const n of Object.keys(chartneeded1)){
                const dict1 = chartneeded1[n];
                // Sort the keys numerically
                const sortedKeys = Object.keys(dict1).sort((a, b) => {
                    // Extract the numeric part of the key by removing the "hour " prefix
                    const numA = parseInt(a.replace('hour ', ''), 10);
                    const numB = parseInt(b.replace('hour ', ''), 10);
                    return numA - numB;
                });
                for (const m of sortedKeys){
                    chartdatas0.push(dict1[m]["telemetry-diff"])
                }
            }
            for (const n of Object.keys(chartneeded0)){
                const dict0 = chartneeded0[n];
                // Sort the keys numerically
                const sortedKeys1 = Object.keys(dict0).sort((a, b) => {
                    // Extract the numeric part of the key by removing the "hour " prefix
                    const numA = parseInt(a.replace('day ', ''), 10);
                    const numB = parseInt(b.replace('day ', ''), 10);
                    return numA - numB;
                });
                for (const m of sortedKeys1){
                    chartdatas1.push(dict0[m]["telemetry-diff"])
                }
                chartdatas2.push(chartdatas1.slice(-7))
            }

            // console.log(chartdatas1)


            let num = 0;
            function renderCharts(page) {
				// Clear the container
				chartContainer.innerHTML = '';

				const startChartIndex = (page - 1) * chartsPerPage;
				const endChartIndex = Math.min(page * chartsPerPage, numberOfCharts);


                num = Math.floor(startChartIndex / 3); // Reset num based on the page

                // let num = 0;
				for (let i = startChartIndex; i < endChartIndex; i += chartsPerRow) {
					// Add a title for each row of charts
					const rowTitle = document.createElement('div');
					rowTitle.className = 'chartRowTitle';
					// rowTitle.textContent = `Row ${Math.floor(i / chartsPerRow) + 1}`;
                    rowTitle.textContent = rowTitles[i/chartsPerRow];
					chartContainer.appendChild(rowTitle);

					// Add charts in the current row
					for (let j = i; j < i + chartsPerRow && j < endChartIndex; j++) {
						const chartBox = document.createElement('div');
						chartBox.className = 'chartBox';

						const canvas = document.createElement('canvas');
						canvas.id = `chart${j}`;

                        canvas.width = 375;
                        canvas.height = 450;

						chartBox.appendChild(canvas);
						chartContainer.appendChild(chartBox);

                        // Calculate the correct data slice for each chart
                        let chartDataSlice = [];
                        if (j % 3 === 0) {  // 0th, 3rd, 6th, etc. charts
                            const chartDataIndex = Math.floor(j / 3) * 24;
                            chartDataSlice = chartdatas0.slice(chartDataIndex, chartDataIndex + 24);
                        } else if (j % 3 === 2) {
                            const chartDataIndex = Math.floor(j / 3) * 30;
                            chartDataSlice = chartdatas1.slice(chartDataIndex, chartDataIndex + 30);
                        } else if (j % 3 === 1) {
                            chartDataSlice = chartdatas2[num]
                            num = num + 1;
                        }
						const data = {
							labels: (j % 3 === 0) ? chartlabels0 :
                                    (j % 3 === 1) ? chartlabels1 :
                                    chartlabels2,
							datasets: [{
								// label: `Chart ${j + 1}`,
                                label: rowTitles[i/chartsPerRow],
								// data: Array.from({ length: 24 }, () => Math.floor(Math.random() * 100)),
                                data: chartDataSlice,
								backgroundColor: 'rgba(54, 162, 235, 0.2)',
								borderColor: 'rgba(54, 162, 235, 1)',
								borderWidth: 1
							}]
						};

						const config = {
							type: chartType, // Always line chart
							data: data,
							options: {
								scales: {
									y: {
										beginAtZero: true
									}
								},
                                plugins: {
                                    title: {
                                        display: true,
                                        text: chartTitle[j],
                                    }
                                },
                                animations: {
                                      radius: {
                                          duration: 400,
                                          easing: 'linear',
                                          loop: (context) => context.active
                                      }
                                },
                                hoverRadius: 8,
                                hoverBackgroundColor: 'yellow',
                                interaction: {
                                    mode: 'nearest',
                                    intersect: false,
                                    axis: 'x'
                                }
							}
						};

						new Chart(document.getElementById(canvas.id), config);
					}
				}
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
			}

			function setupPagination() {
				pagination.innerHTML = ''; // Clear existing pagination

				for (let i = 1; i <= totalPages; i++) {
					const button = document.createElement('button');
					button.textContent = i;
					button.addEventListener('click', () => {
						currentPage = i;
						renderCharts(currentPage);
					});
					pagination.appendChild(button);
				}
			}




            if (response["error-meter-kind"]) {
                errorDiv.hidden = false;
                errorDiv.innerText = "می بایست یک نوع کنتور انتخاب کنید.";
            } else if (response["error-meter-name"]) {
                errorDiv.hidden = false;
                errorDiv.innerText = "می بایست محل کنتور را تعیین کنید.";
            } else if (response["error-start-time"]) {
                errorDiv.hidden = false;
                errorDiv.innerText = "تاریخ ابتدای وارد شده صحیح نیست یا آن را وارد نکرده اید.";
            } else if (response["error-stop-time"]) {
                errorDiv.hidden = false;
                errorDiv.innerText = "تاریخ انتهای وارد شده صحیح نیست یا آن را وارد نکرده اید.";
            } else if (response["error-time-seq"]) {
                errorDiv.hidden = false;
                errorDiv.innerText = "تاریخ انتها عقب تر از تاریخ ابتدا می باشد!";
            }
            if (response["error-time-start-avlbl"]) {
                startErrorDiv.hidden = false;
                startErrorDiv.innerText = "در تاریخ ابتدا داده ای وجود ندارد.";
            } else if (response["error-start-clock"]) {
                startErrorDiv.hidden = false;
                startErrorDiv.innerText = "ساعت ابتدا صحیح وارد نشده است. پیشفرض 12 بامداد انتخاب شد.";
            }
            if (response["error-time-stop-avlbl"]) {
                stopErrorDiv.hidden = false;
                stopErrorDiv.innerText = "در تاریخ انتها داده ای وجود ندارد.";
            } else if (response["error-stop-clock"]) {
                stopErrorDiv.hidden = false;
                stopErrorDiv.innerText = " ساعت انتها صحیح وارد نشده است. پیشفرض 12 بامداد انتخاب شد.";
            }
            setupPagination();
            renderCharts(currentPage);

        }).catch(e => {
            console.log(e);
        });
    });



});

