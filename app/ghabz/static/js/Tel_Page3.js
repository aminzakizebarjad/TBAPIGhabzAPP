
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
    const submitButt = document.getElementById("submit-butt");
    const spinner = document.getElementById("spinner");
    const deviceContainer = document.getElementById('deviceContainer');

    meterKind.addEventListener("change", function () {
        console.log(meterKind.value);
        hideDynamicText();

        const meterNameSelect = document.getElementById("meter_place_selection");

        // Clear the device container when meter kind is changed
        deviceContainer.innerHTML = ''; // Clear deviceContainer


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
                // for (const opt of Object.keys(result)) {
                //     var option = document.createElement("option");
                //     option.text = result[opt][0];
                //     option.value = opt;
                //     // console.log(opt);
                //     meterNameSelect.add(option);
                // }
            });
        }
    });
    submitButt.addEventListener("click", function () {
        submitButt.hidden = true;
        spinner.hidden = false;
        hideDynamicText();

        const formData = new FormData();

        formData.append("meterKind", meterKind.value);
        fetchWithForm(get_all_isAlive_data_API_url, formData).then(response => {
            console.log(response);
            submitButt.hidden = false;
            spinner.hidden = true;
            var isAliveneeded0 = response['isAlive'];
            console.log(isAliveneeded0)

            function createDeviceList() {
                const devices = Object.keys(isAliveneeded0);

                const container = document.getElementById('deviceContainer');
                container.innerHTML = ''; // Clear existing devices

                devices.forEach(device => {
                    const deviceDiv = document.createElement('div');
                    deviceDiv.className = 'deviceSquare';
                    deviceDiv.textContent = device;

                     // Check if the device is alive
                    if (isAliveneeded0[device] === true) {
                        deviceDiv.classList.add('active');
                    }

                    // Add dynamic hover effect
                    // deviceDiv.onmouseover = () => {
                    //     deviceDiv.style.transition = "transform 0.4s linear, background-color 0.4s linear";
                    //     deviceDiv.style.transform = "scale(1.2)";
                    //     deviceDiv.style.backgroundColor = "lightblue";
                    // };
                    //
                    // deviceDiv.onmouseout = () => {
                    //     deviceDiv.style.transform = "scale(1)";
                    //     deviceDiv.style.backgroundColor = "white"; // Reset to original color
                    // };

                    // // Add toggle functionality on click
                    // deviceDiv.onclick = () => {
                    //     deviceDiv.classList.toggle('active');
                    // };

                    container.appendChild(deviceDiv);
                });
            }

            if (response["error-meter-kind"]) {
                errorDiv.hidden = false;
                errorDiv.innerText = "می بایست یک نوع کنتور انتخاب کنید.";
            } else {
                // Show device container and create devices if selection is valid
                deviceContainer.style.display = 'grid';
                createDeviceList();
            }
        }).catch(e => {
            console.log(e);
        });
    });

});

