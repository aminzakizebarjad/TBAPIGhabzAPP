from app import app
import os
import pandas as pd
import numpy as np
import re
from flask import render_template,request, jsonify
import sys
from flask import Flask, send_from_directory, Blueprint
import subprocess
import json
import logging
import jdatetime
from datetime import timedelta
from datetime import datetime

from .APITB import wholeKeeeper,  base_url, username, password, RestClientCE, decor_get_nearest_time_epoch, get_device_entity_by_name
from .util import list_files_without_extension, file_exists
from .util import jalali_string_to_time

# Important note: 
# Change the way data is handled so that the real data is achieved form the server not form a csv file
# Prediction not working and I dont now why exactly
# The last data in each meter is the Meterage of the building if it is -1 do not use it
local_electricityKeeper = {'01_Library':['کتابخانه', 'LIBRARY', 'M_P_0_0', 300, 7500],\
                     '03_Farabi':['فارابی', 'FARABI', 'M_P_0_0', 200, 7000],\
                     '04_Sports_Complex':['مجموعه ورزشی', 'SPORT_COMPLEX', 'M_P_0_0', 200, 8500], \
                     '05_Apa_TarbiatBadany': ['آپا و تربیت بدنی', 'AmirKabir_Meter_G3', 'D1f0', 120, 387],\
                     '06_Civil_Eng_1':['عمران 1', 'AmirKabir_Meter_G4', 'D1f0', 120, 4660],\
                     '07_Civil_Eng_2':['عمران 2', 'AmirKabir_Meter_G4', 'D1f10', 120, 5200],\
                     '08_Aerospace':['هوافضا', 'AmirKabir_Meter_G1', 'D1f10', 200, 4850],\
                     '09_Mathematics':['ریاضی', 'AmirKabir_Meter_G1', 'D1f0', 120, 8114],\
                     '10_Textile_Eng_Transformer1':['نساجی ترانس 1', 'NASAJI', 'M_P_0_0', 500, -1],\
                     '11_Copmuter_Eng_2':['کامپیوتر 2', 'NASAJI', 'M_P_1_0', 120, -1],\
                     '12_Computer_Eng_1':['کامپیوتر 1', 'NASAJI', 'M_P_2_0', 240, -1],\
                     '13_Behdari':['بهداری', 'AmirKabir_Meter_G2', 'D1f0', 120, 2308],\
                     '14_Chemical_Eng':['مهندسی شیمی', 'AmirKabir_Meter_G1', 'D1f20', 120, 4347],\
                     '15_Polymer':['مهندسی پلیمر', 'AmirKabir_Meter_G1', 'D1f30', 200, 6280],\
                     '16_Metallurgy':['متالورژی', 'AmirKabir_Meter_G4', 'D1f40', 120, 4022],\
                     '17_Informatic':['انفورماتیک', 'AmirKabir_Meter_G3', 'D1f30', 120, 1760],\
                     '18_Mineral_Eng':['معدن', 'AmirKabir_Meter_G4', 'D1f30', 200, 7450],\
                     '19_Installations_Dorms':['تاسیسات و امور خوابگاه', 'AmirKabir_Meter_G3', 'D1f10', 120, -1],\
                     '20_Maritime_Eng':['کشتی سازی', 'AmirKabir_Meter_G4', 'D1f20', 120, 1260],\
                     '21_Aboreyhan_Pump':['موتورخانه ابوریحان', 'NASAJI', 'M_P_3_0', 400, -1], \
                     '22_Pump_Station': ['پمپ استیشن', 'NASAJI', 'M_P_4_0', 200, -1],\
                     '23_Aboreyhan_1':['ابوریحان 1','ABOREIHAN_1', 'M_P_0_0', 500, -1],\
                     '24_Aboreyhan_2':['ابوریحان 2','ABOREIHAN_1', 'M_P_1_0', 500, -1],\
                     '25_Aboreyhan_3':['ابوریحان 3','ABOREIHAN_2', 'M_P_0_0', 500, -1],\
                     '26_Raftari_Dorm':['خوابگاه رفتاری','ABOREIHAN_2', 'M_P_1_0', 400, -1],\
                     '27_Industrial_Eng_1': ['صنایع 1', 'ELECTRICITY_INDUSTRIAL_ENG', 'M_P_0_0', 400, -1],\
                     '28_Industrial_Eng_2': ['صنایع 2', 'ELECTRICITY_INDUSTRIAL_ENG', 'M_P_1_0', 200, -1],\
                     'biomedic':['مهندسی پزشکی', 'ELECTRICITY_BIOMEDICAL_ENG_1', 'M_P_0_0', 200, 13000],\
                     '30_Pump_BioMedical':['مهندسی پزشکی موتورخانه', 'ELECTRICITY_BIOMEDIACL_ENG_3', 'M_P_0_0', 160, -1],\
                     '31_Management_IndependentChem':['مدیریت-شیمی مستقل', 'ELECTRICITY_CHEM_INDEPENDENT', 'M_P_0_0', 200, -1],\
                     '32_FanavariBuilding1_EbnSina':['ابن سینا', 'ELECTRICITY_BIOMEDICAL_ENG_2', 'M_P_0_0', 200, 8500],\
                     '33_Nahad':['نهاد رهبری','ELECTRICITY_NAHAD', 'M_P_0_0', 60, 1434], \
                     'ghalamchi': ['خوابگاه قلمچی', 'AmirKabir_Meter_G1', 'D2f20', 60, -1]
                     }

@app.route('/meters', methods=['GET'])
def get_meters():
    
    # Construct address of the dataset
    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(current_dir,'..' ,'dataset_cleaned_Nima') 

    all_meters = list_files_without_extension(full_path)
    meters = []
    for meter in all_meters:
        meters.append({'id':meter, 'name':format_name(meter)}) # id of the meter plus the name to show

    return jsonify(meters)

@app.route('/api/meter_data', methods=['GET'])
def meter_data():
    meter = request.args.get('meter')
    period = request.args.get('period')
    
    # Construct address of the dataset
    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(current_dir, '..' ,'dataset_cleaned_Nima', f'{meter}.csv')
    
    print(full_path)
    
    if file_exists(full_path):
        df = pd.read_csv(full_path)
        
        # Get the specified number of recent records
        recent_data = df.iloc[-int(period):]  # Select the last 'period' rows
        
        # Construct a list of dictionaries with 'datetime' and 'daily_value'
        results = []
        for index, row in recent_data.iterrows():
            results.append({
                'datetime': row['datetime'],
                'daily_value': row['daily_value']
            })
        
        return jsonify(results)  # Return the list of dictionaries as JSON
    
    return jsonify({'error': 'Invalid meter or period'}), 400

# @app.route('/api/make_prediction', methods=['POST'])
# def make_prediction():
#     # Here you would implement the logic for making predictions
#     # For now, we'll return a dummy response
#     meter = request.args.get('meter')
#     print(f'\nMeter to predict for:{meter}\n')    
    
#     # Construct address of the dataset
#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     full_path = os.path.join(current_dir, '..' ,'dataset_cleaned_Nima', f'{meter}.csv')

#     if file_exists(full_path):
#         # Mock the prediction
#         prediction = [np.random.rand()*2.0 +1.0 for _ in range(30)]
#         return jsonify({'prediction': prediction})
#     return jsonify({'error': 'Invalid meter'}), 400

@app.route('/api/make_prediction', methods=['POST'])
def make_prediction():
    meter = request.args.get('meter')
    print(f'\nMeter to predict for:{meter}\n')    
    
    # Construct address of the dataset
    current_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(current_dir, '..','..' ,'run.py')
    
    os.environ['PHASE'] = 'test' 
    os.environ['buldingname'] = meter
    
    try:
        print(f"Running script at path: {script_path}") 
        subprocess.run([sys.executable, script_path], check=True)
        print("\nEnded running the script")

        jsonresults = os.path.join(current_dir, '..','..', 'Results', f'{meter}',f'{meter}.json')

        with open(jsonresults, 'r') as f:
            predictions = json.load(f)
            # predictions = [prediction/1000 for prediction in predictions]
            print(f"\nPredicted values are:\n{predictions}\n{type(predictions)}\n")############
            return jsonify({'prediction': predictions})

    except:
        return jsonify({'error': 'Invalid meter'}), 400


@app.route('/api/all_meters_data', methods=['GET'])
def all_meters_data():
    time_required = request.args.get('time_required')

    # Fetch meter data
    if time_required == 'Meterage':
        print('Meterage')
        meters_data = fetch_all_meters_data_Meterage()  #  'name': meter_name, 'one_week': diff_one_week, 'one_month': diff_one_month
    else:
        print('No Meterage')
        meters_data = fetch_all_meters_data()

    # print('\n\n\n\n')
    # print(100 * 'ABV')
    # print(len(meters_data))
    # print('\n\n\n\n')

    result = []
    # for a in meters_dict.items():
    for data in meters_data:
        
        # meter_name = format_name(data['name'])
        result.append({
            'meter_name': data['name'],
            'one_week': data['one_week'],
            'one_month': data['one_month']
        })

    print('\n\n\n\n')
    print('78'*100)
    print(result)
    print('\n\n\n\n')

    return jsonify(result)


def fetch_all_meters_data():
    from .APITB import epochDistanceToCheck, maxBoundaryTSRetry

    meter_kind = 'electricity'
    meter_names = local_electricityKeeper.keys()

    stop_time = datetime.now()
    stop_time = change_time_to_epoch(stop_time.strftime("%Y-%m-%d %H:%M:%S"))
    one_day_ago = stop_time - (1 * 24 * 60 * 60) # one day ago
    one_week_ago = stop_time - (7 * 24 * 60 * 60) # one week ago
    one_month_ago = stop_time - (30 * 24 * 60 * 60) # one week ago
    
    rest_client = RestClientCE(base_url=base_url)
    rest_client.login(username=username, password=password)
    
    week_list = []
    month_list = []
    results = []
    for meter_name in meter_names:
        # Get meter data 
        meter_name_approved = local_electricityKeeper[meter_name]

        # start to query
        data = {'available': False}

        #get nearest data to start epoch
        time_in_data_available_start = one_week_ago * 1000

        # get nearest data to stop epoch
        time_in_data_available_stop = stop_time * 1000

        deviceEntity = get_device_entity_by_name(restClient=rest_client, deviceName=meter_name_approved[1])

        one_week_data = rest_client.get_timeseries(entity_id=deviceEntity, keys=meter_name_approved[2],
                                                start_ts = one_week_ago * 1000 ,
                                                end_ts = stop_time * 1000 ,
                                                interval = 24 * 60 * 60 * 1000,
                                                agg = 'MAX',
                                                use_strict_data_types= True)

        one_month_data = rest_client.get_timeseries(entity_id=deviceEntity, keys=meter_name_approved[2],
                                            start_ts = one_month_ago * 1000 ,
                                            end_ts = stop_time * 1000,
                                            interval = 24 * 60 * 60 * 1000,
                                            agg = 'MAX',
                                            use_strict_data_types= True)

        try:
            if len(one_week_data) > 0 and len(one_month_data) > 0 :
                # print('GEGE')
                diff_one_week = (one_week_data.get(meter_name_approved[2])[-1]['value'] - one_week_data.get(meter_name_approved[2])[0]['value']) * meter_name_approved[3]        
                diff_one_month = (one_month_data.get(meter_name_approved[2])[-1]['value'] - one_month_data.get(meter_name_approved[2])[0]['value']) * meter_name_approved[3]

                week_list.append(diff_one_week)
                month_list.append(diff_one_month)
                
                # These two 
                if meter_name != '07_Civil_Eng_2' and meter_name != '08_Aerospace':
                    results.append({
                        'name': meter_name_approved[0],  # Use file name (without extension) as meter name
                        'one_week': diff_one_week,
                        'one_month': diff_one_month
                    })
        except:
            pass
    return results  # Return the list of dictionaries


def fetch_all_meters_data_Meterage():
    from .APITB import epochDistanceToCheck, maxBoundaryTSRetry

    meter_kind = 'electricity'
    meter_names = local_electricityKeeper.keys()

    stop_time = datetime.now()
    stop_time = change_time_to_epoch(stop_time.strftime("%Y-%m-%d %H:%M:%S"))
    one_day_ago = stop_time - (1 * 24 * 60 * 60) # one day ago
    one_week_ago = stop_time - (7 * 24 * 60 * 60) # one week ago
    one_month_ago = stop_time - (30 * 24 * 60 * 60) # one week ago
    
    rest_client = RestClientCE(base_url=base_url)
    rest_client.login(username=username, password=password)
    
    week_list = []
    month_list = []
    results = []
    for meter_name in meter_names:
        # Get meter data 
        meter_name_approved = local_electricityKeeper[meter_name]

        # start to query
        data = {'available': False}

        #get nearest data to start epoch
        time_in_data_available_start = one_week_ago * 1000

        # get nearest data to stop epoch
        time_in_data_available_stop = stop_time * 1000

        deviceEntity = get_device_entity_by_name(restClient=rest_client, deviceName=meter_name_approved[1])

        one_week_data = rest_client.get_timeseries(entity_id=deviceEntity, keys=meter_name_approved[2],
                                                start_ts = one_week_ago * 1000 ,
                                                end_ts = stop_time * 1000 ,
                                                interval = 24 * 60 * 60 * 1000,
                                                agg = 'MAX',
                                                use_strict_data_types= True)

        one_month_data = rest_client.get_timeseries(entity_id=deviceEntity, keys=meter_name_approved[2],
                                            start_ts = one_month_ago * 1000 ,
                                            end_ts = stop_time * 1000,
                                            interval = 24 * 60 * 60 * 1000,
                                            agg = 'MAX',
                                            use_strict_data_types= True)

        try:
            if len(one_week_data) > 0 and len(one_month_data) > 0 :
                # print('GEGE')
                diff_one_week = (one_week_data.get(meter_name_approved[2])[-1]['value'] - one_week_data.get(meter_name_approved[2])[0]['value']) * meter_name_approved[3]        
                diff_one_month = (one_month_data.get(meter_name_approved[2])[-1]['value'] - one_month_data.get(meter_name_approved[2])[0]['value']) * meter_name_approved[3]

                week_list.append(diff_one_week)
                month_list.append(diff_one_month)
                
                # These two 
                if meter_name != '07_Civil_Eng_2' and meter_name != '08_Aerospace':
                    if meter_name_approved[4] != -1:
                        results.append({
                            'name': meter_name_approved[0],  # Use file name (without extension) as meter name
                            'one_week': diff_one_week / meter_name_approved[4],
                            'one_month': diff_one_month / meter_name_approved[4]
                        })
        except:
            pass
    return results  # Return the list of dictionaries
            

def calculate_peak_hours(daily_values, datetime):
    # Create an array to hold hourly consumption
    hourly_consumption = np.zeros(24)

    # Assuming daily_values is a list of daily total consumption values
    # and datetime is a list of corresponding datetime strings.
    for daily_value, dt in zip(daily_values, datetime):
        # Here we assume daily_value is distributed evenly across 24 hours
        # Adjust this logic based on your actual data and requirements
        hourly_average = daily_value / 24  # Average per hour
        hour_of_day = int(dt.split(" ")[1].split(":")[0])  # Extract hour from datetime

        # Distribute the daily value into hourly consumption
        hourly_consumption[hour_of_day] += hourly_average

    # Find the peak hours
    peak_hours = np.argsort(hourly_consumption)[-3:]  # Get the top 3 peak hours
    peak_hours_sorted = sorted(peak_hours)  # Sort to return in chronological order

    return [f"{hour}:00" for hour in peak_hours_sorted]  # Return formatted hour strings

def format_name(name):
    # Remove leading digits and underscore
    formatted_name = re.sub(r'^\d+_', '', name)
    
    # Replace underscores with spaces
    formatted_name = formatted_name.replace('_', ' ')
    
    # Capitalize the first letter of each word
    formatted_name = ' '.join(word.capitalize() for word in formatted_name.split())
    
    return formatted_name


###################

'''

a
a
a
asaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

aasaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa



aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
'''

# TODO: Complete this code
@app.route('/api/train_model', methods=['POST'])
def train_model():
    meter = request.args.get('meter')
    print(f'\nMeter to train model on:{meter}\n')    
    
    # Construct address of the dataset
    current_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(current_dir, '..','..' ,'run.py')
    
    os.environ['PHASE'] = 'train' 
    os.environ['buldingname'] = meter
    
    try:
        print(f"Running script at path: {script_path}") 
        subprocess.run([sys.executable, script_path], check=True)
        print("\nEnded running the script")

        jsonresults = os.path.join(current_dir, '..','..', 'Results', f'{meter}',f'{meter}.json')

        with open(jsonresults, 'r') as f:
            predictions = json.load(f)
            predictions = [prediction/1000 for prediction in predictions]
            print(f"\nPredicted values are:\n{predictions}\n{type(predictions)}\n")############
            return jsonify({'prediction': predictions})

    except:
        return jsonify({'error': 'Invalid meter'}), 400


def is_empty_dict(d):
    return d is None or not d  # Check if dictionary is None or empty

def change_time_to_epoch(time_str="2024-11-10 14:30:00", time_format="%Y-%m-%d %H:%M:%S"):
    dt_object = datetime.strptime(time_str, time_format)
    epoch_time = int(dt_object.timestamp()) # in seconds
    return epoch_time

# This one works perfectly and sends realtime data to the front-end
# TODO: Add a functionality that Looks for the last available data for each meter!
@app.route('/api/get_meter_data_realtime')
def get_meter_data_realtime():
    from .APITB import epochDistanceToCheck, maxBoundaryTSRetry

    meter_kind = 'electricity'
    meter_name = request.args.get('meter')
    period = request.args.get('period')

    stop_time = datetime.now()
    stop_time = change_time_to_epoch(stop_time.strftime("%Y-%m-%d %H:%M:%S"))
    start_time = stop_time - (int(period) * 60 * 60) # period is in hours
    
    start_epoch = start_time
    stop_epoch = stop_time
    # print(meter_kind, start_time, stop_time)

    rest_client = RestClientCE(base_url=base_url)
    rest_client.login(username=username, password=password)

    # get data from DB
    raisedStartEpoch = 0
    raisedStopEpoch = 0

    # print('start epoch bef:', start_epoch)
    if not start_epoch == None:
        start_epoch = start_epoch + raisedStartEpoch
        if sys.platform.startswith('linux'):
            start_epoch = start_epoch - (3 * 60 + 30) * 60

    if not stop_epoch == None:
        stop_epoch = stop_epoch + raisedStopEpoch
        if sys.platform.startswith('linux'):
            stop_epoch = stop_epoch - (3 * 60 + 30) * 60

    # print('start epoch aft:', start_epoch)

    all_meter_data_return_dict = {}
    all_meter_data_return_dict.update({'error-time-seq': None})
    time_approved = False
    if ( not start_epoch == None) and ( not stop_epoch == None):
        pre_start_epoch_ms = (start_epoch - maxBoundaryTSRetry * 60 * 60) * 1000
        if (start_epoch > stop_epoch):
            # print(start_epoch, stop_epoch, )
            # meter_data_return_dict.update({'error-time': 'تاریخ ابتدا جلوتر از تاریخ انتها است.'})
            all_meter_data_return_dict.update({'error-time-seq': True})
        else:
            time_approved = True

    # print('time_approved',time_approved)
    
    #changed_updated_form
    meter_name_approved = None

    # Get meter data 
    meter_name_approved = local_electricityKeeper[meter_name]
    # print("meter_name_approved:")
    # print(meter_name_approved)
    
    # start to query
    data = {'available': False}

    #get nearest data to start epoch
    time_in_data_available_start = start_epoch * 1000

    # get nearest data to stop epoch
    time_in_data_available_stop = stop_epoch*1000

    deviceEntity = get_device_entity_by_name(restClient=rest_client, deviceName=meter_name_approved[1])



    data_start = rest_client.get_timeseries(entity_id=deviceEntity, keys=meter_name_approved[2],
                                            start_ts = (start_time - 1 * 60 * 60) * 1000 ,
                                            end_ts = (stop_time -1 * 60 * 60) * 1000,
                                            interval = 3600 * 1000,
                                            agg = 'MAX',
                                            use_strict_data_types= True)

    data_end = rest_client.get_timeseries(entity_id=deviceEntity, keys=meter_name_approved[2],
                                        start_ts = start_time * 1000 ,
                                        end_ts = stop_time * 1000,
                                        interval = 3600 * 1000,
                                        agg = 'MAX',
                                        use_strict_data_types= True)
    results = []
    try:
        for i in range(int(period)):
            results.append({
                'datetime': datetime.fromtimestamp(data_end.get(meter_name_approved[2])[i]['ts']/1000),
                'daily_value': (data_end.get(meter_name_approved[2])[i]['value'] - data_start.get(meter_name_approved[2])[i]['value']) * meter_name_approved[3]
            })
        # print(f"\n\n\n\n\n HEHE \n {results} \n\n\n\n")
        # df = pd.DataFrame(data_start.get(meter_name_approved[2]))
        # df['datetime'] = pd.to_datetime(df['ts'], unit='ms')
        # df = df.rename(columns={'ts': 'epoch_time'})
        # df = df[['datetime', 'epoch_time', 'value']]
        return jsonify(results)
    except:
         return jsonify({'error': 'Invalid meter'}), 400


@app.route('/api/get_30_days')
def get_30_days():
    from .APITB import epochDistanceToCheck, maxBoundaryTSRetry

    meter_kind = 'electricity'
    meter_name = request.args.get('meter')
    one_day_in_seconds = 1 * 24 * 60 * 60

    stop_time = datetime.now()
    stop_time = change_time_to_epoch(stop_time.strftime("%Y-%m-%d %H:%M:%S")) # in seconds
    start_time = stop_time - (30 * 24 * 60 * 60) # Now time - 30 days = 30 days before in seconds
    
    start_epoch = start_time
    stop_epoch = stop_time
    # print(meter_kind, start_time, stop_time)

    rest_client = RestClientCE(base_url=base_url)
    rest_client.login(username=username, password=password)

    # get data from DB
    raisedStartEpoch = 0
    raisedStopEpoch = 0

    # print('start epoch bef:', start_epoch)
    if not start_epoch == None:
        start_epoch = start_epoch + raisedStartEpoch
        if sys.platform.startswith('linux'):
            start_epoch = start_epoch - (3 * 60 + 30) * 60

    if not stop_epoch == None:
        stop_epoch = stop_epoch + raisedStopEpoch
        if sys.platform.startswith('linux'):
            stop_epoch = stop_epoch - (3 * 60 + 30) * 60

    # print('start epoch aft:', start_epoch)

    all_meter_data_return_dict = {}
    all_meter_data_return_dict.update({'error-time-seq': None})
    time_approved = False
    if ( not start_epoch == None) and ( not stop_epoch == None):
        pre_start_epoch_ms = (start_epoch - maxBoundaryTSRetry * 60 * 60) * 1000
        if (start_epoch > stop_epoch):
            all_meter_data_return_dict.update({'error-time-seq': True})
        else:
            time_approved = True

    #changed_updated_form
    meter_name_approved = None

    # Get meter data 
    meter_name_approved = local_electricityKeeper[meter_name]

    # start to query
    data = {'available': False}

    #get nearest data to start epoch
    time_in_data_available_start = start_epoch * 1000

    # get nearest data to stop epoch
    time_in_data_available_stop = stop_epoch*1000

    deviceEntity = get_device_entity_by_name(restClient=rest_client, deviceName=meter_name_approved[1])



    data_start = rest_client.get_timeseries(entity_id=deviceEntity, keys=meter_name_approved[2],
                                            start_ts = (start_time - 1 * 24 * 60 * 60) * 1000 ,
                                            end_ts = (stop_time -1 * 24 * 60 * 60) * 1000,
                                            interval = one_day_in_seconds * 1000,
                                            agg = 'MAX',
                                            use_strict_data_types= True)

    data_end = rest_client.get_timeseries(entity_id=deviceEntity, keys=meter_name_approved[2],
                                        start_ts = start_time * 1000 ,
                                        end_ts = stop_time * 1000,
                                        interval = one_day_in_seconds * 1000,
                                        agg = 'MAX',
                                        use_strict_data_types= True)
    results = []
    # try:
    for i in range(int(30)):
        results.append({
            'datetime': datetime.fromtimestamp(data_end.get(meter_name_approved[2])[i]['ts']/1000),
            'daily_value': data_end.get(meter_name_approved[2])[i]['value'] - data_start.get(meter_name_approved[2])[i]['value']
        })
    print(f"\n\n\n\n\n HEHE \n {results} \n\n\n\n")
    return jsonify(results)
    # except:
    #      return jsonify({'error': 'Invalid meter'}), 400



























############################################################################################################
################################################## TESTS ###################################################
############################################################################################################

# The new get data Inshalah works! 
# Just for test purposes to get data from a time to a time
@app.route('/AI_Elec_Get')
def AI_Elec_Get():
    # gather form data returned from js fetch API
    # meter_kind = request.args.get('meterKind')
    # start_time = request.args.get('startTime')
    # stop_time = request.args.get('endTime')
    # meter_name = request.args.get('meter_name')
    meter_kind = 'electricity'
    meter_name = request.args.get('meter')
    period = request.args.get('period')

    # print("\n\n\n\n\n\n",period,'\n\n\n\n\n\n')
    # construct start and end time
    stop_time = datetime.now()
    stop_time = change_time_to_epoch(stop_time.strftime("%Y-%m-%d %H:%M:%S"))
    start_time = stop_time - (int(period) * 60 * 60 * 1000) # period is in hours
    
    print(f"\n\n StartTime: {start_time} ,  Stop Time: {stop_time}")
    # # get current time and store it as stop_time
    # start_time = "2024-11-8 14:38:00"
    # start_time = change_time_to_epoch(start_time) # TODO: Change if needed #################################3
    # stop_time =  datetime.now()  
    # stop_time = change_time_to_epoch(stop_time.strftime("%Y-%m-%d %H:%M:%S"))

    # useless epochtimes
    start_epoch = start_time 
    stop_epoch = stop_time

    print(meter_kind, start_time, stop_time)

    rest_client = RestClientCE(base_url=base_url)
    rest_client.login(username=username, password=password)

    # get data from DB
    raisedStartEpoch = 0
    raisedStopEpoch = 0
    
    from .APITB import epochDistanceToCheck, maxBoundaryTSRetry


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

    all_meter_data_return_dict = {}
    all_meter_data_return_dict.update({'error-time-seq': None})
    time_approved = False
    if ( not start_epoch == None) and ( not stop_epoch == None):
        pre_start_epoch_ms = (start_epoch - maxBoundaryTSRetry * 60 * 60) * 1000
        if (start_epoch > stop_epoch):
            print(start_epoch, stop_epoch, )
            # meter_data_return_dict.update({'error-time': 'تاریخ ابتدا جلوتر از تاریخ انتها است.'})
            all_meter_data_return_dict.update({'error-time-seq': True})
        else:
            time_approved = True

    print('time_approved',time_approved)
    
    #changed_updated_form
    meter_name_approved = None
    from .APITB import electricityKeeper, waterKeeper, gasKeeper

    # Get meter data 
    meter_name_approved = local_electricityKeeper[meter_name]
    print("meter_name_approved:")
    print(meter_name_approved)
    
    # start to query
    data = {'available': False}

    #get nearest data to start epoch
    time_in_data_available_start = start_epoch * 1000

    # get nearest data to stop epoch
    time_in_data_available_stop = stop_epoch*1000

    deviceEntity = get_device_entity_by_name(restClient=rest_client, deviceName=meter_name_approved[1])
    data_start = rest_client.get_timeseries(entity_id=deviceEntity, keys=meter_name_approved[2],
                                            start_ts=pre_start_epoch_ms,
                                            end_ts=time_in_data_available_start)
    print(data_start)
    data_end = rest_client.get_timeseries(entity_id=deviceEntity, keys=meter_name_approved[2],
                                            start_ts=time_in_data_available_start,
                                            end_ts=time_in_data_available_stop)
    print(data_end)


    ts_distance = maxBoundaryTSRetry * 60 * 60 ** 1000  # when not using clock, check in 12 ours distance

    if not (is_empty_dict(data_end) or is_empty_dict(data_start)):  # check if data is available in such epochs
        data_dict_start = data_start.get(meter_name_approved[2])[0]
        data_dict_end = data_end.get(meter_name_approved[2])[0]
        data_ts_start = data_start.get(meter_name_approved[2])[0].get('ts')
        data_ts_end = data_end.get(meter_name_approved[2])[0].get('ts')

        if(time_in_data_available_start-ts_distance<data_ts_start and data_ts_start<time_in_data_available_start+ts_distance):

            data_start_decode = float(data_dict_start.get('value'))
            data_end_decode = float(data_dict_end.get('value'))
            print(round(data_end_decode-data_start_decode,3))
            data = {}
            data.update({'available': True})
            
            if meter_kind == 'electricity':
                data.update({"telemetry-diff": round((data_end_decode - data_start_decode)*meter_name_approved[3],3)})
                # print(data_end)
                data.update({'unit': 'کیلو وات ساعت'})
            # elif meter_kind == 'water':
            #     data.update({"telemetry-diff": round(data_end_decode-data_start_decode,3)})
            #     # print(data_end.get())
            #     data.update({'unit': 'متر مکعب'})
            
            print(data)

    all_meter_data_return_dict.update({meter_name_approved[0]: data})
    # return jsonify(all_meter_data_return_dict)
    return jsonify(data)























@app.post('/AI_get_meter_data_API')
def ai_get_meter_data_API():
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

    # extract meter data from requst
    meter_kind = request.args.get('meterKind')
    meter_name = request.args.get('meter_name')

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

    # Connect to rest client
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
    print('\n\n\n\n')
    print(20*'*')
    print(local_electricityKeeper)
    print("\n\n\n\n\n\n")
    for meter_info in local_electricityKeeper.get(meter_name):
        meter_info = local_electricityKeeper.get(meter_name)
        print('\n\n\n#####################################\nrun the damn for!\n\n\n')

        DictData0 = {}
        DictData1 = {}
        # print("meter_info: ")
        # print(meter_info)
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

            deviceEntity0 = get_device_entity_by_name(restClient=rest_client, deviceName=meter_name_approved[1])
            deviceEntity1 = deviceEntity0

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

                time_in_data_available_start0 = start_epoch_1hour * 1000
                time_in_data_available_stop0 = stop_epoch_1hour * 1000

                data_start0 = rest_client.get_timeseries(entity_id=deviceEntity0, keys=meter_name_approved[2],
                                                         start_ts=(pre_start_epoch_1hour * 1000),
                                                         end_ts=time_in_data_available_start0)
                data_end0 = rest_client.get_timeseries(entity_id=deviceEntity0, keys=meter_name_approved[2],
                                                       start_ts=time_in_data_available_start0,
                                                       end_ts=time_in_data_available_stop0)

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
        break



    print('here is DictData_lastday: ', DictData_lastday)
    all_charts_data_return_dict.update({'data_hourbyhour': DictData_lastday})  # TODO: include unit and value to data
    print('here', all_charts_data_return_dict)



    return jsonify(all_charts_data_return_dict)



##########################################################
# print('\n\n\n')
# print(20*"*")
# print('Some NEW INFO')
# print(f"")
# print(f"")
# print(f"")
# print(20*"*")
# print('\n\n\n')
#########################################################