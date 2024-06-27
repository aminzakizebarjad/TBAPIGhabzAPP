async function fetchWithForm(link, formData) {
  try {
    const response = await fetch(link, {
      method: "POST",
      body: formData,
    });
    const result = await response.json();
    // console.log("Success in func:", result);
    return result;

  } catch (error) {
    console.error("Error:", error);
  }
}


document.addEventListener("DOMContentLoaded", function() {

    function hideDynamicText(){
        errorDiv.hidden = true;
        startErrorDiv.hidden = true;
        stopErrorDiv.hidden = true;
        dataDive.hidden = true;
    }

    const errorDiv = document.getElementById("error-division");
    const startErrorDiv = document.getElementById("error-start-time-division");
    const stopErrorDiv = document.getElementById("error-stop-time-division");
    const dataDive = document.getElementById("data-div")

    // const meterNameSelect = document.getElementById(meter_place_selection);
    const meterKind = document.getElementById("meter_kind_selection");
    const meterName = document.getElementById("meter_place_selection");
    const startTime = document.getElementById("telemetry_start_date");
    const endTime = document.getElementById("telemetry_stop_date");
    // meterKind.disabled = true;


    console.log("DOM fully loaded and parsed");

    // hiding error division if any change done in them.
    meterName.addEventListener("input",function () {
        hideDynamicText()
    })
    startTime.addEventListener("input",function () {
        hideDynamicText()
    })
    endTime.addEventListener("input",function () {
        hideDynamicText()
    })

    meterKind.addEventListener("change",function () {
      console.log(meterKind.value );
      hideDynamicText()
      // console.log(meterKind.value === "water")
        const meterNameSelect = document.getElementById("meter_place_selection");

        // if another option is selected from meterKind then we must remove the previously added options to meterNameSelect
        while(meterNameSelect.options.length>1)
        {
            meterNameSelect.remove(1)
        }

      if (meterKind.value === "None"){

        meterNameSelect.disabled = true;
        }
      else {
          meterNameSelect.disabled = false;
          const formData = new FormData();
          formData.append('meterKind', meterKind.value)
          fetchWithForm('/meter_name_API', formData).then(result=>{
              console.log(result)
              for (const opt of Object.keys(result))
              {
                  var option = document.createElement("option");
                  option.text = result[opt][0];
                  option.value = opt;
                  meterNameSelect.add(option);
              }
          });

      }
      }
  );

    const submitButt = document.getElementById('submit-butt');

    submitButt.addEventListener("click", function (){

        const spinner = document.getElementById("spinner");
        // when butt is clicked then the butt will change
        // submitButt.innerText = '';  // text is disappeared
        submitButt.hidden = true;  // text is disappeared
        spinner.hidden = false; // spinner is shown

        // end change of butt

        errorDiv.hidden = true;
        startErrorDiv.hidden = true;
        stopErrorDiv.hidden = true;
        dataDive.hidden = true;

        const formData = new FormData();
        formData.append('meterKind', meterKind.value);
        formData.append('meterName', meterName.value);
        formData.append('startTime', startTime.value);
        formData.append('endTime', endTime.value);
        fetchWithForm("/get_meter_data_API",formData).then(response=>{
            console.log(response);
            // submitButt.innerText = '';  // text is disappeared
            submitButt.hidden = false;  // text is disappeared
            spinner.hidden = true; // spinner is shown

            if(response['error-meter-kind']){
                errorDiv.hidden = false;
                errorDiv.innerText = 'می بایست یک نوع کنتور انتخاب کنید.'
            }
            else if (response['error-meter-name']){
                errorDiv.hidden = false;
                errorDiv.innerText = 'می بایست محل کنتور را تعیین کنید.'
            }
            else if (response['error-start-time']){
                errorDiv.hidden = false;
                errorDiv.innerText = 'تاریخ ابتدای وارد شده صحیح نیست یا آن را وارد نکرده اید.'
            }
            else if (response['error-stop-time']){
                errorDiv.hidden = false;
                errorDiv.innerText = 'تاریخ انتهای وارد شده صحیح نیست یا آن را وارد نکرده اید.'
            }
            else if (response['error-time-seq']){
                errorDiv.hidden = false;
                errorDiv.innerText = 'تاریخ انتها عقب تر از تاریخ ابتدا می باشد!'
            }

            if (response['error-time-start-avlbl']){
                startErrorDiv.hidden = false;
                startErrorDiv.innerText = 'در تاریخ ابتدا داده ای وجود ندارد.'
            }

            if (response['error-time-stop-avlbl']){
                stopErrorDiv.hidden = false;
                stopErrorDiv.innerText = 'در تاریخ انتها داده ای وجود ندارد.'
            }

            const avlbData = response['data']
            console.log(avlbData)
            if(avlbData['available']){
                dataDive.style.marginTop = '2rem'
                dataDive.style.color = 'green'
                dataDive.style.borderColor = 'magenta'
                dataDive.style.textAlign = 'center'
                dataDive.style.direction = "rtl";
                dataDive.hidden = false
                dataDive.innerText = `مقدار مصرفی در این بازه ${avlbData['telemetry-diff']} ${avlbData['unit']} می باشد. `
                // const telDiff = avlbData['telemetry-diff']
                // const telUnit = avlbData['unit']
            }
        }).catch((e)=>{
            console.log(e);
        });


    });
});

// document.addEventListener("DOMContentLoaded", function() {
//
//     const submitButt = document.getElementById('submit-butt');
//
//     submitButt.addEventListener("click", function () {
//         const meterKind = document.getElementById("meter_kind_selection");
//         const meterName = document.getElementById("meter_place_selection");
//         const startTime = document.getElementById("telemetry_start_date");
//         const endTime = document.getElementById("telemetry_stop_date");
//         const formData = new FormData();
//         formData.append('meterKind', meterKind.value);
//         formData.append('meterName', meterName.value);
//         formData.append('startTime', startTime.value);
//         formData.append('endTime', endTime.value);
//         fetch("/get_meter_data_API", {
//             method:'POST',
//             body:formData,
//         }).then(response => {
//             console.log(response);
//         }).catch((e) => {
//             console.log(e);
//         });
//
//     });
//
// });