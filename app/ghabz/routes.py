from flask import Blueprint
from flask import render_template,request, jsonify
from .util import jalali_string_to_time

ghabz_bp = Blueprint('ghabz', __name__, template_folder='templates', static_folder='static', url_prefix='/ghabz')

@ghabz_bp.route('/')
def hello_world():  # put application's code here

    return render_template("Tel_Page.html")

@ghabz_bp.post('/choose water')
def calculate_meter():
    print(request.form.keys())
    for k in request.form.keys():
        print(request.form.get(k))

    return render_template("Tel_Page.html")

from .APITB import wholeKeeeper, get_device_alive, base_url, username, password, RestClientCE, decor_get_nearest_time_epoch, get_device_entity_by_name
@ghabz_bp.post('/meter_name_API')
def meter_name_API():
    meter_kind = request.form.get('meterKind')
    return jsonify(wholeKeeeper[meter_kind])

meter_data_return_dict ={'error-start-time': None}
@ghabz_bp.post('/get_meter_data_API')
def get_meter_data_API():

    # gather form data returned from js fetch API
    meter_kind = request.form.get('meterKind')
    meter_name = request.form.get('meterName')
    start_time = request.form.get('startTime')
    stop_time = request.form.get('endTime')
    clk_EN = request.form.get('clkEN')
    start_clock = request.form.get('startClock')
    stop_clock = request.form.get('stopClock')
    print(meter_name,meter_kind,start_time,stop_time,clk_EN,start_clock,stop_clock)

    # TODO: add some data to say if we can access to API else return error to service in front
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

    meter_data_return_dict.update({'error-start-clock': False})
    meter_data_return_dict.update({'error-stop-clock': False})
    raisedStartEpoch = 0
    raisedStopEpoch = 0
    if clk_EN:
        colonOcurrClockStart = str(start_clock).count(':')
        colonOcurrClockStop = str(start_clock).count(':')
        if colonOcurrClockStart == 1:
            startClockList = str(start_clock).split(':')
            try:
                raisedStartEpoch = (int(startClockList[0]) * 60 + int(startClockList[1])) * 60
            except:
                meter_data_return_dict.update({'error-start-clock': true})

        if colonOcurrClockStop == 1:
            stopClockList = str(stop_clock).split(':')
            try:
                raisedStopEpoch = (int(stopClockList[0]) * 60 + int(stopClockList[1])) * 60
            except:
                meter_data_return_dict.update({'error-stop-clock': true})

    # see if the Dates are valid
    start_epoch = jalali_string_to_time(start_time)
    stop_epoch = jalali_string_to_time(stop_time)

    print('start epoch bef:', start_epoch)

    start_epoch = start_epoch + raisedStartEpoch
    stop_epoch = stop_epoch + raisedStopEpoch

    print('start epoch aft:', start_epoch)

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
        from .APITB import epochDistanceToCheck, maxBoundaryTSRetry

        if clk_EN:
            epochDistanceToCheck = 1  # 1 minutes each query
            maxBoundaryTSRetry = .1  # .1*60 = 6 minutes

        print('maxBoundaryTSRetry, ',epochDistanceToCheck, maxBoundaryTSRetry)

        time_in_data_available_start = decor_get_nearest_time_epoch(restClient=rest_client,
                                                                    deviceName=meter_name_approved[1],
                                                                    date=start_epoch,  # TODO: change it to string time or other functions
                                                                    key_to_ask_for_nearest=meter_name_approved[2],
                                                                    from_epoch=True,
                                                                    epochDistanceToCheckInner=epochDistanceToCheck,
                                                                    maxBoundaryTSRetryInner=maxBoundaryTSRetry)

        if not time_in_data_available_start:
            meter_data_return_dict.update({'error-time-start-avlbl': True})

        # get nearest data to stop epoch
        time_in_data_available_stop = decor_get_nearest_time_epoch(restClient=rest_client,
                                                                    deviceName=meter_name_approved[1],
                                                                    date=stop_epoch,  # TODO: change it to string time or other functions
                                                                    key_to_ask_for_nearest=meter_name_approved[2],
                                                                    from_epoch=True,
                                                                    epochDistanceToCheckInner=epochDistanceToCheck,
                                                                    maxBoundaryTSRetryInner=maxBoundaryTSRetry)
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
                data.update({"telemetry-diff": round(data_end_decode-data_start_decode,3)})
                # print(data_end.get())
                data.update({'unit': 'متر مکعب'})
            elif meter_kind == 'electricity':
                data.update({"telemetry-diff": round((data_end_decode - data_start_decode)*meter_name_approved[3],3)})
                # print(data_end)
                data.update({'unit': 'کیلو وات ساعت'})


    # TODO: check the data to

    print(data)
    meter_data_return_dict.update({'data': data}) # TODO: include unit and value to data
    print('here', meter_data_return_dict)

    return jsonify(meter_data_return_dict)