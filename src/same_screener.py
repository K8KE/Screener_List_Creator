from calendar import week
import warnings
import pandas as pd
import os
from datetime import date, datetime
from typing import Tuple, Set, List, Dict, Union


# VARIABLES
DATE = "Assigned Date"
SCREENER = "Screener"

COLOR = "Color"
INFO = "Info"

POSITION_NAME = "Global Position Name"
VOLUNTEER_NAME = "Account Name"
CURRENT_STATUS = "Status Name (Current)"

IS_RECRUITING = "Global Is Recruiting"
INTAKE = "Intake Passed To Region"

BGC = "Last BGC Status"
REGION = "Region Name"

international_prefix = "NHQ:ISD - R&R:"



def build_screener_map(yesterday_sheet: pd.DataFrame) -> Dict[str, Dict[str, str]]:
    """
    Build dictionary from previous screener list
    {Volunteer Name: {"Screener": Screener Name, Position: Date}}

    """

    screener_map = {}
    for _, row in yesterday_sheet.iterrows():
        name = row[VOLUNTEER_NAME]
        position = row[POSITION_NAME]
        date = row[DATE]
        screener = row[SCREENER]

        if not screener:
            print(name)
            continue

        if name in screener_map:
            screener_map[name][position] = date
        else:
            screener_map[name] = {
                "screener": screener,
                position: date
            }

    return screener_map


def apply_same_screener(
    original_sheet: pd.DataFrame, 
    screener_map: Dict[str, Dict[str, str]]):
    """
    Based on screener map, assign volunteers to the same screeners they had

    """

    today = date.today()
    today_string = str(today.strftime("%m/%d/%Y"))

    # IF NEW NAME IN YESTERDAY'S LIST, ASSIGN SAME SCREENER
    for index, row in original_sheet.iterrows():
        name = row[VOLUNTEER_NAME]
        position = row[POSITION_NAME]
        date_set = False
        if name in screener_map:
            original_sheet.at[index, SCREENER] = screener_map[name]["screener"]
            if position in screener_map[name]:
                try:
                    original_sheet.at[index, DATE] = screener_map[name][position].strftime("%m/%d/%Y")
                    date_set = True
                except AttributeError:
                    date_set = False
        
        if not date_set:
            original_sheet.at[index, DATE] = today_string
    
    return original_sheet