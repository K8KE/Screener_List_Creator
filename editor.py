import warnings
import pandas as pd
import os
from datetime import datetime, date


# DATE = "Date"
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
DIVISION = "Division Name"

today = date.today()

new_data = ""
last_list = ""

cwd = os.getcwd()
for filename in os.listdir(os.path.join(cwd, "data")):
    if filename.startswith("data"): 
        new_data = filename
    elif filename.startswith("Screen"):
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

# FORMAT COLUMNS
datefields = ["Intake Application Date", "Intake Passed To Region", "Last BGC Created", "Submission Date"]
for field in datefields:
    original_sheet[field] = original_sheet[field].dt.strftime('%m/%d/%Y')

original_sheet = original_sheet.drop(["Service Name"], axis=1)

# ADD COLUMNS
for index, column in enumerate([DATE, SCREENER, COLOR, INFO]):
    original_sheet.insert(loc=index, column=column, value="")


# WRONG REGION
columns_list = original_sheet.columns
wrong_region = pd.DataFrame(columns = columns_list)


delete_indices = []
bgc_agreed = []
international_prefix = "NHQ:ISD - R&R:"

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
    not_recruiting = row[IS_RECRUITING] == "No"
    international = position.startswith(international_prefix)
    is_closed = not_recruiting and not international

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


# ASSIGN BASED ON ROLE

lesslee = [
    "Employee", 
    "Inactive Prospective Volunteer",
    "On-Hold General Volunteers",
    "AmeriCorps"
]
kate = [
    "Disaster Event Based Volunteers"
]
US_divisions = [
    "ARC National Operations Division",
    "Central Atlantic Division",
    "North Central Division",
    "Northeast Division",
    "Pacific Division",
    "Southeast and Caribbean Division",
    "Southwest and Rocky Mountains Division"
]

for index, row in original_sheet.iterrows():

    position = row[POSITION_NAME]
    
    if position.startswith(international_prefix):
        original_sheet.at[index, COLOR] = "ISD - R&R"

    if row[DIVISION] == "ARC National Operations Division":
        original_sheet.at[index, SCREENER] = "Lesslee"
    elif row[DIVISION] not in US_divisions:
        original_sheet.at[index, INFO] = "LOCATION"

    if row[CURRENT_STATUS] in kate:
        original_sheet.at[index, SCREENER] = "Kate"
    elif row[CURRENT_STATUS] in lesslee:
        original_sheet.at[index, SCREENER] = "Lesslee"
    elif row[CURRENT_STATUS] == "Biomed Event Based Volunteers":
        original_sheet.at[index, INFO] = "BIOMED"

    if row[BGC] == "Review":
        original_sheet.at[index, SCREENER] = "Lesslee"
    elif row[BGC] == "Processing" or row[BGC] == "Ready":
        original_sheet.at[index, INFO] = "BGC"
    elif row[BGC] == "Agreed":
        bgc_agreed.append(row[VOLUNTEER_NAME])





# BUILD SCREENER MAP
screener_map = {}
for index, row in yesterday_sheet.iterrows():
    name = row[VOLUNTEER_NAME]
    position = row[POSITION_NAME]
    date = row[DATE]
    screener = row[SCREENER]

    if name in screener_map:
        screener_map[name][position] = date
    else:
        screener_map[name] = {
            "screener": screener,
            position: date
        }

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
    

foldername = str(today.strftime("%m-%d-%Y"))

if not os.path.isdir(foldername):
    os.mkdir(foldername)

today_sheetname = "LEAD Screener List " + str(today.strftime("%m-%d-%Y")) + ".xlsx"

# PUT UNASSIGNED AT TOP
original_sheet = original_sheet.sort_values(by=[SCREENER])
original_sheet.to_excel(os.path.join(foldername, today_sheetname))

wrong_region = wrong_region[["Region Name", "Global Position Name", "Account Name", "Status Name (Current)", "Progress Status"]]
wrong_region.to_excel(os.path.join(foldername, "wrong_region.xlsx"))

with open(os.path.join(foldername, "bgc_agreed.txt"), 'w') as f:
    f.write("\n".join(bgc_agreed))