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
        if not position or pd.isnull(row[VOLUNTEER_NAME]):
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
        intake_status = str(row["Intake Progress Status"])
        if intake_status == "Passed to National Headquarters" or intake_status == "Passed to Regional Volunteer Services" or intake_status.startswith("RVS"):
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

    to_kate = "Kate"
    kate = [
        "Disaster Event Based Volunteers",
        "Employee", 
        "Inactive Prospective Volunteer",
        "On-Hold General Volunteers",
        "AmeriCorps"
    ]
    
    special_positions = {
        "NHQ:ISD R&R Deployment Coordinator": "Vanessa"
    }
    name_to_screener = {}

    bgc_regions = [
        "Michigan Region", "Greater New York Region", 
        "Eastern New York Region", "Western New York Region", 
        "Kentucky Region"]
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
        
        if row[VOLUNTEER_NAME].title() in name_to_screener:
            original_sheet.at[index, SCREENER] = name_to_screener[row[VOLUNTEER_NAME].title()]

        if row[REGION] == "ARC National Operations":
            original_sheet.at[index, SCREENER] = to_kate
        elif row[REGION] in non_US_region:
            original_sheet.at[index, INFO] = "LOCATION"

        if row[CURRENT_STATUS] in kate:
            original_sheet.at[index, SCREENER] = to_kate
        elif row[CURRENT_STATUS] == "Biomed Event Based Volunteers":
            original_sheet.at[index, INFO] = "BIOMED"
        if row[POSITION_NAME] in special_positions:
            original_sheet.at[index, SCREENER] = special_positions[POSITION_NAME]

        if row[BGC] == "Review":
            original_sheet.at[index, SCREENER] = to_kate
        elif row[BGC] == "Ready":
            if row["Region Name"] in bgc_regions:
                original_sheet.at[index, INFO] = "BGC"
            else:
                original_sheet.at[index, SCREENER] = to_kate
        elif row[BGC] == "Processing":
            original_sheet.at[index, INFO] = "BGC"
        elif row[BGC] == "Agreed":
            bgc_agreed.append(row[VOLUNTEER_NAME])

        if row["Intake Progress Status"] == "Passed to Regional Department":
            original_sheet.at[index, SCREENER] = to_kate
        

    original_sheet = original_sheet.drop(delete_indices_2)
    return original_sheet, wrong_region, bgc_agreed