import os
import jdatetime
from datetime import timedelta

from flask import Blueprint
from flask import render_template,request, jsonify
from .util import jalali_string_to_time
import sys
ghabz_bp = Blueprint('ghabz', __name__, template_folder='templates', static_folder='static', url_prefix='/ghabz')

@ghabz_bp.route('/')
def hello_world():  # put application's code here

    return render_template("Tel_Page.html")

@ghabz_bp.route('/chart')
def chart():

    return render_template("Tel_Page2.html")



@ghabz_bp.route('/isAlive')
def isAlivePage():

    return render_template("Is_Alive.html")

def is_empty_dict(d):
    return d is None or not d  # Check if dictionary is None or empty


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
    start_epoch, start_date_obj = jalali_string_to_time(start_time)
    stop_epoch, stop_date_obj = jalali_string_to_time(stop_time)


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



    if not (start_date_obj is None or stop_date_obj is None):
        start_date = start_date_obj
        stop_date = stop_date_obj
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
        stop_epoch_day1, stop_date_day1 = jalali_string_to_time(days_separated[0])
        if (len(days_separated) > 1):
            stop_epoch_day1, stop_date_day1 = jalali_string_to_time(days_separated[1])
        # if  (len(days_separated) > 2):
        #     stop_epoch_day2, stop_date_day2 = jalali_string_to_time(days_separated[2])
        if (not meter_kind_approved == None) \
                and (not meter_name_approved == None) \
                and (time_approved == True):

            from .APITB import epochDistanceToCheck, maxBoundaryTSRetry

            if clk_EN == True:
                epochDistanceToCheck = 1  # 1 minutes each query
                maxBoundaryTSRetry = .1  # .1*60 = 6 minutes

            print('maxBoundaryTSRetry, ', epochDistanceToCheck, maxBoundaryTSRetry)
            previous_epoch_day1 = start_epoch - 86400000
            time_in_data_available_start_day1 = start_epoch * 1000
            time_in_data_available_stop_day1 = stop_epoch_day1 * 1000
            deviceEntity_day1 = get_device_entity_by_name(restClient=rest_client, deviceName=meter_name_approved[1])

            data_start_day1 = rest_client.get_timeseries(entity_id=deviceEntity_day1, keys=meter_name_approved[2],
                                                         start_ts=(previous_epoch_day1 * 1000),
                                                         end_ts=time_in_data_available_start_day1)
            data_end_day1 = rest_client.get_timeseries(entity_id=deviceEntity_day1, keys=meter_name_approved[2],
                                                       start_ts=time_in_data_available_start_day1,
                                                       end_ts=(time_in_data_available_stop_day1))
            # print('lets see the data_start_day1: ', data_start_day1)
            if is_empty_dict(data_end_day1) or is_empty_dict(data_start_day1):
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
            else:
                data_start_decode_day1 = float(data_start_day1.get(meter_name_approved[2])[0].get('value'))
                data_end_decode_day1 = float(data_end_day1.get(meter_name_approved[2])[0].get('value'))
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
            previous_j = days_separated[k-1]
            j = days_separated[k]
            p = k + 1
            next_j = days_separated[k+1]
            data2 = {'available': False}
            # meter_data_return_dict.update({'error-time-start-avlbl': None})
            # meter_data_return_dict.update({'error-time-stop-avlbl': None})
            pre_start_epd, pre_start_date_epd = jalali_string_to_time(previous_j)
            start_epd,  start_date_epd= jalali_string_to_time(j)
            stop_epd, stop_date_epd = jalali_string_to_time(next_j)
            if (not meter_kind_approved == None) \
                    and (not meter_name_approved == None) \
                    and (time_approved == True):


                from .APITB import epochDistanceToCheck, maxBoundaryTSRetry

                if clk_EN == True:
                    epochDistanceToCheck = 1  # 1 minutes each query
                    maxBoundaryTSRetry = .1  # .1*60 = 6 minutes

                print('maxBoundaryTSRetry, ', epochDistanceToCheck, maxBoundaryTSRetry)


                time_in_data_available_start2 = start_epd * 1000
                time_in_data_available_stop2 = stop_epd * 1000
                deviceEntity2 = get_device_entity_by_name(restClient=rest_client, deviceName=meter_name_approved[1])

                data_start2 = rest_client.get_timeseries(entity_id=deviceEntity2, keys=meter_name_approved[2],
                                                         start_ts=(pre_start_epd * 1000),
                                                         end_ts=time_in_data_available_start2)
                data_end2 = rest_client.get_timeseries(entity_id=deviceEntity2, keys=meter_name_approved[2],
                                                       start_ts=time_in_data_available_start2,
                                                       end_ts=time_in_data_available_stop2)

                if is_empty_dict(data_start2) or is_empty_dict(data_start2):
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
                else:
                    data_start_decode2 = float(data_start2.get(meter_name_approved[2])[0].get('value'))
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
            start_epoch_lastday, start_date_lastday = jalali_string_to_time(days_separated[-1])
            pre_start_epoch_lastday= start_epoch_lastday - 86400000
            if (not meter_kind_approved == None) \
                    and (not meter_name_approved == None) \
                    and (time_approved == True):

                from .APITB import epochDistanceToCheck, maxBoundaryTSRetry

                if clk_EN == True:
                    epochDistanceToCheck = 1  # 1 minutes each query
                    maxBoundaryTSRetry = .1  # .1*60 = 6 minutes

                print('maxBoundaryTSRetry, ', epochDistanceToCheck, maxBoundaryTSRetry)

                time_in_data_available_pre_start_lastday = pre_start_epoch_lastday * 1000
                time_in_data_available_start_lastday = start_epoch_lastday * 1000
                time_in_data_available_stop_lastday = stop_epoch * 1000
                deviceEntity_lastday = get_device_entity_by_name(restClient=rest_client,
                                                                 deviceName=meter_name_approved[1])

                data_start_lastday = rest_client.get_timeseries(entity_id=deviceEntity_lastday,
                                                                keys=meter_name_approved[2],
                                                                start_ts=time_in_data_available_pre_start_lastday,
                                                                end_ts=time_in_data_available_start_lastday)
                data_end_lastday = rest_client.get_timeseries(entity_id=deviceEntity_lastday,
                                                              keys=meter_name_approved[2],
                                                              start_ts=time_in_data_available_start_lastday,
                                                              end_ts=time_in_data_available_stop_lastday)

                if is_empty_dict(data_end_lastday) or is_empty_dict(data_start_lastday):
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
                else:
                    data_start_decode_lastday = float(data_start_lastday.get(meter_name_approved[2])[0].get('value'))
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
    start_epoch, start_date_obj = jalali_string_to_time(start_time)
    stop_epoch, stop_date_obj = jalali_string_to_time(stop_time)
    pre_start_epoch_ms = (start_epoch - 86400000)*1000

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

            time_in_data_available_start = start_epoch * 1000
            if time_in_data_available_start == 0:
                all_meter_data_return_dict.update({'error-time-start-avlbl': True})

            # get nearest data to stop epoch
            time_in_data_available_stop = stop_epoch*1000
            if time_in_data_available_stop == 0:
                all_meter_data_return_dict.update({'error-time-stop-avlbl': True})

            deviceEntity = get_device_entity_by_name(restClient=rest_client, deviceName=meter_name_approved[1])
            data_start = rest_client.get_timeseries(entity_id=deviceEntity, keys=meter_name_approved[2],
                                                    start_ts=pre_start_epoch_ms,
                                                    end_ts=time_in_data_available_start)
            data_end = rest_client.get_timeseries(entity_id=deviceEntity, keys=meter_name_approved[2],
                                                  start_ts=time_in_data_available_start,
                                                  end_ts=time_in_data_available_stop)

            if not (is_empty_dict(data_end) or is_empty_dict(data_start)):  # check if data is available in such epochs
                data_start_decode = float(data_start.get(meter_name_approved[2])[0].get('value'))
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

@ghabz_bp.post('/get_all_charts_data_API')
def get_all_charts_data_API():
    # gathering data for drawing charts of last day, last week and last month usage
    all_charts_data_return_dict = {}
    today_jalali = jdatetime.date.today()
    now_jalali = jdatetime.datetime.now().replace(second=0, microsecond=0, minute=0)
    yesterday_same_time = (now_jalali - timedelta(days=1)).replace(second=0, microsecond=0, minute=0)
    formatted_time = now_jalali.strftime("%H:%M")
    today_date = today_jalali.strftime("%Y-%m-%d")
    one_day_before = (today_jalali - timedelta(days=1)).strftime("%Y-%m-%d")
    one_week_before = (today_jalali - timedelta(days=6)).strftime("%Y-%m-%d")
    one_month_before = (today_jalali - timedelta(days=30)).strftime("%Y-%m-%d")
    # two_day_before = (today_jalali - timedelta(days=2)).strftime("%Y-%m-%d")

    meter_kind = request.form.get('meterKind')
    start_time = [one_day_before,one_week_before,one_month_before]
    stop_time = today_date
    start_clock = formatted_time
    print(meter_kind, start_time[0], start_time[1], start_time[2], stop_time, start_clock)
    # Generate the list of days from one_month_before to now
    start_date = jdatetime.datetime.strptime(one_month_before, '%Y-%m-%d')
    stop_date = jdatetime.datetime.strptime(today_date, '%Y-%m-%d')
    difference_date = (stop_date - start_date).days
    days_counter = difference_date + 1
    print(f"Total number of days including both dates: {days_counter}")
    days_separated = [start_date.strftime('%Y-%m-%d')];

    next_day = start_date
    for i in range(1, days_counter):
        next_day += jdatetime.timedelta(days=1)
        days_separated.append(next_day.strftime('%Y-%m-%d'))

    print("Days separated:", days_separated)
    all_charts_data_return_dict.update({'days_separated': days_separated})  # TODO: include unit and value to data

    fulldaysName = [' شنبه', ' یکشنبه', ' دوشنبه', ' سه شنبه', ' چهارشنبه', ' پنج شنبه', ' جمعه']
    # daysName = [fulldaysName[start_date.weekday()]]
    daysName = []
    for day in days_separated:
        day_date = jdatetime.datetime.strptime(day, '%Y-%m-%d')
        daysName.append(fulldaysName[day_date.weekday()])

    # print("Days name:", daysName)
    all_charts_data_return_dict.update({'daysName': daysName})
    # start_epd = jalali_string_to_time(days_separated[0])
    # print('start_epd: ', start_epd)
    # print('start_epoch: ', start_epoch)

    # Generate the list of hours from yesterday to now
    difference_hours = int((now_jalali - yesterday_same_time).total_seconds() // 3600)
    times_separated = []
    midnight_index = None
    current_time = yesterday_same_time
    for i in range(difference_hours + 1):
        formatted_time = current_time.strftime('%H:%M')
        times_separated.append(formatted_time)
        if formatted_time == '00:00':
            midnight_index = i
        current_time += timedelta(hours=1)

    print("Times separated from yesterday to now: ", times_separated)

    all_charts_data_return_dict.update({'times_separated': times_separated})

    rest_client = RestClientCE(base_url=base_url)
    rest_client.login(username=username, password=password)

    meter_kind_approved = wholeKeeeper.get(meter_kind)
    if meter_kind_approved:
        all_charts_data_return_dict.update({'error-meter-kind': None})
    else:
        # meter_data_return_dict.update({'error-meter-kind': 'این نوع دیوایس وجود ندارد.'})
        all_charts_data_return_dict.update({'error-meter-kind': True})

    all_charts_data_return_dict.update({'error-start-clock': False})
    all_charts_data_return_dict.update({'error-stop-clock': False})
    raisedStartEpoch = 0
    raisedStopEpoch = 0
    startClockList = str(start_clock).split(':')
    try:
        raisedStartEpoch = (int(startClockList[0]) * 60 + int(startClockList[1])) * 60
        raisedStopEpoch = raisedStartEpoch
        print(raisedStartEpoch)
    except:
        all_charts_data_return_dict.update({'error-start-clock': True})
        all_charts_data_return_dict.update({'error-stop-clock': True})

    start_epoch0, start_date_obj = jalali_string_to_time(start_time[0])
    stop_epoch, stop_date_obj = jalali_string_to_time(stop_time)
    print(start_epoch0, stop_epoch)

    all_charts_data_return_dict.update({'error-start-time': None})
    all_charts_data_return_dict.update({'error-stop-time': None})
    all_charts_data_return_dict.update({'error-time-seq': None})

    meter_name_approved = None
    from .APITB import electricityKeeper, waterKeeper, gasKeeper
    DictData_lastday = {}
    DictData_lastmonth = {}
    for meter_info in wholeKeeeper.get(meter_kind).values():
        DictData0 = {}
        DictData1 = {}
        print("meter_info: ")
        print(meter_info)
        meter_name_approved = meter_info

        # start to query
        # data1 = {'available': False}
        # data2 = {'available': False}
        all_charts_data_return_dict.update({'error-time-start-avlbl': None})
        all_charts_data_return_dict.update({'error-time-stop-avlbl': None})

        if (not meter_kind_approved == None) \
                and (not meter_name_approved == None):
            # get nearest data to start epoch
            from .APITB import epochDistanceToCheck, maxBoundaryTSRetry

            epochDistanceToCheck = 1  # 1 minutes each query
            maxBoundaryTSRetry = .1  # .1*60 = 6 minutes
            for k in range(0, (len(times_separated) - 1)):
                # print(k)
                pre_time_obj = jdatetime.datetime.strptime(times_separated[0], "%H:%M")
                previous_j = (pre_time_obj - timedelta(hours=1)).strftime("%H:%M")
                # previous_j = times_separated[k-1]
                j = times_separated[k]
                next_j = times_separated[k + 1]
                p = k + 1
                data0 = {'available': False}
                raisedStartEpoch2 = 0
                raisedStopEpoch2 = 0
                pre_startClockList2 = str(previous_j).split(':')
                try:
                    pre_raisedStartEpoch2 = (int(pre_startClockList2[0]) * 60 + int(pre_startClockList2[1])) * 60
                    # print(raisedStartEpoch2)
                except:
                    all_charts_data_return_dict.update({'error-start-clock': True})

                startClockList2 = str(j).split(':')
                try:
                    raisedStartEpoch2 = (int(startClockList2[0]) * 60 + int(startClockList2[1])) * 60
                    # print(raisedStartEpoch2)
                except:
                    all_charts_data_return_dict.update({'error-start-clock': True})

                stopClockList2 = str(next_j).split(':')
                try:
                    raisedStopEpoch2 = (int(stopClockList2[0]) * 60 + int(stopClockList2[1])) * 60
                    # print(raisedStopEpoch2)
                except:
                    all_charts_data_return_dict.update({'error-stop-clock': True})

                pre_start_epoch_1hour = start_epoch0 + pre_raisedStartEpoch2
                if sys.platform.startswith('linux'):
                    pre_start_epoch_1hour = pre_start_epoch_1hour - (3 * 60 + 30) * 60

                start_epoch_1hour = start_epoch0 + raisedStartEpoch2
                if sys.platform.startswith('linux'):
                    start_epoch_1hour = start_epoch_1hour - (3 * 60 + 30) * 60

                stop_epoch_1hour = start_epoch0 + raisedStopEpoch2
                if sys.platform.startswith('linux'):
                    stop_epoch_1hour = stop_epoch_1hour - (3 * 60 + 30) * 60

                if k  == (midnight_index-1):
                    start_epoch_1hour = start_epoch_1hour
                    if sys.platform.startswith('linux'):
                        start_epoch_1hour = start_epoch_1hour - (3 * 60 + 30) * 60

                    stop_epoch_1hour = stop_epoch_1hour + 86400
                    if sys.platform.startswith('linux'):
                        stop_epoch_1hour = stop_epoch_1hour - (3 * 60 + 30) * 60

                if k  > (midnight_index-1):
                    start_epoch_1hour = start_epoch_1hour + 86400
                    if sys.platform.startswith('linux'):
                        start_epoch_1hour = start_epoch_1hour - (3 * 60 + 30) * 60

                    stop_epoch_1hour = stop_epoch_1hour + 86400
                    if sys.platform.startswith('linux'):
                        stop_epoch_1hour = stop_epoch_1hour - (3 * 60 + 30) * 60


                # print('here is start_epoch_1hour: ',start_epoch_1hour)
                # print('here is stop_epoch_1hour: ', stop_epoch_1hour)

                time_in_data_available_start0 = start_epoch_1hour * 1000
                time_in_data_available_stop0 = stop_epoch_1hour * 1000
                # print('here is time_in_data_available_start0: ', time_in_data_available_start0)
                # print('here is time_in_data_available_stop0: ', time_in_data_available_stop0)

                deviceEntity0 = get_device_entity_by_name(restClient=rest_client, deviceName=meter_name_approved[1])

                data_start0 = rest_client.get_timeseries(entity_id=deviceEntity0, keys=meter_name_approved[2],
                                                         start_ts=(pre_start_epoch_1hour * 1000),
                                                         end_ts=time_in_data_available_start0)
                # print(data_start0)
                data_end0 = rest_client.get_timeseries(entity_id=deviceEntity0, keys=meter_name_approved[2],
                                                       start_ts=time_in_data_available_start0,
                                                       end_ts=time_in_data_available_stop0)
                # print(data_end0)
                if is_empty_dict(data_end0) or is_empty_dict(data_start0):
                    data0.update({'available': False})
                    if meter_kind == 'water':
                        data0.update({"telemetry-diff": 'no data'})
                        # print(data_end.get())
                        data0.update({'unit': 'متر مکعب'})
                    elif meter_kind == 'electricity':
                        data0.update(
                            {"telemetry-diff": 'no data'})
                        # print(data_end)
                        data0.update({'unit': 'کیلو وات ساعت'})
                else:
                    data_start_decode0 = float(data_start0.get(meter_name_approved[2])[0].get('value'))
                    data_end_decode0 = float(data_end0.get(meter_name_approved[2])[0].get('value'))

                    data0.update({'available': True})
                    if meter_kind == 'water':
                        data0.update({"telemetry-diff": round(data_end_decode0 - data_start_decode0, 3)})
                        # print(data_end.get())
                        data0.update({'unit': 'متر مکعب'})
                    elif meter_kind == 'electricity':
                        data0.update(
                            {"telemetry-diff": round((data_end_decode0 - data_start_decode0) * meter_name_approved[3],3)})
                        # print(data_end)
                        data0.update({'unit': 'کیلو وات ساعت'})
                DictData0.update({f'hour {p}': data0})
            DictData_lastday.update({meter_name_approved[0] :DictData0})
            for k in range(0, (len(days_separated) - 1)):
                # start to query
                pre_date_obj = jdatetime.datetime.strptime(days_separated[k], "%Y-%m-%d").date()
                pre_start_date = pre_date_obj - timedelta(days=1)
                previous_j = pre_start_date.strftime("%Y-%m-%d")
                j = days_separated[k]
                p = k + 1
                next_j = days_separated[k + 1]
                data1 = {'available': False}
                # meter_data_return_dict.update({'error-time-start-avlbl': None})
                # meter_data_return_dict.update({'error-time-stop-avlbl': None})

                pre_start_epd, pre_start_epd_obj = jalali_string_to_time(previous_j)
                start_epd, start_epd_obj = jalali_string_to_time(j)
                stop_epd, stop_epd_obj = jalali_string_to_time(next_j)

                time_in_data_available_pre_start1 = pre_start_epd * 1000
                time_in_data_available_start1 = start_epd * 1000
                time_in_data_available_stop1 = stop_epd * 1000

                deviceEntity1 = get_device_entity_by_name(restClient=rest_client, deviceName=meter_name_approved[1])
                data_start1 = rest_client.get_timeseries(entity_id=deviceEntity1, keys=meter_name_approved[2],
                                                         start_ts=time_in_data_available_pre_start1,
                                                         end_ts=time_in_data_available_start1)
                data_end1 = rest_client.get_timeseries(entity_id=deviceEntity1, keys=meter_name_approved[2],
                                                       start_ts=time_in_data_available_start1,
                                                       end_ts=time_in_data_available_stop1)

                if is_empty_dict(data_end1) or is_empty_dict(data_start1):
                    data1.update({'available': False})
                    if meter_kind == 'water':
                        data1.update({"telemetry-diff": 'no data'})
                        # print(data_end.get())
                        data1.update({'unit': 'متر مکعب'})
                    elif meter_kind == 'electricity':
                        data1.update(
                            {"telemetry-diff": 'no data'})
                        # print(data_end)
                        data1.update({'unit': 'کیلو وات ساعت'})
                    # meter_data_return_dict.update({'error-time-stop-avlbl': True})

                else:
                    data_start_decode1 = float(data_start1.get(meter_name_approved[2])[0].get('value'))
                    data_end_decode1 = float(data_end1.get(meter_name_approved[2])[0].get('value'))
                    data1.update({'available': True})
                    if meter_kind == 'water':
                        data1.update({"telemetry-diff": round(data_end_decode1 - data_start_decode1, 3)})
                        # print(data_end.get())
                        data1.update({'unit': 'متر مکعب'})
                    elif meter_kind == 'electricity':
                        data1.update(
                            {"telemetry-diff": round((data_end_decode1 - data_start_decode1) * meter_name_approved[3],
                                                     3)})
                        # print(data_end)
                        data1.update({'unit': 'کیلو وات ساعت'})

                DictData1.update({f'day {p}': data1})
            DictData_lastmonth.update({meter_name_approved[0] : DictData1})


    all_charts_data_return_dict.update({'data_daybyday': DictData_lastmonth})  # TODO: include unit and value to data
    # print('here', all_charts_data_return_dict)

    print('here is DictData_lastday: ', DictData_lastday)
    all_charts_data_return_dict.update({'data_hourbyhour': DictData_lastday})  # TODO: include unit and value to data
    print('here', all_charts_data_return_dict)



    return jsonify(all_charts_data_return_dict)



@ghabz_bp.post('/get_all_isAlive_data_API')
def get_all_isAlive_data_API():
    all_isAlive_data_return_dict = {}
    meter_kind = request.form.get('meterKind')
    print(meter_kind)

    rest_client = RestClientCE(base_url=base_url)
    rest_client.login(username=username, password=password)

    meter_kind_approved = wholeKeeeper.get(meter_kind)
    if meter_kind_approved:
        all_isAlive_data_return_dict.update({'error-meter-kind': None})
    else:
        # meter_data_return_dict.update({'error-meter-kind': 'این نوع دیوایس وجود ندارد.'})
        all_isAlive_data_return_dict.update({'error-meter-kind': True})

    meter_name_approved = None
    from .APITB import electricityKeeper, waterKeeper, gasKeeper, get_device_alive
    DictData_isAlive = {}
    for meter_info in wholeKeeeper.get(meter_kind).values():
        print("meter_info: ", meter_info)
        meter_name_approved = meter_info

        if (not meter_kind_approved == None) \
                and (not meter_name_approved == None):

            # see if the device is alive
            isAlive = False

            DictData_isAlive.update({meter_name_approved[0] : isAlive})
            if meter_name_approved:
                print(meter_name_approved[1])
                isAlive = get_device_alive(restClient=rest_client, deviceName=meter_name_approved[1])
                DictData_isAlive.update({meter_name_approved[0] :isAlive})
                # print('checking is alive', meter_data_return_dict)

        all_isAlive_data_return_dict.update({'isAlive': DictData_isAlive})

    return jsonify(all_isAlive_data_return_dict)

