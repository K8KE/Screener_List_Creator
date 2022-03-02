import warnings
import pandas as pd
from datetime import datetime
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


def create_roster_limits() -> pd.DataFrame:
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        screener_roster = pd.read_excel(
            "NHQ Screener Roster.xlsx", 
            engine="openpyxl")

    screener_limits = {}
    weekly_limits = []

    day = datetime.today().strftime('%A')[0].upper()

    for _, row in screener_roster.iterrows():

        screener_name = row["Screener"]

        if pd.isnull(screener_name):
            continue
        screener = screener_name.split()[0]

        is_available = row["Available to screen"].strip()
        if is_available != "Yes":
            continue

        if row["No List Days"] == day:
            continue

        screener_limits[screener] = {"BGC": str(row["Background Checks"]).strip()}

        # screener_limits[screener]["Limit"] = 3
        if not pd.isnull(row["Limit"]):
            screener_limits[screener]["Limit"] = int(row["Limit"])
            
        if row["Limit On"] == "week":
            weekly_limits.append(screener)

    return screener_limits, weekly_limits


def get_screener_workload(original_sheet):
    screener_list = {
        'Jake', 'Melinda', 'Xenia', 'Reshma', 'Manuel',
        'Wajiha', 'Adrienne', 'Lynette', 'Karina', 'Karen',
        'Jacqueline', 'Younos', 'Jawanza', 'Kate', 'Brittany',
        'Guy', 'Danielle', 'Nandhini', 'Kimberly', 'Bella',
        'Maia', 'Maria', 'Elizabeth', 'Lesslee'
    }
    screener_names = {screener: set() for screener in screener_list}

    for _, row in original_sheet.iterrows():

        screener = row[SCREENER]
        if pd.isnull(screener) or not screener:
            continue

        screener = screener.strip()

        if screener not in screener_names:
            print("." + screener + ".")
            continue

        volunteer = row[VOLUNTEER_NAME]
        screener_names[screener].add(volunteer)

    screener_counts = {screener: len(screener_names[screener]) for screener in screener_names}
    return screener_counts


def screener_limit_check(screener_limits):
    to_delete = []
    for name in screener_limits:
        if "Limit" not in screener_limits[name]:
            continue

        if screener_limits[name]["Limit"] <= 0:
            to_delete.append(name)
    
    for name in to_delete:
        del screener_limits[name]


def assign_remaining(
    original_sheet: pd.DataFrame, 
    screener_limits: Dict[str, Dict[str, Union[str, int]]],
    weekly_limits: List[str]) -> pd.DataFrame:

    current_workload = get_screener_workload(original_sheet)

    for name in weekly_limits:
        total_limit = screener_limits[name]["Limit"]
        current_names = current_workload[name]

        if total_limit > current_names:
            screener_limits[name]["Limit"] = total_limit - current_names
        else:
            del screener_limits[name]

    screener_limit_check(screener_limits)
    screeners = list(screener_limits.keys())

    assignments = {}

    for index, row in original_sheet.iterrows():

        if row[SCREENER]:
            continue

        if not screeners:
            print(screener_limits)
            break

        name = row[VOLUNTEER_NAME]

        if name in assignments:
            assigned_screener = assignments[name]
        else:
            if row[INFO] == "BGC":
                for screener in screeners:
                    if screener_limits[screener]["BGC"] == "Yes":
                        assigned_screener = screener
                        break
                screeners.remove(assigned_screener)
            else:
                assigned_screener = screeners.pop(0)
                
            assignments[name] = assigned_screener
            
            remaining = 10
            if "Limit" in screener_limits[assigned_screener]:
                remaining = screener_limits[assigned_screener]["Limit"] - 1
                screener_limits[assigned_screener]["Limit"] = remaining

            if remaining != 0:
                screeners.append(assigned_screener)

        original_sheet.at[index, SCREENER] = assigned_screener

    return original_sheet





