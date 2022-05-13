import warnings
import pandas as pd
import os
from datetime import date
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


def open_files() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Open files in data folder
    original_sheet = "data*"
    yesterday_sheet = "Screener List*"

    """

    new_data = ""
    last_list = ""

    cwd = os.getcwd()
    for filename in os.listdir(os.path.join(cwd, "data")):
        if filename.startswith("data"): 
            new_data = filename
        elif filename.startswith("Screener List"):
            last_list = filename

    if not new_data or not last_list:
        new_data = input("Enter name of today's file: ")
        last_list = input("Enter name of yesterday's file: ")


    # OPEN FILES
    new_data_path = os.path.join("data", new_data)
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        original_sheet = pd.read_excel(
            new_data_path, 
            engine="openpyxl")

    last_list_path = os.path.join("data", last_list)
    yesterday_sheet = pd.read_excel(last_list_path)

    return original_sheet, yesterday_sheet


def preliminary_formatting(original_sheet: pd.DataFrame) -> pd.DataFrame:
    """
    Delete unused columns
    Add additional columns

    """

    # FORMAT COLUMNS
    datefields = ["Intake Application Date", "Intake Passed To Region", "Last BGC Created", "Submission Date"]

    for field in datefields:
        original_sheet[field] = original_sheet[field].dt.strftime('%m/%d/%Y')

    original_sheet = original_sheet.drop(["Service Name"], axis=1)

    # ADD COLUMNS
    for index, column in enumerate([DATE, SCREENER, COLOR, INFO]):
        original_sheet.insert(loc=index, column=column, value="")

    return original_sheet


def output_sheets(
    original_sheet: pd.DataFrame, 
    wrong_region: pd.DataFrame, 
    bgc_agreed: List[str]) -> None:
    """
    Output sheets

    """

    today = date.today()
    foldername = str(today.strftime("%m-%d-%Y"))

    if not os.path.isdir(foldername):
        os.mkdir(foldername)

    today_sheetname = "LEAD Screener List " + str(today.strftime("%m-%d-%Y")) + ".xlsx"
    wr_sheetname = "WR " + str(today.strftime("%m-%d-%Y")) + ".xlsx"

    # PUT UNASSIGNED AT TOP
    # original_sheet = original_sheet.sort_values(by=[VOLUNTEER_NAME, SCREENER])
    original_sheet.to_excel(os.path.join(foldername, today_sheetname))

    wrong_region = wrong_region[["Region Name", "Global Position Name", "Account Name", "Status Name (Current)", "Progress Status"]]
    wrong_region.to_excel(os.path.join(foldername, wr_sheetname))

    with open(os.path.join(foldername, "bgc_agreed.txt"), 'w') as f:
        f.write("\n".join(bgc_agreed))