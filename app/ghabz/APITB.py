import time
from tb_rest_client.rest_client_ce import RestClientCE
from tb_rest_client.models.models_ce.entity_id import EntityId
from tb_rest_client.models.models_ce.customer_id import CustomerId
import logging
from typing import List, Dict, Optional
import os
# API Section

# ThingsBoard REST API URL
base_url = os.getenv("base_url", "http://172.20.2.74")
# Default Tenant Administrator credentials
username = os.getenv("yourThingsBoardUser")
password = os.getenv("yourThingsBoardPass")
pageSizeParameter = 10
aliveMinutesParameters = 20  # minutes until we say one device is not active
epochDistanceToCheck = 15  # minutes from base epoch of a day to chech for data must be less  maxBoundaryTSRetry in minutes
maxBoundaryTSRetry = 12 # hours away from 12 A.M. to check if data exists can be fraction of hour
# print(base_url+APILogin)
# x = APIPost(url=base_url+APILogin, json=JsonLogin, headers=HeaderLogin)
# print(x.json())
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# print(int(time.time()))
# TODO: use the stopped and logged_in attributes from RestClientCE to check the connectivity
# the dictionary to hold the gateway names, the number of meters connected to them and the value they must query
waterKeeper = {'station':['استیشن','WATER_STATION','M_P_1_0_frwd'],\
               'metalorgy' :['متالورژی','WATER_METALORGY','M_P_1_0_frwd'],\
               'mosque':['مسجد','WATER_MOSQUE', 'M_P_1_0_frwd'],\
               'aerospace':['هوافضا','WATER_AEROSPACE_ENG', 'M_P_1_0_frwd'],\
               'boiler':['بویلر','WATER_BOILER', 'M_P_1_0_frwd'],\
               'mining':['معدن','WATER_MINING_ENG', 'M_P_1_0_frwd'],\
               'central_kitchen':['سلف مرکزی','WATER_CENTRAL_KITCHEN', 'M_P_1_0_frwd'],\
               'toranj': ['ترنج','WATER_TORANG', 'M_P_1_0_frwd'],\
               'polymer':['پلیمر','WATER_POLYMER', 'M_P_1_0_frwd'],\
               'informatic':['انفورماتیک', 'WATER_INFORMATIC', 'M_P_1_0_frwd'],\
               'chemistry':['شیمی','WATER_CHEM_ENG', 'M_P_1_0_frwd'], \
               'library': ['کتابخانه','WATER_LIBRARY', 'M_P_1_0_frwd'],\
               'computer':['کامپیوتر','WATER_COMPUTER', 'M_P_1_0_frwd'],\
               'tasisat':['تاسیسات','WATER_TASISAT_ABI_CORE', 'M_P_1_0_frwd'],\
               'farabi':['فارابی','FARABI_WATER', 'M_P_1_0_frwd'],\
               'ship-man':['دریا','WATER_SHIP_MANUFACTURING', 'M_P_2_0_frwd'],\
               'main-ship-man': ['اصلی دریا','WATER_SHIP_MANUFACTURING', 'M_P_1_0_frwd'], \
               'main-civil':['عمران اصلی', 'AmirKabir_Meter_G4', 'D2f6'], # instant D2f5\
               'lab-civil':['عمران آزمایشکاه', 'AmirKabir_Meter_G4', 'D2f1'], # instant D2f0\
               'boiler-civil':['عمران موتورخانه', 'AmirKabir_Meter_G3', 'D2f1'] # instant D2f0\
               }
electricityKeeper = {'library':['کتابخانه', 'LIBRARY', 'M_P_0_0', 300],\
                     'farabi':['فارابی', 'FARABI', 'M_P_0_0', 200],\
                     'sport-cplx':['مجموعه ورزشی', 'SPORT_COMPLEX', 'M_P_0_0', 200], \
                     'physical-edu': ['آپا و تربیت بدنی', 'AmirKabir_Meter_G3', 'D1f0', 120],\
                     'civil-1':['عمران 1', 'AmirKabir_Meter_G4', 'D1f0', 120],\
                     'civil-2':['عمران 2', 'AmirKabir_Meter_G4', 'D1f10', 120],\
                     'aerospace':['هوافضا', 'AmirKabir_Meter_G1', 'D1f10', 200],\
                     'math':['ریاضی', 'AmirKabir_Meter_G1', 'D1f0', 120],\
                     'nasaji-trans1':['نساجی ترانس 1', 'NASAJI', 'M_P_0_0', 500],\
                     'computer-2':['کامپیوتر 2', 'NASAJI', 'M_P_1_0', 120],\
                     'computer-1':['کامپیوتر 1', 'NASAJI', 'M_P_2_0', 240],\
                     'clinic':['بهداری', 'AmirKabir_Meter_G2', 'D1f0', 120],\
                     'chem':['مهندسی شیمی', 'AmirKabir_Meter_G1', 'D1f20', 120],\
                     'polymer':['مهندسی پلیمر', 'AmirKabir_Meter_G1', 'D1f30', 200],\
                     'metalorgy':['متالورژی', 'AmirKabir_Meter_G4', 'D1f40', 120],\
                     'informatic':['انفورماتیک', 'AmirKabir_Meter_G3', 'D1f30', 120],\
                     'mining':['معدن', 'AmirKabir_Meter_G4', 'D1f30', 200],\
                     'tasisat':['تاسیسات و امور خوابگاه', 'AmirKabir_Meter_G3', 'D1f10', 120],\
                     'ship-man':['کشتی سازی', 'AmirKabir_Meter_G4', 'D1f20', 120],\
                     'boiler-aboreihan':['موتورخانه ابوریحان', 'NASAJI', 'M_P_3_0', 400], \
                     'station-pomp': ['پمپ استیشن', 'NASAJI', 'M_P_4_0', 200],\
                     'aboreihan-1':['ابوریحان 1','ABOREIHAN_1', 'M_P_0_0', 500],\
                     'aboreihan-2':['ابوریحان 2','ABOREIHAN_1', 'M_P_1_0', 500],\
                     'aboreihan-3':['ابوریحان 3','ABOREIHAN_2', 'M_P_0_0', 500],\
                     'aboreihan-4':['ابوریحان 4','ABOREIHAN_2', 'M_P_1_0', 500],\
                     'indust-1': ['صنایع 1', 'ELECTRICITY_INDUSTRIAL_ENG', 'M_P_0_0', 400],\
                     'indust-2': ['صنایع 2', 'ELECTRICITY_INDUSTRIAL_ENG', 'M_P_1_0', 200],\
                     'biomedic':['مهندسی پزشکی', 'ELECTRICITY_BIOMEDICAL_ENG_1', 'M_P_0_0', 200],\
                     'biomedic-boiler':['مهندسی پزشکی موتورخانه', 'ELECTRICITY_BIOMEDIACL_ENG_3', 'M_P_0_0', 160],\
                     'chem-ind':['مدیریت-شیمی مستقل', 'ELECTRICITY_CHEM_INDEPENDENT', 'M_P_0_0', 200],\
                     'ibn-sina':['ابن سینا', 'ELECTRICITY_BIOMEDICAL_ENG_2', 'M_P_0_0', 200],\
                     'nahad':['نهاد رهبری','ELECTRICITY_NAHAD', 'M_P_0_0', 60], \
                     'ghalamchi': ['خوابگاه قلمچی', 'AmirKabir_Meter_G1', 'D2f20', 60]
                     }
gasKeeper = {}
wholeKeeeper = {'water':waterKeeper, 'electricity':electricityKeeper, 'natural-gas':gasKeeper}
def get_customer_names(restClient: RestClientCE) -> List[str]:
    """
    provides names of customers in the whole system
    :param restClient: the client class of thingsBoard
    :return: a list of all customers availale
    """
    customerList = []
    pageInc = 0

    while(True):
        resCustomers = restClient.get_customers(page_size=pageSizeParameter, page=pageInc)
        pageInc = pageInc+1

        if(len(resCustomers.data)):
            for customer in resCustomers.data:
                customerList.append(customer.name)
        if(len(resCustomers.data)<pageSizeParameter):
            break

    return customerList

def get_customer_name_id_dict(restClient: RestClientCE) -> Dict[str, str]:
    """
    provides names of customers in the whole system
    :param restClient: the client class of thingsBoard
    :return: a list of all customers availale
    """
    customerDict = {}
    pageInc = 0

    while(True):
        resCustomers = restClient.get_customers(page_size=pageSizeParameter, page=pageInc)
        pageInc = pageInc+1

        if(len(resCustomers.data)):
            for customer in resCustomers.data:
                customerDict.update({customer.name: customer.id.id})
        if(len(resCustomers.data)<pageSizeParameter):
            break

    return customerDict

def get_customer_entity(restClient: RestClientCE, customerID: str) -> EntityId:
    return CustomerId(id=customerID, entity_type='CUSTOMER')

def get_customer_entity_by_name(restClient: RestClientCE, customerName: str) -> CustomerId:
    try:
        customer_dict = get_customer_name_id_dict(restClient)
        return CustomerId(id=customer_dict.get(customerName), entity_type='CUSTOMER')
    except ValueError: logging.error("%s does not exist in customers", customerName)

def get_device_names(restClient: RestClientCE) -> List[str]:
    """
    provides names of devices in the whole system
    :param restClient: the client class of thingsBoard
    :return: a list of all devices availale
    """
    deviceList = []
    pageInc = 0

    while(True):
        resDevices = restClient.get_tenant_devices(page_size=pageSizeParameter, page=pageInc)
        pageInc = pageInc+1

        if(len(resDevices.data)):
            for device in resDevices.data:
                deviceList.append(device.name)
        if(len(resDevices.data)<pageSizeParameter):
            break

    return deviceList

def get_device_name_id_dict(restClient: RestClientCE) -> Dict[str, str]:
    """
    provides names of devices in the whole system
    :param restClient: the client class of thingsBoard
    :return: a list of all devices availale
    """
    deviceList = {}
    pageInc = 0

    while(True):
        resDevices = restClient.get_tenant_devices(page_size=pageSizeParameter, page=pageInc)
        pageInc = pageInc+1

        if(len(resDevices.data)):
            for device in resDevices.data:
                deviceList.update({device.name: device.id.id})
        if(len(resDevices.data)<pageSizeParameter):
            break

    return deviceList

def get_device_entity(restClient: RestClientCE, deviceID: str) -> EntityId:
    return EntityId(id=deviceID, entity_type='DEVICE')

def get_device_entity_by_name(restClient: RestClientCE, deviceName: str) -> EntityId:
    try:
        device_dict = get_device_name_id_dict(restClient)
        return EntityId(id=device_dict.get(deviceName), entity_type='DEVICE')
    except ValueError:
        logging.error("%s does not exist in devices", deviceName)

def get_device_alive(restClient: RestClientCE, deviceName: str):
    try:
        nowTime = int(time.time())
        allowedTime = nowTime-aliveMinutesParameters*60
        device_dict = get_device_name_id_dict(restClient)
        entity_id = EntityId(id=device_dict.get(deviceName), entity_type='DEVICE')
        latestTimeSeries = restClient.get_timeseries(entity_id=entity_id, keys=key_to_ask_for_nearest,
                                                    start_ts=allowedTime*1000,
                                                     end_ts= nowTime*1000)
        # restClient.get_latest_timeseries(entity_id)
        latestData = next(iter(latestTimeSeries.values()), None)
        if latestData:
            latestTS = latestData[0].get("ts")
            return allowedTime < int(latestTS/1000)
        else:
            return False

    except ValueError:
        logging.error("%s does not exist in devices", deviceName)

from .util import string_to_time, dayEpochSwipper
# the date will come from a form in html

# we got three type of devices, electicity of mine, water of mine, electricity of ansari,
# we give them to nearest. each of which is not availble the output data will not contain any key related to that.
# so always we can have the result with one of the below keys
key_to_ask_for_nearest = 'M_P_0_0,M_P_1_0_frwd,D1f0'
def get_nearest_time_epoch(restClient: RestClientCE, deviceName: str, date: str,
                           maxBoundaryTSRetryInner:float,
                           epochDistanceToCheckInner:int,
                           key_to_ask_for_nearest: Optional[str],
                           backwards: bool = False,
                           from_epoch:bool=False, ):
    """
    :param restClient: the thingsboard client to work with
    :param deviceName: the device that we want to derive data for
    :param date: must be in format "yyyy-mm-dd" or "yyyy/mm/dd"
    :return: the nearest ts that has data to the input date
    """

    if not from_epoch:
        epochToCheck = string_to_time(date)
    else:
        epochToCheck = date

    # epochDistanceToCheck  is entered in minutes so multiplication to 60 is needed,
    # maxBoundaryTSRetry is entered in hours so multilication to 60*60 is needed
    epochDistanceToCheckInner = int(epochDistanceToCheckInner * 60)
    maxBoundaryTSRetryInner = int(maxBoundaryTSRetryInner * 60 * 60)
    if maxBoundaryTSRetryInner < epochDistanceToCheckInner:
        maxBoundaryTSRetryInner = epochDistanceToCheckInner
    epochSwipperClass = dayEpochSwipper(base_epoch=epochToCheck, swip_distance=epochDistanceToCheckInner,
                                        max_swip=maxBoundaryTSRetryInner, backward=backwards)
    deviceEntity = get_device_entity_by_name(restClient=restClient, deviceName=deviceName)
    epochDistanceToCheckms = int(epochDistanceToCheckInner * 1000)  # swip distance to check is in minutes
    # i = 0
    for swip in epochSwipperClass:
        # print(i, swip)
        # i=i+1
        swipms = swip*1000  # TB timestaamp accuracy is in miliseconds so multiplication to 1000 is done
        data = restClient.get_timeseries(entity_id=deviceEntity, keys=key_to_ask_for_nearest,
                                         start_ts=swipms, end_ts= swipms+epochDistanceToCheckms)
        if data.keys() :
            # print("there is data")
            return data.get(list(data.keys())[0])[0].get('ts')
            break
    else:
        # print("no data found.")
        return 0  # when no data is found in the eopchSwipperClass then the is no data in this epoch scope and 0 is returned


def decor_get_nearest_time_epoch(restClient: RestClientCE, deviceName: str, date: str,
                                maxBoundaryTSRetryInner = maxBoundaryTSRetry,
                                epochDistanceToCheckInner = epochDistanceToCheck,
                                 key_to_ask_for_nearest:Optional[str]=key_to_ask_for_nearest, from_epoch:bool=False ):
    """
    do the exact thing that get_nearest_epoch_time does but in forward way first and backward
    if the forward did not work
    :param restClient: the thingsboard client to work with
    :param deviceName: the device that we want to derive data for
    :param date: must be in format "yyyy-mm-dd" or "yyyy/mm/dd"
    :return: the nearest ts that has data to the input date
    """
    ts = get_nearest_time_epoch(restClient, deviceName, date, backwards=False,
                                maxBoundaryTSRetryInner = maxBoundaryTSRetryInner,
                                epochDistanceToCheckInner = epochDistanceToCheckInner,
                                key_to_ask_for_nearest=key_to_ask_for_nearest, from_epoch=from_epoch)
    if ts:
        print("in forward")
        return ts
    else:
        ts = get_nearest_time_epoch(restClient, deviceName, date, backwards=True,
                                    maxBoundaryTSRetryInner=maxBoundaryTSRetryInner,
                                    epochDistanceToCheckInner=epochDistanceToCheckInner,
                                    key_to_ask_for_nearest=key_to_ask_for_nearest, from_epoch=from_epoch)
        print("in backward")
        return ts


# with RestClientCE(base_url=base_url) as rest_client:
#     try:
#         rest_client.login(username=username, password=password)
#
#         # we can get all tenenat devices
#         # res = rest_client.get_tenant_device_infos(page_size=10, page=0)
#
#         # or we can get customer devices
#         cus_res = rest_client.get_customers(page_size=10, page=0)
#         # print(res.data)
#
#         # printing devices
#         for customer in cus_res.data:
#             print(customer.name, customer.id.id)
#
#         print(f"\nprinting devices for cutomer: {cus_res.data[3].name}\n")
#         res = rest_client.get_customer_devices(
#             CustomerId(id=cus_res.data[3].id.id, entity_type= 'CUSTOMER'), page_size=10, page=0)
#         print(res.data)
#
#         # printing devices name, id and latest telemetries
#         for device in res.data:
#             print(device.name, device.id.id)
#
#             # if (device.active):
#             entityID = EntityId(id=device.id.id, entity_type='DEVICE')
#             print(rest_client.get_latest_timeseries(entityID))
#             rest_client.get_timeseries_keys(device_profile_id= device.device_profile_id)
#
#             rest_client.get_timeseries(entity_id=entityID,start_ts= int(time.time()) - 60*60*24*7*30, end_ts= int(time.time()))
#         # else:
#             print(f"device {device.name} not active")
#
#         # logging.info("Device info:\n%r", res)
#     except ApiException as e:
#         logging.exception(e)

if __name__ == "__main__":
    rest_client = RestClientCE(base_url=base_url)
    # print(rest_client.logged_in)
    rest_client.login(username=username, password=password)

    # testing functions
    print(rest_client.logged_in)
    # print(rest_client.get_latest_timeseries(entity_id=))
    # print(get_device_names(rest_client))
    # print(get_device_name_id_dict(rest_client))
    # print(get_device_entity_by_name(rest_client, 'WATER_INFORMATIC'))
    # print(get_customer_name_id_dict(rest_client))

    # print(get_customer_entity_by_name(rest_client, 'AMIRKABIR'))

    # print(get_device_alive(rest_client, 'WATER_TORANG'))
    # deviceEntity = get_device_entity_by_name(restClient=rest_client, deviceName='WATER_TORANG')
    # print(rest_client.get_timeseries_keys(deviceEntity))

    print(decor_get_nearest_time_epoch(restClient=rest_client, deviceName='WATER_MOSQUE', date='2023-11-28', ))