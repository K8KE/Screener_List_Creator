import warnings
import pandas as pd
from datetime import datetime, date
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

all_screeners = {
        'Melinda', 
        'Adrienne', 'Lynette', 'Karina',
        'Younos', 'Kate', 'Guy', 'Kimberly', 
        'Maia', 'Maria', 'Elizabeth', 
        'Lesslee', 'Annie', 'Anchita',
        'Vanessa', 'Cherelle', 'Passha'
    }


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
        else:
            screener_limits[screener]["Limit"] = 10
            
        if row["Limit On"] == "week":
            weekly_limits.append(screener)

    return screener_limits, weekly_limits


def get_screener_workload(original_sheet):
    today = date.today()
    today_string = str(today.strftime("%m/%d/%Y"))
    
    names = {screener: 0 for screener in all_screeners}
    new_names = {screener: 0 for screener in all_screeners}

    for _, row in original_sheet.iterrows():

        screener = row[SCREENER]
        if pd.isnull(screener) or not screener:
            continue

        screener = screener.strip()

        if screener not in names:
            print("." + screener + ".")
            continue
        
        names[screener] += 1
        if (row[DATE] == today_string and pd.isnull(row["Progress Status"])):
            new_names[screener] += 1
        
    return names, new_names


def create_workload_df(names, new_names):
    new_dict = {}
    for name, load in names.items():
        new_dict[name] = {"Total": load}
    
    for name, load in new_names.items():
        new_dict[name]["New"] = load

    load_df = pd.DataFrame.from_dict(new_dict, orient='index')
    return load_df


def screener_limit_check(screener_limits):
    to_delete = []
    for name in screener_limits:

        if screener_limits[name]["Limit"] <= 0:
            to_delete.append(name)
    
    for name in to_delete:
        del screener_limits[name]


def assign_remaining(
    original_sheet: pd.DataFrame, 
    screener_limits: Dict[str, Dict[str, Union[str, int]]],
    weekly_limits: List[str]) -> pd.DataFrame:

    current_workload, _ = get_screener_workload(original_sheet)

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

    original_sheet = original_sheet.sort_values(by='Color')

    for index, row in original_sheet.iterrows():

        if row[SCREENER]:
            continue

        if not screeners:
            print('OVERLOAD')
            break

        name = row[VOLUNTEER_NAME]

        if name in assignments:
            assigned_screener = assignments[name]
            try:
                screeners.remove(assigned_screener)
            except ValueError:
                print("CHECK " + assigned_screener + " ASSIGNMENTS")
            
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
        
        screener_limits[assigned_screener]["Limit"] -= 1

        if screener_limits[assigned_screener]["Limit"] > 0:
            screeners.append(assigned_screener)

        original_sheet.at[index, SCREENER] = assigned_screener

    return original_sheet




