from datetime import datetime, timezone
import re
from typing import Optional
import logging

import jdatetime

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

def get_midnight_epoch(timeToConvert: datetime) -> int:
  """
  Gets the epoch time of 12 AM for the current day in UTC.
  """
  # now = datetime.now(timezone.utc)
  # print(type(now))
  midnight = timeToConvert.replace(hour=0, minute=0, second=0, microsecond=0)
  return int(midnight.timestamp())


def match_time_regex(timeTOMatch: str) -> bool | str:
  """
  function to match input to regex of a Date seperated by '/' or '-' or space
  :param timeTOMatch: string input to provide
  :return: boolean to see if the provided string is a time, string for providing the seperator
  """
  date_pattern = r"[0-9]{4}[/\- ][0-9]{1,2}[/\- ][0-9]{1,2}"
  matches = re.finditer(pattern=r"[/\- ]", string=timeTOMatch)
  cnt = 0
  match_start = []
  for match in matches:
    cnt = cnt+1
    match_start.append(match.span()[0])
    # print(match_start)
  # print(cnt)
  # check if the total match happens and total number of seperators are 2 and seperators are same
  # print(match_start)
  math_cond =  re.fullmatch(date_pattern, timeTOMatch) and\
         cnt ==2 and\
         timeTOMatch[match_start[0]] == timeTOMatch[match_start[1]]

  if math_cond:
    return math_cond, timeTOMatch[match_start[0]]
  else:
    return math_cond,  None

def string_to_time(timeToConvert: str) -> datetime:
  """
  converts a Date in string to epoch time at its 12 A.M.

  :param str timeToConvert: The string to convert to a datetime object.

  :return: epoch time as integer
  """
  matched, sep = match_time_regex(timeToConvert)
  if(matched):
    # print("matched")
    # date_str = "2024-05-18"  # Replace with your desired date format
    date_obj = datetime.strptime(timeToConvert, f"%Y{sep}%m{sep}%d")  # Adjust format if needed
    # print(type(date_obj))
    # year = date_obj.year
    # month = date_obj.month
    # day = date_obj.day
    # print(f"Year: {year}, Month: {month}, Day: {day}")
    # print(date_obj.hour, date_obj.minute, date_obj.second)
    return int(date_obj.timestamp())
  else:
    return None

def jalali_string_to_time(timeToConvert: str) -> jdatetime.datetime:
  """
  converts a Date in string to epoch time at its 12 A.M.

  :param str timeToConvert: The string to convert to a datetime object.

  :return: epoch time as integer
  """
  matched, sep = match_time_regex(timeToConvert)
  if(matched):
    # print("matched")
    # date_str = "2024-05-18"  # Replace with your desired date format
    date_obj = jdatetime.datetime.strptime(timeToConvert, f"%Y{sep}%m{sep}%d")  # Adjust format if needed
    print(date_obj)
    # print(type(date_obj))
    # year = date_obj.year
    # month = date_obj.month
    # day = date_obj.day
    # print(f"Year: {year}, Month: {month}, Day: {day}")
    # print(date_obj.hour, date_obj.minute, date_obj.second)
    return int(date_obj.togregorian().timestamp())
  else:
    return None

# def jalali_string_to_epoch()
class dayEpochSwipper:
  def __init__(self, base_epoch: int, backward: Optional[bool]= False, swip_distance: Optional[int] = 60*60,
               max_swip: Optional[int] = 24*60*60, valid_base_swip: Optional[int]=0):
    self.__base_epoch = base_epoch
    self.__swip_distance = swip_distance
    self.__current_epoch = self.__base_epoch
    self.__max_swip = max_swip
    self.__valid_base_swip = valid_base_swip
    self.__backward = backward


  def __iter__(self):
    return self
  def __next__(self):
    try:
      if( self.__base_epoch > self.__valid_base_swip ):  # check if epoch time entered is accepteable, for example,
        # starts after the very first device is installed for customer
        if abs(self.__current_epoch - self.__base_epoch) < self.__max_swip :  # set abs for both forward and backward
          if(self.__backward):
            self.__current_epoch = self.__current_epoch - self.__swip_distance
          else:
            self.__current_epoch = self.__current_epoch + self.__swip_distance
          return self.__current_epoch
        else:
          raise StopIteration
      else:
        raise ValueError

    except ValueError:
      print("in value error")
      raise StopIteration
      logging.warn("not a valid epoch start asked to generate an iterator for. telemetry ticket project")



# Example usage
if __name__ == "__main__":
  ...

  # testing find 12 A.M. epoch
  # midnight_epoch = get_midnight_epoch(datetime.now(timezone.utc))
  # print(f"Epoch time for 12 AM today (UTC): {midnight_epoch}")

  # testing string_to_time()
  # print(string_to_time("2024/05/12"))

  # testing dayepochswipper
  # classSwipper = dayEpochSwipper(datetime.now().timestamp(), 60*15, max_swip=24*60*30, valid_base_swip=1816128872)
  # for stamp in classSwipper:
  #   print(stamp)

  # test jalali string to time
  print(jalali_string_to_time(""))
