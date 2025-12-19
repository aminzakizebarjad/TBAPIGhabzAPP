

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

    let navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach((link) => {
        link.classList.remove('active');
    });

    const nav_item = document.getElementById("nav-ghabz");
    nav_item.classList.add('active');

    let myChart;



    const errorDiv = document.getElementById("error-division");
    const startErrorDiv = document.getElementById("error-start-time-division");
    const stopErrorDiv = document.getElementById("error-stop-time-division");
    const dataDive = document.getElementById("data-div");
    const meterKind = document.getElementById("meter_kind_selection");
    const meterName = document.getElementById("meter_place_selection");
    const allmeterplacesTable = document.getElementById("all_meter_places_table");
    const allmeterplacesTable2 = document.getElementById("all_meter_places_table2");
    // const chartneeded2;
    const heading2 = document.getElementById("heading2");
    const startTime = document.getElementById("telemetry_start_date");
    const endTime = document.getElementById("telemetry_stop_date");
    const clockCheckBox = document.getElementById("clockCheckBox");
    const singlechoosingCheckBox = document.getElementById("singlechoosingCheckBox");
    const startDataDesc = document.getElementById("start_data");
    const stopDataDesc = document.getElementById("stop_data");
    const startClockDiv = document.getElementById("divStartClock");
    const stopClockDiv = document.getElementById("divStopClock");
    const startClock = document.getElementById("telemetry_start_clock");
    const stopClock = document.getElementById("telemetry_stop_clock");
    const submitButt = document.getElementById("submit-butt");
    const spinner = document.getElementById("spinner");
    var clockEN = false;


    function hideDynamicText() {
        errorDiv.hidden = true;
        startErrorDiv.hidden = true;
        stopErrorDiv.hidden = true;
        dataDive.hidden = true;
    }

    function setTableHead(){
        if(meterKind.value == "water")
            heading2.innerHTML = ` مقدار مصرفی (متر مکعب)`;
        else if(meterKind.value == "electricity")
            heading2.innerHTML = ` مقدار مصرفی (کیلو وات ساعت)`;
        else if(meterKind.value == "gas")
            heading2.innerHTML = ` مقدار مصرفی (متر مکعب)`;
    }
    function pageInit(){
        meterName.hidden = true;
        startClockDiv.hidden = true;
        stopClockDiv.hidden = true;
        allmeterplacesTable.hidden = true;
    }
    function enableClock() {
        startDataDesc.hidden = true;
        stopDataDesc.hidden = true;
        startClockDiv.hidden = false;
        stopClockDiv.hidden = false;
        clockEN = true;
    }
    function disableClock() {
        startDataDesc.hidden = false;
        stopDataDesc.hidden = false;
        startClockDiv.hidden = true;
        stopClockDiv.hidden = true;
        clockEN = false;
    }

    pageInit();

    clockCheckBox.addEventListener("change", function () {
        if (clockCheckBox.checked) {
            enableClock();
        } else {
            disableClock();
        }
    });

    function enablemeterName() {
        meterName.hidden = false;
        allmeterplacesTable.hidden = true;
        allmeterplacesTable2.hidden = true;
        dataDive.hidden = true;
        // Check if chart already exists and destroy it
        if (myChart) {
            myChart.destroy();
        }
    }

    function disablemeterName() {
        meterName.hidden = true;
        meterName.value = "None";
        allmeterplacesTable.hidden = true;
        allmeterplacesTable2.hidden = true;
        dataDive.hidden = true;
        // Check if chart already exists and destroy it
        if (myChart) {
            myChart.destroy();
        }
    }

    singlechoosingCheckBox.addEventListener("change", function () {
        if (singlechoosingCheckBox.checked) {
            enablemeterName();
        } else {
            disablemeterName();
        }
    });

    meterName.addEventListener("input", hideDynamicText);
    startTime.addEventListener("input", hideDynamicText);
    endTime.addEventListener("input", hideDynamicText);

    meterKind.addEventListener("change", function () {
        allmeterplacesTable.hidden = true;
        allmeterplacesTable2.hidden = true;
        // Check if chart already exists and destroy it
        if (myChart) {
            myChart.destroy();
        }

        console.log(meterKind.value);
        setTableHead();
        hideDynamicText();
        const meterNameSelect = document.getElementById("meter_place_selection");

        while (meterNameSelect.options.length > 1) {
            meterNameSelect.remove(1);
        }

        // check if one of water,electricity or gas kind is chosen then enable the meter name option field and fill it by meter_name_API_url API
        if (meterKind.value === "None") {
            meterNameSelect.disabled = true;
        } else {
            meterNameSelect.disabled = false;
            const formData = new FormData();
            formData.append("meterKind", meterKind.value);
            fetchWithForm(meter_name_API_url, formData).then(result => {
                console.log(result);
                for (const opt of Object.keys(result)) {
                    var option = document.createElement("option");
                    option.text = result[opt][0];
                    option.value = opt;
                    // console.log(opt);
                    meterNameSelect.add(option);
                }
            });
        }
    });

    // submit data and get all data from get_meter_data_API_url API
    submitButt.addEventListener("click", function () {
        submitButt.hidden = true;
        spinner.hidden = false;
        hideDynamicText();

        // Check if chart already exists and destroy it
        if (myChart) {
            myChart.destroy();
        }

        const formData = new FormData();

        if (singlechoosingCheckBox.checked) {
            formData.append("meterKind", meterKind.value);
            formData.append("meterName", meterName.value);
            formData.append("startTime", startTime.value);
            formData.append("endTime", endTime.value);
            formData.append("clkEN", clockEN);
            if (!clockEN) {
                startClock.value = null;
                stopClock.value = null;
            }
            formData.append("startClock", startClock.value);
            formData.append("stopClock", stopClock.value);

            // // Check if chart already exists and destroy it
            // if (myChart) {
            //     myChart.destroy();
            // }

            fetchWithForm(get_meter_data_API_url, formData).then(response => {
                console.log(response);
                submitButt.hidden = false;
                spinner.hidden = true;

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
                // else if (!response["isAlive"]) {
                //     errorDiv.hidden = false;
                //     errorDiv.innerText = "دستگاه مورد نظر فعال نیست، پشتیبانی را خبر کنید.";
                // }

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

                const avlbData = response["data"];
                console.log(avlbData);
                if (avlbData["available"]) {
                    dataDive.style.marginTop = "2rem";
                    dataDive.style.color = "green";
                    dataDive.style.borderColor = "magenta";
                    dataDive.style.textAlign = "center";
                    dataDive.style.direction = "rtl";
                    dataDive.hidden = false;
                    dataDive.innerText = `مقدار مصرفی در این بازه ${avlbData["telemetry-diff"]} ${avlbData["unit"]} می باشد. `;
                }

                // charts only when singlechoosingCheckBox.checked
                // Update chart data
                var chartneeded = response['data_daybyday']
                var chartneeded2 = response['days_separated']
                var chartneeded3 = response['daysName']
                const chartlabels = []
                const chartlabelsmain = []
                const chartlabelsmain2 = []
                const concatenatedList = [];
                const chartdatas = []
                var chartTitle = meterName.value;
                for (const i of Object.keys(chartneeded)) {
                    chartlabels.push(i)
                    chartdatas.push(chartneeded[i]["telemetry-diff"])
                }
                for (const j of Object.keys(chartneeded2)){
                    chartlabelsmain.push(chartneeded2[j])
                }
                if (!clockEN)
                    chartlabelsmain.pop()

                for (const k of Object.keys(chartneeded3)){
                    chartlabelsmain2.push(chartneeded3[k])
                }
                if (!clockEN)
                    chartlabelsmain2.pop()

                for (let i = 0; i < chartlabelsmain.length; i++) {
                    concatenatedList.push(chartlabelsmain[i] + chartlabelsmain2[i]);
                }
                // console.log(chartlabelsmain);
                // console.log(chartlabelsmain2);
                console.log(concatenatedList);
                // console.log(chartdatas);
                if (concatenatedList.length <= 1) {
                    return; // Exit the function and prevent chart rendering
                }


                // Combine labels and data, then sort
                const combined = chartlabels.map((label, index) => ({
                    label: label,
                    data: chartdatas[index]
                })).sort((a, b) => {
                    const numA = parseInt(a.label.match(/\d+/)[0], 10); // Extract numeric part from label
                    const numB = parseInt(b.label.match(/\d+/)[0], 10); // Extract numeric part from label
                    return numA - numB;
                });

                // Split the combined array back into labels and data arrays
                const sortedLabels = combined.map(item => item.label);
                const sortedData = combined.map(item => item.data);

                console.log(sortedData);
                // console.log(sortedLabels);
                if (concatenatedList.length <= 1) {
                    return; // Exit the function to prevent chart rendering
                }

                // Render the chart
                const ctx = document.getElementById('myLineChart').getContext('2d');
                const data = {
                    labels: concatenatedList,
                    datasets: [{
                        label: chartTitle,
                        backgroundColor: 'rgb(75, 192, 192)',
                        borderColor: 'rgb(75, 192, 192)',
                        data: sortedData,
                        pointStyle: 'circle',
                        pointRadius: 5,
                        pointHoverRadius: 10
                    }]
                };
                const chartAreaBorder = {
                  id: 'chartAreaBorder',
                  beforeDraw(chart, args, options) {
                    const {ctx, chartArea: {left, top, width, height}} = chart;
                    ctx.save();
                    // ctx.strokeStyle = options.borderColor;
                    ctx.lineWidth = options.borderWidth;
                    // ctx.setLineDash(options.borderDash || []);
                    ctx.lineDashOffset = options.borderDashOffset;
                    ctx.strokeRect(left, top, width, height);
                    ctx.restore();
                  }
                };
                const config = {
                    type: 'line',
                    data: data,
                    options: {
                        plugins: {
                            chartAreaBorder: {
                                borderColor: 'rgb(1, 1, 1)',
                                borderWidth: 2,
                                borderDash: [5, 5],
                                borderDashOffset: 2,
                            },
                            title: {
                                display: true,
                                text: 'نمودار مقدار مصرفی روزانه در بازه مشخص شده',
                            },
                            chartAreaBorder: {
                                borderColor: 'red',
                                borderWidth: 2,
                                borderDash: [5, 5],
                                borderDashOffset: 2,
                            },
                            tooltip: {
                                usePointStyle: true,
                            }
                        },
                        animations: {
                            radius: {
                                duration: 400,
                                easing: 'linear',
                                loop: (context) => context.active
                            }
                        },
                        hoverRadius: 12,
                        hoverBackgroundColor: 'yellow',
                        interaction: {
                            mode: 'nearest',
                            intersect: false,
                            axis: 'x'
                        }
                        // plugins: {
                        //     tooltip: {
                        //         enabled: true
                        //     }
                        // }
                    },
                    plugins: [chartAreaBorder]
                };
                myChart = new Chart(ctx, config); // Save the chart instance


            }).catch(e => {
                console.log(e);
            });

        // when singlechoosingCheckBox not checked only show commulative table from all meters
        } else {
            formData.append("meterKind", meterKind.value);
            formData.append("startTime", startTime.value);
            formData.append("endTime", endTime.value);
            formData.append("clkEN", clockEN);
            if (!clockEN) {
                startClock.value = null;
                stopClock.value = null;
            }
            formData.append("startClock", startClock.value);
            formData.append("stopClock", stopClock.value);
            allmeterplacesTable.hidden = true;
            allmeterplacesTable2.hidden = true;
            fetchWithForm(get_all_meter_data_API_url, formData).then(response => {
                console.log(response);
                submitButt.hidden = false;
                spinner.hidden = true;
                //
                if (response["error-meter-kind"]) {
                    errorDiv.hidden = false;
                    errorDiv.innerText = "می بایست یک نوع کنتور انتخاب کنید.";
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

                var ndata = response['data']
                allmeterplacesTable2.innerHTML = ''; // Clear existing rows
                // heading2.innerHTML = '';
                allmeterplacesTable.hidden = false;
                allmeterplacesTable2.hidden = false;
                for (const opt of Object.keys(ndata)) {

                    var table = document.getElementById("all_meter_places_table2");
                    var row = table.insertRow();
                    var cell1 = row.insertCell(0);
                    var cell2 = row.insertCell(1);
                    cell1.innerHTML = opt;

                    const avlbData = ndata[opt]["available"];
                    // heading2.innerHTML = `(${ndata[opt]["unit"]}) مقدار مصرفی ` ;
                    if (avlbData) {
                        // cell2.innerHTML = `مقدار مصرفی در این بازه ${ndata[opt]["telemetry-diff"]} ${ndata[opt]["unit"]} می باشد. `;
                        cell2.innerHTML = `${ndata[opt]["telemetry-diff"]} `;
                    } else {
                        cell2.innerHTML = "داده ای موجود نیست";
                    }
                }

                scrollToBottom();
            }).catch(e => {
                console.log(e);
            });
        }
    });
});
