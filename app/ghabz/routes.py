import os
import jdatetime

from flask import Blueprint
from flask import render_template,request, jsonify
from .util import jalali_string_to_time
import sys
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



from .APITB import wholeKeeeper,  base_url, username, password, RestClientCE, decor_get_nearest_time_epoch, get_device_entity_by_name
@ghabz_bp.post('/meter_name_API')
def meter_name_API():
    meter_kind = request.form.get('meterKind')
    return jsonify(wholeKeeeper[meter_kind])

meter_data_return_dict ={'error-start-time': None}
all_meter_data_return_dict ={'error-start-time': None}
@ghabz_bp.post('/get_meter_data_API')
def get_meter_data_API():

    # gather form data returned from js fetch API
    meter_kind = request.form.get('meterKind')
    meter_name = request.form.get('meterName')
    start_time = request.form.get('startTime')
    stop_time = request.form.get('endTime')
    clk_EN = request.form.get('clkEN')
    if (str(clk_EN)  == 'true'):
        clk_EN = True
    else:
        clk_EN = False
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
        # isAlive = get_device_alive(restClient=rest_client, deviceName=meter_name_approved[1])
        # meter_data_return_dict.update({'isAlive':isAlive})
        # print('checking is alive', meter_data_return_dict)

    meter_data_return_dict.update({'error-start-clock': False})
    meter_data_return_dict.update({'error-stop-clock': False})
    raisedStartEpoch = 0
    raisedStopEpoch = 0
    if clk_EN == True:
        print("in here to ask clock valid" )
        colonOcurrClockStart = str(start_clock).count(':')
        colonOcurrClockStop = str(stop_clock).count(':')
        if colonOcurrClockStart == 1:
            startClockList = str(start_clock).split(':')
            try:
                raisedStartEpoch = (int(startClockList[0]) * 60 + int(startClockList[1])) * 60
                print(raisedStartEpoch)
            except:
                meter_data_return_dict.update({'error-start-clock': True})
        else:
            meter_data_return_dict.update({'error-start-clock': True})

        if colonOcurrClockStop == 1:
            stopClockList = str(stop_clock).split(':')
            try:
                raisedStopEpoch = (int(stopClockList[0]) * 60 + int(stopClockList[1])) * 60
                print(raisedStopEpoch)
            except:
                meter_data_return_dict.update({'error-stop-clock': True})
        else:
            meter_data_return_dict.update({'error-stop-clock': True})


    # see if the Dates are valid
    start_epoch = jalali_string_to_time(start_time)
    stop_epoch = jalali_string_to_time(stop_time)


    print('start epoch bef:', start_epoch)
    if not start_epoch == None:
        start_epoch = start_epoch + raisedStartEpoch
        if sys.platform.startswith('linux'):
            start_epoch = start_epoch - (3 * 60 + 30) * 60

    if not stop_epoch == None:
        stop_epoch = stop_epoch + raisedStopEpoch
        if sys.platform.startswith('linux'):
            stop_epoch = stop_epoch - (3 * 60 + 30) * 60

    print('start epoch aft:', start_epoch)

    print('epoch:' ,start_epoch)
    meter_data_return_dict.update({'error-start-time': None})
    if start_epoch == None:
        # meter_data_return_dict.update({'error-start-time': 'فرمت تاریخ ابتدا صحیح نیست'})
        meter_data_return_dict.update({'error-start-time': True})

    meter_data_return_dict.update({'error-stop-time': None})
    if stop_epoch == None:
        # meter_data_return_dict.update({'error-stop-time': 'فرمت تاریخ انتها صحیح نیست'})
        meter_data_return_dict.update({'error-stop-time': True})

    meter_data_return_dict.update({'error-time-seq': None})
    time_approved = False
    if ( not start_epoch == None) and ( not stop_epoch == None):
        if (start_epoch > stop_epoch):
            print(start_epoch, stop_epoch, )
            # meter_data_return_dict.update({'error-time': 'تاریخ ابتدا جلوتر از تاریخ انتها است.'})
            meter_data_return_dict.update({'error-time-seq': True})
        else:
            time_approved = True

    # start to query
    data = {'available': False}
    meter_data_return_dict.update({'error-time-start-avlbl': None})
    meter_data_return_dict.update({'error-time-stop-avlbl': None})

    if (not meter_kind_approved == None)\
            and (not meter_name_approved == None)\
            and (time_approved == True):

        #get nearest data to start epoch
        from .APITB import epochDistanceToCheck, maxBoundaryTSRetry

        if clk_EN == True:
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
        print('time_in_data_available_start is : ',time_in_data_available_start)
        print('start_epoch is : ',start_epoch)
        print('stop_epoch is : ', stop_epoch)

        if time_in_data_available_start == 0:
            meter_data_return_dict.update({'error-time-start-avlbl': True})

        # get nearest data to stop epoch
        time_in_data_available_stop = decor_get_nearest_time_epoch(restClient=rest_client,
                                                                    deviceName=meter_name_approved[1],
                                                                    date=stop_epoch,  # TODO: change it to string time or other functions
                                                                    key_to_ask_for_nearest=meter_name_approved[2],
                                                                    from_epoch=True,
                                                                    epochDistanceToCheckInner=epochDistanceToCheck,
                                                                    maxBoundaryTSRetryInner=maxBoundaryTSRetry)
        if time_in_data_available_stop == 0:
            meter_data_return_dict.update({'error-time-stop-avlbl': True})

        print('here', meter_data_return_dict)
        deviceEntity = get_device_entity_by_name(restClient=rest_client, deviceName=meter_name_approved[1])

        if (not time_in_data_available_stop == 0) and (
        not time_in_data_available_start == 0):  # check if data is available in such epochs
            data_start = rest_client.get_timeseries(entity_id=deviceEntity, keys=meter_name_approved[2],
                                                    start_ts=time_in_data_available_start - 1,
                                                    end_ts=time_in_data_available_start + 1)
            print(rest_client)
            print('lets see the data_start: ', data_start)
            data_start_decode = float(data_start.get(meter_name_approved[2])[0].get('value'))
            print('lets see the data_start_decode: ', data_start_decode)
            data_end = rest_client.get_timeseries(entity_id=deviceEntity, keys=meter_name_approved[2],
                                                  start_ts=time_in_data_available_stop - 1,
                                                  end_ts=time_in_data_available_stop + 1)
            print('so lets see the data_end: ', data_end)
            data_end_decode = float(data_end.get(meter_name_approved[2])[0].get('value'))

            data.update({'available': True})
            if meter_kind == 'water':
                data.update({"telemetry-diff": round(data_end_decode - data_start_decode, 3)})
                # print(data_end.get())
                data.update({'unit': 'متر مکعب'})
            elif meter_kind == 'electricity':
                data.update(
                    {"telemetry-diff": round((data_end_decode - data_start_decode) * meter_name_approved[3], 3)})
                # print(data_end)
                data.update({'unit': 'کیلو وات ساعت'})

    # TODO: check the data to

    print(data)
    meter_data_return_dict.update({'data': data}) # TODO: include unit and value to data
    print('here', meter_data_return_dict)


    start_time_str = start_time.replace('/', '-')
    stop_time_str = stop_time.replace('/', '-')
    start_date = jdatetime.datetime.strptime(start_time_str, '%Y-%m-%d')
    stop_date = jdatetime.datetime.strptime(stop_time_str, '%Y-%m-%d')
    print(start_date, stop_date)
    difference_date = (stop_date - start_date).days
    days_counter = difference_date +1
    print(f"Total number of days including both dates: {days_counter}")
    days_separated = [start_date.strftime('%Y-%m-%d')];

    next_day = start_date
    for i in range(1, days_counter):
        next_day += jdatetime.timedelta(days=1)
        days_separated.append(next_day.strftime('%Y-%m-%d'))

    print("Days separated:", days_separated)
    meter_data_return_dict.update({'days_separated': days_separated}) # TODO: include unit and value to data
    print('here', meter_data_return_dict)

    fulldaysName = [ ' شنبه',' یکشنبه',' دوشنبه',' سه شنبه',' چهارشنبه',' پنج شنبه',' جمعه']
    # daysName = [fulldaysName[start_date.weekday()]]
    daysName = []
    for day in days_separated:
        day_date = jdatetime.datetime.strptime(day, '%Y-%m-%d')
        daysName.append(fulldaysName[day_date.weekday()])

    # print("Days name:", daysName)
    meter_data_return_dict.update({'daysName': daysName})
    # start_epd = jalali_string_to_time(days_separated[0])
    # print('start_epd: ', start_epd)
    # print('start_epoch: ', start_epoch)

    data_day1 = {'available': False}
    stop_epoch_day1 = jalali_string_to_time(days_separated[1])
    if (not meter_kind_approved == None) \
            and (not meter_name_approved == None) \
            and (time_approved == True):

        from .APITB import epochDistanceToCheck, maxBoundaryTSRetry

        if clk_EN == True:
            epochDistanceToCheck = 1  # 1 minutes each query
            maxBoundaryTSRetry = .1  # .1*60 = 6 minutes

        print('maxBoundaryTSRetry, ', epochDistanceToCheck, maxBoundaryTSRetry)

        time_in_data_available_start_day1 = decor_get_nearest_time_epoch(restClient=rest_client,
                                                                     deviceName=meter_name_approved[1],
                                                                     date=start_epoch,
                                                                     # TODO: change it to string time or other functions
                                                                     key_to_ask_for_nearest=meter_name_approved[2],
                                                                     from_epoch=True,
                                                                     epochDistanceToCheckInner=epochDistanceToCheck,
                                                                     maxBoundaryTSRetryInner=maxBoundaryTSRetry)

        time_in_data_available_stop_day1 = decor_get_nearest_time_epoch(restClient=rest_client,
                                                                    deviceName=meter_name_approved[1],
                                                                    date=stop_epoch_day1,
                                                                    # TODO: change it to string time or other functions
                                                                    key_to_ask_for_nearest=meter_name_approved[2],
                                                                    from_epoch=True,
                                                                    epochDistanceToCheckInner=epochDistanceToCheck,
                                                                    maxBoundaryTSRetryInner=maxBoundaryTSRetry)

        if (time_in_data_available_stop_day1 == 0 or time_in_data_available_start_day1 == 0):
            data_day1.update({'available': False})
            if meter_kind == 'water':
                data_day1.update({"telemetry-diff": 'no data'})
                # print(data_end.get())
                data_day1.update({'unit': 'متر مکعب'})
            elif meter_kind == 'electricity':
                data_day1.update(
                    {"telemetry-diff": 'no data'})
                # print(data_end)
                data_day1.update({'unit': 'کیلو وات ساعت'})

        print('here', meter_data_return_dict)
        deviceEntity_day1 = get_device_entity_by_name(restClient=rest_client, deviceName=meter_name_approved[1])

        if (not time_in_data_available_stop_day1 == 0) and (
                not time_in_data_available_start_day1 == 0):  # check if data is available in such epochs
            data_start_day1 = rest_client.get_timeseries(entity_id=deviceEntity_day1, keys=meter_name_approved[2],
                                                     start_ts=time_in_data_available_start_day1 - 1,
                                                     end_ts=time_in_data_available_start_day1 + 1)
            print('lets see the data_start_day1: ', data_start_day1)
            data_start_decode_day1 = float(data_start_day1.get(meter_name_approved[2])[0].get('value'))
            print('lets see the data_start_decode_day1: ', data_start_decode_day1)
            data_end_day1 = rest_client.get_timeseries(entity_id=deviceEntity_day1, keys=meter_name_approved[2],
                                                   start_ts=time_in_data_available_stop_day1 - 1,
                                                   end_ts=time_in_data_available_stop_day1 + 1)
            data_end_decode_day1 = float(data_end_day1.get(meter_name_approved[2])[0].get('value'))
            print('lets see the data_end_decode_day1: ', data_end_decode_day1)
            data_day1.update({'available': True})
            if meter_kind == 'water':
                data_day1.update({"telemetry-diff": round(data_end_decode_day1 - data_start_decode_day1, 3)})
                # print(data_end.get())
                data_day1.update({'unit': 'متر مکعب'})
            elif meter_kind == 'electricity':
                data_day1.update(
                    {"telemetry-diff": round((data_end_decode_day1 - data_start_decode_day1) * meter_name_approved[3], 3)})
                # print(data_end)
                data_day1.update({'unit': 'کیلو وات ساعت'})

    DictData2 = {}
    DictData2.update({'day 1': data_day1})

    for k in range(1 , (len(days_separated) - 1)):
        # start to query
        j = days_separated[k]
        p = k + 1
        next_j = days_separated[k+1]
        data2 = {'available': False}
        # meter_data_return_dict.update({'error-time-start-avlbl': None})
        # meter_data_return_dict.update({'error-time-stop-avlbl': None})
        start_epd = jalali_string_to_time(j)
        stop_epd = jalali_string_to_time(next_j)
        if (not meter_kind_approved == None) \
                and (not meter_name_approved == None) \
                and (time_approved == True):


            from .APITB import epochDistanceToCheck, maxBoundaryTSRetry

            if clk_EN == True:
                epochDistanceToCheck = 1  # 1 minutes each query
                maxBoundaryTSRetry = .1  # .1*60 = 6 minutes

            print('maxBoundaryTSRetry, ', epochDistanceToCheck, maxBoundaryTSRetry)


            time_in_data_available_start2 = decor_get_nearest_time_epoch(restClient=rest_client,
                                                                        deviceName=meter_name_approved[1],
                                                                        date=start_epd,
                                                                        # TODO: change it to string time or other functions
                                                                        key_to_ask_for_nearest=meter_name_approved[2],
                                                                        from_epoch=True,
                                                                        epochDistanceToCheckInner=epochDistanceToCheck,
                                                                        maxBoundaryTSRetryInner=maxBoundaryTSRetry)

            # if time_in_data_available_start == 0:
            #     data2.update({'error-time-start-avlbl': True})

            time_in_data_available_stop2 = decor_get_nearest_time_epoch(restClient=rest_client,
                                                                       deviceName=meter_name_approved[1],
                                                                       date=stop_epd,
                                                                       # TODO: change it to string time or other functions
                                                                       key_to_ask_for_nearest=meter_name_approved[2],
                                                                       from_epoch=True,
                                                                       epochDistanceToCheckInner=epochDistanceToCheck,
                                                                       maxBoundaryTSRetryInner=maxBoundaryTSRetry)

            if (time_in_data_available_stop2 == 0 or time_in_data_available_start2 == 0):
                data2.update({'available': False})
                if meter_kind == 'water':
                    data2.update({"telemetry-diff": 'no data'})
                    # print(data_end.get())
                    data2.update({'unit': 'متر مکعب'})
                elif meter_kind == 'electricity':
                    data2.update(
                        {"telemetry-diff": 'no data'})
                    # print(data_end)
                    data2.update({'unit': 'کیلو وات ساعت'})
                # meter_data_return_dict.update({'error-time-stop-avlbl': True})

            print('here', meter_data_return_dict)
            deviceEntity2 = get_device_entity_by_name(restClient=rest_client, deviceName=meter_name_approved[1])

            if (not time_in_data_available_stop2 == 0) and (
            not time_in_data_available_start2 == 0):  # check if data is available in such epochs
                data_start2 = rest_client.get_timeseries(entity_id=deviceEntity2, keys=meter_name_approved[2],
                                                        start_ts=time_in_data_available_start2 - 1,
                                                        end_ts=time_in_data_available_start2 + 1)
                data_start_decode2 = float(data_start2.get(meter_name_approved[2])[0].get('value'))
                data_end2 = rest_client.get_timeseries(entity_id=deviceEntity2, keys=meter_name_approved[2],
                                                      start_ts=time_in_data_available_stop2 - 1,
                                                      end_ts=time_in_data_available_stop2 + 1)
                data_end_decode2 = float(data_end2.get(meter_name_approved[2])[0].get('value'))

                data2.update({'available': True})
                if meter_kind == 'water':
                    data2.update({"telemetry-diff": round(data_end_decode2 - data_start_decode2, 3)})
                    # print(data_end.get())
                    data2.update({'unit': 'متر مکعب'})
                elif meter_kind == 'electricity':
                    data2.update(
                        {"telemetry-diff": round((data_end_decode2 - data_start_decode2) * meter_name_approved[3], 3)})
                    # print(data_end)
                    data2.update({'unit': 'کیلو وات ساعت'})

        DictData2.update({f'day {p}' : data2})

    if clk_EN == True:
        data_lastday = {'available': False}
        start_epoch_lastday = jalali_string_to_time(days_separated[-1])
        if (not meter_kind_approved == None) \
                and (not meter_name_approved == None) \
                and (time_approved == True):

            from .APITB import epochDistanceToCheck, maxBoundaryTSRetry

            if clk_EN == True:
                epochDistanceToCheck = 1  # 1 minutes each query
                maxBoundaryTSRetry = .1  # .1*60 = 6 minutes

            print('maxBoundaryTSRetry, ', epochDistanceToCheck, maxBoundaryTSRetry)

            time_in_data_available_start_lastday = decor_get_nearest_time_epoch(restClient=rest_client,
                                                                                deviceName=meter_name_approved[1],
                                                                                date=start_epoch_lastday,
                                                                                # TODO: change it to string time or other functions
                                                                                key_to_ask_for_nearest=
                                                                                meter_name_approved[2],
                                                                                from_epoch=True,
                                                                                epochDistanceToCheckInner=epochDistanceToCheck,
                                                                                maxBoundaryTSRetryInner=maxBoundaryTSRetry)

            time_in_data_available_stop_lastday = decor_get_nearest_time_epoch(restClient=rest_client,
                                                                               deviceName=meter_name_approved[1],
                                                                               date=stop_epoch,
                                                                               # TODO: change it to string time or other functions
                                                                               key_to_ask_for_nearest=
                                                                               meter_name_approved[2],
                                                                               from_epoch=True,
                                                                               epochDistanceToCheckInner=epochDistanceToCheck,
                                                                               maxBoundaryTSRetryInner=maxBoundaryTSRetry)

            if (time_in_data_available_stop_lastday == 0 or time_in_data_available_start_lastday == 0):
                data_lastday.update({'available': False})
                if meter_kind == 'water':
                    data_lastday.update({"telemetry-diff": 'no data'})
                    # print(data_end.get())
                    data_lastday.update({'unit': 'متر مکعب'})
                elif meter_kind == 'electricity':
                    data_lastday.update(
                        {"telemetry-diff": 'no data'})
                    # print(data_end)
                    data_lastday.update({'unit': 'کیلو وات ساعت'})
                # meter_data_return_dict.update({'error-time-stop-avlbl': True})

            print('here', meter_data_return_dict)
            deviceEntity_lastday = get_device_entity_by_name(restClient=rest_client, deviceName=meter_name_approved[1])

            if (not time_in_data_available_stop_lastday == 0) and (
                    not time_in_data_available_start_lastday == 0):  # check if data is available in such epochs
                data_start_lastday = rest_client.get_timeseries(entity_id=deviceEntity_lastday,
                                                                keys=meter_name_approved[2],
                                                                start_ts=time_in_data_available_start_lastday - 1,
                                                                end_ts=time_in_data_available_start_lastday + 1)
                data_start_decode_lastday = float(data_start_lastday.get(meter_name_approved[2])[0].get('value'))
                data_end_lastday = rest_client.get_timeseries(entity_id=deviceEntity_lastday,
                                                              keys=meter_name_approved[2],
                                                              start_ts=time_in_data_available_stop_lastday - 1,
                                                              end_ts=time_in_data_available_stop_lastday + 1)
                data_end_decode_lastday = float(data_end_lastday.get(meter_name_approved[2])[0].get('value'))

                data_lastday.update({'available': True})
                if meter_kind == 'water':
                    data_lastday.update(
                        {"telemetry-diff": round(data_end_decode_lastday - data_start_decode_lastday, 3)})
                    # print(data_end.get())
                    data_lastday.update({'unit': 'متر مکعب'})
                elif meter_kind == 'electricity':
                    data_lastday.update(
                        {"telemetry-diff": round(
                            (data_end_decode_lastday - data_start_decode_lastday) * meter_name_approved[3], 3)})
                    # print(data_end)
                    data_lastday.update({'unit': 'کیلو وات ساعت'})
        lastday = len(days_separated)
        DictData2.update({f'day {lastday}': data_lastday})


    meter_data_return_dict.update({'data_daybyday': DictData2})  # TODO: include unit and value to data
    print('here', meter_data_return_dict)

    # sum_of_days= 0
    # for k in DictData2:
    #     sum_of_days += DictData2[k]['telemetry-diff']
    # print('sum_of_days is :',sum_of_days)
    # data.update({'available': True})
    # if meter_kind == 'water':
    #     data.update({"telemetry-diff": sum_of_days})
    #     # print(data_end.get())
    #     data.update({'unit': 'متر مکعب'})
    # elif meter_kind == 'electricity':
    #     data.update(
    #         {"telemetry-diff": sum_of_days})
    #     # print(data_end)
    #     data.update({'unit': 'کیلو وات ساعت'})
    # print(data)
    # meter_data_return_dict.update({'data': data})  # TODO: include unit and value to data
    # meter_data_return_dict.update({'sum_of_days': sum_of_days})
    # print('here', meter_data_return_dict)


    return jsonify(meter_data_return_dict)



@ghabz_bp.post('/get_all_meter_data_API')
def get_all_meter_data_API():
    # gather form data returned from js fetch API
    meter_kind = request.form.get('meterKind')
   # meter_name = request.form.get('meterName')
    start_time = request.form.get('startTime')
    stop_time = request.form.get('endTime')
    clk_EN = request.form.get('clkEN')
    if (str(clk_EN) == 'true'):
        clk_EN = True
    else:
        clk_EN = False
    start_clock = request.form.get('startClock')
    stop_clock = request.form.get('stopClock')
    print(meter_kind, start_time, stop_time, clk_EN, start_clock, stop_clock)

    rest_client = RestClientCE(base_url=base_url)
    rest_client.login(username=username, password=password)

    # get data from DB
    meter_kind_approved= wholeKeeeper.get(meter_kind)
    if meter_kind_approved:
        all_meter_data_return_dict.update({'error-meter-kind': None})
    else:
        # meter_data_return_dict.update({'error-meter-kind': 'این نوع دیوایس وجود ندارد.'})
        all_meter_data_return_dict.update({'error-meter-kind': True})

    all_meter_data_return_dict.update({'error-start-clock': False})
    all_meter_data_return_dict.update({'error-stop-clock': False})
    raisedStartEpoch = 0
    raisedStopEpoch = 0
    if clk_EN == True:
        print("in here to ask clock valid")
        colonOcurrClockStart = str(start_clock).count(':')
        colonOcurrClockStop = str(start_clock).count(':')
        if colonOcurrClockStart == 1:
            startClockList = str(start_clock).split(':')
            try:
                raisedStartEpoch = (int(startClockList[0]) * 60 + int(startClockList[1])) * 60
                print(raisedStartEpoch)
            except:
                all_meter_data_return_dict.update({'error-start-clock': True})
        else:
            all_meter_data_return_dict.update({'error-start-clock': True})

        if colonOcurrClockStop == 1:
            stopClockList = str(stop_clock).split(':')
            try:
                raisedStopEpoch = (int(stopClockList[0]) * 60 + int(stopClockList[1])) * 60
                print(raisedStopEpoch)
            except:
                all_meter_data_return_dict.update({'error-stop-clock': True})
        else:
            all_meter_data_return_dict.update({'error-stop-clock': True})

    # see if the Dates are valid
    start_epoch = jalali_string_to_time(start_time)
    stop_epoch = jalali_string_to_time(stop_time)


    print('start epoch bef:', start_epoch)
    if not start_epoch == None:
        start_epoch = start_epoch + raisedStartEpoch
        if sys.platform.startswith('linux'):
            start_epoch = start_epoch - (3 * 60 + 30) * 60

    if not stop_epoch == None:
        stop_epoch = stop_epoch + raisedStopEpoch
        if sys.platform.startswith('linux'):
            stop_epoch = stop_epoch - (3 * 60 + 30) * 60

    print('start epoch aft:', start_epoch)

    print('epoch:' ,start_epoch)
    all_meter_data_return_dict.update({'error-start-time': None})

    if start_epoch == None:
        # meter_data_return_dict.update({'error-start-time': 'فرمت تاریخ ابتدا صحیح نیست'})
        all_meter_data_return_dict.update({'error-start-time': True})

    all_meter_data_return_dict.update({'error-stop-time': None})
    if stop_epoch == None:
        # meter_data_return_dict.update({'error-stop-time': 'فرمت تاریخ انتها صحیح نیست'})
        all_meter_data_return_dict.update({'error-stop-time': True})

    all_meter_data_return_dict.update({'error-time-seq': None})
    time_approved = False
    if ( not start_epoch == None) and ( not stop_epoch == None):
        if (start_epoch > stop_epoch):
            print(start_epoch, stop_epoch, )
            # meter_data_return_dict.update({'error-time': 'تاریخ ابتدا جلوتر از تاریخ انتها است.'})
            all_meter_data_return_dict.update({'error-time-seq': True})
        else:
            time_approved = True


#changed_updated_form
    meter_name_approved = None
    from .APITB import electricityKeeper, waterKeeper, gasKeeper

    # Function to get the correct keeper dictionary based on meter kind
    # def get_keeper(meter_kind_local):
    #     if meter_kind_local == 'electricity':
    #         return electricityKeeper
    #     elif meter_kind_local == 'water':
    #         return waterKeeper
    #     elif meter_kind_local == 'gas':
    #         return gasKeeper
    #     else:
    #         return None
        # Iterate through each meter kind

    # for meter_kind in ['electricity', 'water', 'gas']:
    #     keeper = get_keeper(meter_kind)
    #     if keeper is None:
    #         continue
    DictData = {}
    for meter_info in wholeKeeeper.get(meter_kind).values():
        print("meter_info:")
        print(meter_info)
        meter_name_approved = meter_info
    # start to query


        data = {'available': False}
        all_meter_data_return_dict.update({'error-time-start-avlbl': None})
        all_meter_data_return_dict.update({'error-time-stop-avlbl': None})

        if (not meter_kind_approved == None) \
                and (not meter_name_approved == None) \
                and (time_approved == True):

            #get nearest data to start epoch
            from .APITB import epochDistanceToCheck, maxBoundaryTSRetry

            if clk_EN == True:
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

            if time_in_data_available_start == 0:
                all_meter_data_return_dict.update({'error-time-start-avlbl': True})

            # get nearest data to stop epoch
            time_in_data_available_stop = decor_get_nearest_time_epoch(restClient=rest_client,
                                                                        deviceName=meter_name_approved[1],
                                                                        date=stop_epoch,  # TODO: change it to string time or other functions
                                                                        key_to_ask_for_nearest=meter_name_approved[2],
                                                                        from_epoch=True,
                                                                        epochDistanceToCheckInner=epochDistanceToCheck,
                                                                        maxBoundaryTSRetryInner=maxBoundaryTSRetry)
            if time_in_data_available_stop == 0:
                all_meter_data_return_dict.update({'error-time-stop-avlbl': True})

            print('here', all_meter_data_return_dict)
            deviceEntity = get_device_entity_by_name(restClient=rest_client, deviceName=meter_name_approved[1])

            if (not time_in_data_available_stop ==0) and (not time_in_data_available_start == 0):  # check if data is available in such epochs
                data_start = rest_client.get_timeseries(entity_id=deviceEntity, keys=meter_name_approved[2],
                                                 start_ts=time_in_data_available_start-1,
                                                       end_ts=time_in_data_available_start +1)
                data_start_decode = float(data_start.get(meter_name_approved[2])[0].get('value'))
                data_end = rest_client.get_timeseries(entity_id=deviceEntity, keys=meter_name_approved[2],
                                                       start_ts=time_in_data_available_stop - 1,
                                                       end_ts=time_in_data_available_stop + 1)
                data_end_decode = float(data_end.get(meter_name_approved[2])[0].get('value'))

                data = {}
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

        DictData.update({meter_name_approved[0]: data}) # TODO: include unit and value to data
        print('here', all_meter_data_return_dict)
    all_meter_data_return_dict.update({'data': DictData})
    return jsonify(all_meter_data_return_dict)
    # return jsonify(DictData)