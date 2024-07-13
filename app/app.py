from flask import Flask
from flask import redirect, url_for, render_template,request, jsonify
from requests import get as API_GET
from requests import post as API_POST
from .util import jalali_string_to_time
import os

base_url_path = os.getenv("SCRIPT_NAME")
if not base_url_path:
    base_url_path = '/'
    print('not found base path')
app = Flask(__name__)
app.config['APPLICATION_ROOT'] = base_url_path
# print('base_url_path', base_url_path)
# print('APPLICATION_ROOT', app.config.get('APPLICATION_ROOT'))
# print('root_path', app.root_path)
# print('static_url_path', app.static_url_path)
# print('url_map', app.url_map)
# print('template_folder', app.template_folder)
@app.route('/')
def hello_world():  # put application's code here

    return render_template("Tel_Page.html")

@app.post('/choose water')
def calculate_meter():
    print(request.form.keys())
    for k in request.form.keys():
        print(request.form.get(k))

    return render_template("Tel_Page.html")

from .APITB import wholeKeeeper, get_device_alive, base_url, username, password, RestClientCE, decor_get_nearest_time_epoch, get_device_entity_by_name
@app.post('/meter_name_API')
def meter_name_API():
    meter_kind = request.form.get('meterKind')
    return jsonify(wholeKeeeper[meter_kind])

meter_data_return_dict ={'error-start-time': None}
@app.post('/get_meter_data_API')
def get_meter_data_API():

    # gather form data returned from js fetch API
    meter_kind = request.form.get('meterKind')
    meter_name = request.form.get('meterName')
    start_time = request.form.get('startTime')
    stop_time = request.form.get('endTime')
    print(meter_name,meter_kind,start_time,stop_time)

    # TODO: add some data to say if we can access to API
    # login to API
    rest_client = RestClientCE(base_url=base_url)
    rest_client.login(username=username, password=password)

    # get data from DB
    meter_kind_approved= wholeKeeeper.get(meter_kind)

    # meter kind field checking
    if meter_kind_approved:
        meter_data_return_dict.update({'error-meter-kind': None})
    else:
        # meter_data_return_dict.update({'error-meter-kind': 'این نوع دیوایس وجود ندارد.'})
        meter_data_return_dict.update({'error-meter-kind': True})


    # print('here')
    #meter name fileld checking
    meter_name_approved = None
    meter_data_return_dict.update({'error-meter-name': None})
    if  meter_kind_approved:
        meter_name_approved = meter_kind_approved.get(meter_name)
        if not meter_name_approved:
            # meter_data_return_dict.update({'error-meter-name': 'دیوایسی با این نام وجود ندارد.'})
            meter_data_return_dict.update({'error-meter-name': True})


    # see if the device is alive
    isAlive = False

    meter_data_return_dict.update({'isAlive': isAlive})
    if meter_name_approved:
        print(meter_name_approved[1])
        isAlive = get_device_alive(restClient=rest_client, deviceName=meter_name_approved[1])
        meter_data_return_dict.update({'isAlive':isAlive})
        # print('checking is alive', meter_data_return_dict)


    # see if the Dates are valid
    start_epoch = jalali_string_to_time(start_time)
    stop_epoch = jalali_string_to_time(stop_time)
    print('epoch:' ,start_epoch)
    meter_data_return_dict.update({'error-start-time': None})
    if not start_epoch:
        # meter_data_return_dict.update({'error-start-time': 'فرمت تاریخ ابتدا صحیح نیست'})
        meter_data_return_dict.update({'error-start-time': True})

    meter_data_return_dict.update({'error-stop-time': None})
    if not stop_epoch:
        # meter_data_return_dict.update({'error-stop-time': 'فرمت تاریخ انتها صحیح نیست'})
        meter_data_return_dict.update({'error-stop-time': True})

    meter_data_return_dict.update({'error-time': None})
    if start_epoch and stop_epoch:
        if not start_epoch < stop_epoch :
            # meter_data_return_dict.update({'error-time': 'تاریخ ابتدا جلوتر از تاریخ انتها است.'})
            meter_data_return_dict.update({'error-time-seq': True})

    # start to query
    data = {'available': False}
    meter_data_return_dict.update({'error-time-start-avlbl': None})
    meter_data_return_dict.update({'error-time-stop-avlbl': None})

    if meter_kind_approved and meter_name_approved and start_epoch and stop_epoch and start_epoch < stop_epoch:

        #get nearest data to start epoch
        time_in_data_available_start = decor_get_nearest_time_epoch(restClient=rest_client,
                                                                    deviceName=meter_name_approved[1],
                                                                    date=start_epoch,  # TODO: change it to string time or other functions
                                                                    key_to_ask_for_nearest=meter_name_approved[2],
                                                                    from_epoch=True)

        if not time_in_data_available_start:
            meter_data_return_dict.update({'error-time-start-avlbl': True})

        # get nearest data to stop epoch
        time_in_data_available_stop = decor_get_nearest_time_epoch(restClient=rest_client,
                                                                    deviceName=meter_name_approved[1],
                                                                    date=stop_epoch,  # TODO: change it to string time or other functions
                                                                    key_to_ask_for_nearest=meter_name_approved[2],
                                                                    from_epoch=True)
        if not time_in_data_available_stop:
            meter_data_return_dict.update({'error-time-stop-avlbl': True})
        print('here', meter_data_return_dict)
        deviceEntity = get_device_entity_by_name(restClient=rest_client, deviceName=meter_name_approved[1])

        if time_in_data_available_stop and time_in_data_available_start:  # check if data is available in such epochs
            data_start = rest_client.get_timeseries(entity_id=deviceEntity, keys=meter_name_approved[2],
                                             start_ts=time_in_data_available_start-1,
                                                   end_ts=time_in_data_available_start +1)
            data_start_decode = float(data_start.get(meter_name_approved[2])[0].get('value'))
            data_end = rest_client.get_timeseries(entity_id=deviceEntity, keys=meter_name_approved[2],
                                                   start_ts=time_in_data_available_stop - 1,
                                                   end_ts=time_in_data_available_stop + 1)
            data_end_decode = float(data_end.get(meter_name_approved[2])[0].get('value'))


            data.update({'available': True})
            if meter_kind == 'water':
                data.update({"telemetry-diff": data_end_decode-data_start_decode})
                # print(data_end.get())
                data.update({'unit': 'متر مکعب'})
            elif meter_kind == 'electricity':
                data.update({"telemetry-diff": (data_end_decode - data_start_decode)*meter_name_approved[3]})
                # print(data_end)
                data.update({'unit': 'کیلو وات ساعت'})


    # TODO: check the data to

    print(data)
    meter_data_return_dict.update({'data': data}) # TODO: include unit and value to data
    print('here', meter_data_return_dict)

    return jsonify(meter_data_return_dict)


if __name__ == '__main__':
    app.run()
