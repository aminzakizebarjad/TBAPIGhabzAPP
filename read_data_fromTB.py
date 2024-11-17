import os
import sys
from datetime import datetime, timedelta
from tb_rest_client.rest_client_ce import RestClientCE
from dotenv import load_dotenv
import pandas as pd

from  app.ghabz.APITB import get_device_entity_by_name


maxBoundaryTSRetry = 12 # hours away from 12 A.M. to check if data exists can be fraction of hour
# load .env file for login information
load_dotenv()

# ThingsBoard REST API URL
base_url = os.getenv("base_url", "http://172.20.2.74")
# Default Tenant Administrator credentials
username = os.getenv("yourThingsBoardUser")
password = os.getenv("yourThingsBoardPass")

local_electricityKeeper = {'01_Library':['کتابخانه', 'LIBRARY', 'M_P_0_0', 300],\
                     '03_Farabi':['فارابی', 'FARABI', 'M_P_0_0', 200],\
                     '04_Sports_Complex':['مجموعه ورزشی', 'SPORT_COMPLEX', 'M_P_0_0', 200], \
                     '05_Apa_TarbiatBadany': ['آپا و تربیت بدنی', 'AmirKabir_Meter_G3', 'D1f0', 120],\
                     '06_Civil_Eng_1':['عمران 1', 'AmirKabir_Meter_G4', 'D1f0', 120],\
                     '07_Civil_Eng_2':['عمران 2', 'AmirKabir_Meter_G4', 'D1f10', 120],\
                     '08_Aerospace':['هوافضا', 'AmirKabir_Meter_G1', 'D1f10', 200],\
                     '09_Mathematics':['ریاضی', 'AmirKabir_Meter_G1', 'D1f0', 120],\
                     '10_Textile_Eng_Transformer1':['نساجی ترانس 1', 'NASAJI', 'M_P_0_0', 500],\
                     '11_Copmuter_Eng_2':['کامپیوتر 2', 'NASAJI', 'M_P_1_0', 120],\
                     '12_Computer_Eng_1':['کامپیوتر 1', 'NASAJI', 'M_P_2_0', 240],\
                     '13_Behdari':['بهداری', 'AmirKabir_Meter_G2', 'D1f0', 120],\
                     '14_Chemical_Eng':['مهندسی شیمی', 'AmirKabir_Meter_G1', 'D1f20', 120],\
                     '15_Polymer':['مهندسی پلیمر', 'AmirKabir_Meter_G1', 'D1f30', 200],\
                     '16_Metallurgy':['متالورژی', 'AmirKabir_Meter_G4', 'D1f40', 120],\
                     '17_Informatic':['انفورماتیک', 'AmirKabir_Meter_G3', 'D1f30', 120],\
                     '18_Mineral_Eng':['معدن', 'AmirKabir_Meter_G4', 'D1f30', 200],\
                     '19_Installations_Dorms':['تاسیسات و امور خوابگاه', 'AmirKabir_Meter_G3', 'D1f10', 120],\
                     '20_Maritime_Eng':['کشتی سازی', 'AmirKabir_Meter_G4', 'D1f20', 120],\
                     '21_Aboreyhan_Pump':['موتورخانه ابوریحان', 'NASAJI', 'M_P_3_0', 400], \
                     '22_Pump_Station': ['پمپ استیشن', 'NASAJI', 'M_P_4_0', 200],\
                     '23_Aboreyhan_1':['ابوریحان 1','ABOREIHAN_1', 'M_P_0_0', 500],\
                     '24_Aboreyhan_2':['ابوریحان 2','ABOREIHAN_1', 'M_P_1_0', 500],\
                     '25_Aboreyhan_3':['ابوریحان 3','ABOREIHAN_2', 'M_P_0_0', 500],\
                     '26_Raftari_Dorm':['خوابگاه رفتاری','ABOREIHAN_2', 'M_P_1_0', 400],\
                     '27_Industrial_Eng_1': ['صنایع 1', 'ELECTRICITY_INDUSTRIAL_ENG', 'M_P_0_0', 400],\
                     '28_Industrial_Eng_2': ['صنایع 2', 'ELECTRICITY_INDUSTRIAL_ENG', 'M_P_1_0', 200],\
                     'biomedic':['مهندسی پزشکی', 'ELECTRICITY_BIOMEDICAL_ENG_1', 'M_P_0_0', 200],\
                     '30_Pump_BioMedical':['مهندسی پزشکی موتورخانه', 'ELECTRICITY_BIOMEDIACL_ENG_3', 'M_P_0_0', 160],\
                     '31_Management_IndependentChem':['مدیریت-شیمی مستقل', 'ELECTRICITY_CHEM_INDEPENDENT', 'M_P_0_0', 200],\
                     '32_FanavariBuilding1_EbnSina':['ابن سینا', 'ELECTRICITY_BIOMEDICAL_ENG_2', 'M_P_0_0', 200],\
                     '33_Nahad':['نهاد رهبری','ELECTRICITY_NAHAD', 'M_P_0_0', 60], \
                     'ghalamchi': ['خوابگاه قلمچی', 'AmirKabir_Meter_G1', 'D2f20', 60]
                     }

def is_empty_dict(d):
    return d is None or not d  # Check if dictionary is None or empty

def change_time_to_epoch(time_str="2024-11-10 14:30:00", time_format="%Y-%m-%d %H:%M:%S"):
    try :
        dt_object = datetime.strptime(time_str, time_format)
    except : 
        dt_object = datetime.strptime(str(time_str), time_format)
    epoch_time = int(dt_object.timestamp()) # in seconds
    return epoch_time

def AI_Elec_Get(meter_kind='electricity', meter_name='23_Aboreyhan_1', start_time='',stop_time=''):
    # get current time and store it as stop_time
    # start_time = "2024-11-8 14:38:00"
    # start_time = change_time_to_epoch(start_time) # TODO: Change if needed #################################3
    # stop_time =  datetime.now()  
    # stop_time = change_time_to_epoch(stop_time.strftime("%Y-%m-%d %H:%M:%S"))
    
    # print('\n\n\n\n\n\n')
    # print(50*'*')
    # print('Start and Stop TIMES:')
    # print(start_time , type(start_time))
    # print(stop_time , type(start_time))


    start_time = change_time_to_epoch(start_time)
    stop_time = change_time_to_epoch(stop_time)

    # useless epochtimes
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
                                            start_ts = start_time * 1000 ,
                                            end_ts = stop_time * 1000,
                                            interval = 3600 * 1000,
                                            agg = 'MAX',
                                            use_strict_data_types= True)



    # data_start = rest_client.get_timeseries(entity_id=deviceEntity, keys=meter_name_approved[2],
    #                                         start_ts=pre_start_epoch_ms,
    #                                         end_ts=time_in_data_available_start)
    # print(data_start)
    # data_end = rest_client.get_timeseries(entity_id=deviceEntity, keys=meter_name_approved[2],
    #                                         start_ts=time_in_data_available_start,
    #                                         end_ts=time_in_data_available_stop)
    # print('\n\n\n\n This is the end data')
    # print(data_end)


    # ts_distance = maxBoundaryTSRetry * 60 * 60 ** 1000  # when not using clock, check in 12 ours distance

    # if not (is_empty_dict(data_end) or is_empty_dict(data_start)):  # check if data is available in such epochs
    #     data_dict_start = data_start.get(meter_name_approved[2])[0]
    #     data_dict_end = data_end.get(meter_name_approved[2])[0]
    #     data_ts_start = data_start.get(meter_name_approved[2])[0].get('ts')
    #     data_ts_end = data_end.get(meter_name_approved[2])[0].get('ts')

    #     if(time_in_data_available_start-ts_distance<data_ts_start and data_ts_start<time_in_data_available_start+ts_distance):

    #         data_start_decode = float(data_dict_start.get('value'))
    #         data_end_decode = float(data_dict_end.get('value'))
    #         print(round(data_end_decode-data_start_decode,3))
    #         data = {}
    #         data.update({'available': True})
            
    #         if meter_kind == 'electricity':
    #             data.update({"telemetry-diff": round((data_end_decode - data_start_decode)*meter_name_approved[3],3)})
    #             # print(data_end)
    #             data.update({'unit': 'کیلو وات ساعت'})
    #         # elif meter_kind == 'water':
    #         #     data.update({"telemetry-diff": round(data_end_decode-data_start_decode,3)})
    #         #     # print(data_end.get())
    #         #     data.update({'unit': 'متر مکعب'})
            
    #         print(data)

    # all_meter_data_return_dict.update({meter_name_approved[0]: data})

    df = pd.DataFrame(data_start.get(meter_name_approved[2]))
    # Check if the DataFrame is empty
    if df.empty:
        return None

    df['datetime'] = pd.to_datetime(df['ts'], unit='ms')
    df = df.rename(columns={'ts': 'epoch_time'})
    df = df[['datetime', 'epoch_time', 'value']]
    df['value'] = df['value'] * meter_name_approved[3]
    df['compensation'] = 0
    df = df.set_index('datetime')
    return df


# Define a function to fetch and save the data for each building
def fetch_and_save_data(building_name, start_date, end_date):
    # Initialize an empty list to collect all the dataframes
    all_data = []
    
    # Loop through the date range in 10-day intervals
    current_start_date = start_date
    while current_start_date < end_date:
        # Define the end date for this interval
        current_end_date = current_start_date + timedelta(days=10)
        if current_end_date > end_date:
            current_end_date = end_date
        
        # Format the date strings to the required format for AI_Elec_Get
        start_time_str = current_start_date.strftime('%Y-%m-%d %H:%M:%S')
        stop_time_str = current_end_date.strftime('%Y-%m-%d %H:%M:%S')
        
        # Fetch the data using AI_Elec_Get (assuming this function returns a DataFrame)
        df = AI_Elec_Get(meter_kind='electricity', meter_name=building_name, 
                         start_time=start_time_str, stop_time=stop_time_str)
        if df is not None and not df.empty:         
            # Append the fetched data to the list
            all_data.append(df)
        
        # Update the current start date to the next interval
        current_start_date = current_end_date
    
    # Concatenate all dataframes into one
    full_data = pd.concat(all_data)
    
    # Save the concatenated data to a file (you can change the file format as needed)
    full_data.to_pickle(f"{building_name}.pkl")
    full_data.to_csv(f"{building_name}.csv")
    print(f"Data for {building_name} saved to {building_name} .csv and .pkl")



#'datetime', 'epoch_time', 'value'
if __name__ == '__main__':
    print("Start the process of making dataset fils")
    
    building_names = local_electricityKeeper.keys()
    print(building_names)

    start_date = datetime(2022, 1, 1)  
    end_date = datetime(2024, 11, 11)  
    
    for building_name in building_names:
        fetch_and_save_data(building_name, start_date, end_date)

    print("Done!")





# building_name = '24_Aboreyhan_2'

# df10 = AI_Elec_Get(meter_kind='electricity', meter_name= building_name, start_time='2024-11-01 14:00:00',stop_time='2024-11-10 14:00:00')
# df9 = AI_Elec_Get(meter_kind='electricity', meter_name= building_name, start_time='2024-10-20 14:00:00',stop_time='2024-11-01 14:00:00')
# df8 = AI_Elec_Get(meter_kind='electricity', meter_name= building_name, start_time='2024-10-10 14:00:00',stop_time='2024-10-20 14:00:00')
# df7 = AI_Elec_Get(meter_kind='electricity', meter_name= building_name, start_time='2024-10-01 14:00:00',stop_time='2024-10-10 14:00:00')
# df6 = AI_Elec_Get(meter_kind='electricity', meter_name= building_name, start_time='2024-09-20 14:00:00',stop_time='2024-10-01 14:00:00')
# df5 = AI_Elec_Get(meter_kind='electricity', meter_name= building_name, start_time='2024-09-10 14:00:00',stop_time='2024-09-20 14:00:00')
# df4 = AI_Elec_Get(meter_kind='electricity', meter_name= building_name, start_time='2024-09-01 14:00:00',stop_time='2024-09-10 14:00:00')
# df3 = AI_Elec_Get(meter_kind='electricity', meter_name= building_name, start_time='2024-08-20 14:00:00',stop_time='2024-09-01 14:00:00')
# df2 = AI_Elec_Get(meter_kind='electricity', meter_name= building_name, start_time='2024-08-10 14:00:00',stop_time='2024-08-20 14:00:00')
# df1 = AI_Elec_Get(meter_kind='electricity', meter_name= building_name, start_time='2024-08-01 14:00:00',stop_time='2024-08-10 14:00:00')

# df = pd.concat([df1,df2,df3,df4,df5,df6,df7,df8,df9,df10], axis= 0)
# df.to_pickle(f"{building_name}.pkl")
# df.to_csv(f"{building_name}.csv")
# print('\n\n\n\n\n\n')
# print(df)