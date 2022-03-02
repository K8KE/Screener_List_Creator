import pandas as pd
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



def closed_and_wrong_region(original_sheet: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, Set[str]]:
    """
    Deal with closed positions appropriately
    Record names that applied in the wrong region

    """

    # WRONG REGION
    columns_list = original_sheet.columns
    wrong_region = pd.DataFrame(columns = columns_list)

    delete_indices = []

    for index, row in original_sheet.iterrows():

        position = row[POSITION_NAME]

        # DELETE
        if not position:
            delete_indices.append(index)
            continue

        if row["Opportunity Status"] == "Pending Not In Region":
            delete_indices.append(index)
            wrong_region = wrong_region.append(row, ignore_index=True)
            continue
        
        # IS OPEN POSITION
        is_closed = row[IS_RECRUITING] == "No"

        # READY TO VOLUNTEER
        new_volunteer = row[CURRENT_STATUS] == "Prospective Volunteer"
        intaked = not pd.isnull(row[INTAKE])
        if row["Intake Progress Status"] == "Passed to National Headquarters" or row["Intake Progress Status"] == "Passed to Regional Volunteer Services":
            intaked = True
        not_ready = new_volunteer and not intaked

        if is_closed:

            if not_ready:
                original_sheet.at[index, POSITION_NAME] = position + " (closed for recruitment, not passed to region)"
                original_sheet.at[index, COLOR] = "ORANGE"
            else:
                original_sheet.at[index, POSITION_NAME] = position + " (closed for recruitment)"
                original_sheet.at[index, COLOR] = "RED"

        elif not is_closed:

            if not_ready: # applied for open position but not done with intake - ignore for now
                delete_indices.append(index)


    delete_indices = list(set(delete_indices))
    original_sheet = original_sheet.drop(delete_indices)

    return original_sheet, wrong_region


def auto_assignments(
    original_sheet: pd.DataFrame, 
    wrong_region: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    """
    Automatically assign volunteers in special conditions to specific screeners
    (ex. weird region, weird status, etc)

    """

    wrong_region_names = set(wrong_region[VOLUNTEER_NAME].tolist())

    to_lesslee = "Kate"
    lesslee = [
        "Employee", 
        "Inactive Prospective Volunteer",
        "On-Hold General Volunteers",
        "AmeriCorps"
    ]
    to_kate = "Kate"
    kate = [
        "Disaster Event Based Volunteers"
    ]
    kate_positions = [
        "NHQ:ISD- R&R: Response Info Analyst Volunteer Support"
    ]
    non_US_region = [
        "Bagram AB", "Central Europe Region", 
        "Deployed Sites", "EuroMED", "Japan", 
        "Korea", "US Naval Station Guantanamo Bay"
    ]
    bgc_agreed = []
    delete_indices_2 = []

    for index, row in original_sheet.iterrows():

        if row[VOLUNTEER_NAME] in wrong_region_names:
            delete_indices_2.append(index)
            wrong_region = wrong_region.append(row, ignore_index=True)
            continue

        if row[REGION] == "ARC National Operations":
            original_sheet.at[index, SCREENER] = to_lesslee
        elif row[REGION] in non_US_region:
            original_sheet.at[index, INFO] = "LOCATION"

        if row[CURRENT_STATUS] in kate:
            original_sheet.at[index, SCREENER] = to_kate
        elif row[CURRENT_STATUS] in lesslee:
            original_sheet.at[index, SCREENER] = to_lesslee
        elif row[CURRENT_STATUS] == "Biomed Event Based Volunteers":
            original_sheet.at[index, INFO] = "BIOMED"
        if row[POSITION_NAME] in kate_positions:
            original_sheet.at[index, SCREENER] = to_kate

        if row[BGC] == "Review":
            original_sheet.at[index, SCREENER] = to_lesslee
        elif row[BGC] == "Processing" or row[BGC] == "Ready":
            original_sheet.at[index, INFO] = "BGC"
        elif row[BGC] == "Agreed":
            bgc_agreed.append(row[VOLUNTEER_NAME])
        

    original_sheet = original_sheet.drop(delete_indices_2)
    return original_sheet, wrong_region, bgc_agreed