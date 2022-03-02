import warnings
import pandas as pd

DATE = "Date"
SCREENER = "Screener"

COLOR = "Color"
HIGHLIGHT = "Highlight"

POSITION_NAME = "Global Position Name"
VOLUNTEER_NAME = "Account Name"
CURRENT_STATUS = "Status Name (Current)"

IS_RECRUITING = "Global Is Recruiting"
INTAKE = "Intake Passed To Region"

different = [
    "Austin, Monique", 
    "O'Connell, Debra",
    "Ahluwalia, Milli",
    "Kakkar, Aaruti",

    "Hope, Maricel", # Demia != DeMia

    "Rodriguez, Eric", # Lesslee != Lesslee-LINK
    "Judd, Derek", # same as above
    "Mora, Veronica",

    "Espinosa, Lahur", # employee so went to lesslee but should IR&R be treated differently? (was actually assigned to amanda)
    "Prado-Gannon, Luz", # same as above
    
    "Campbell, Ava", # Xenia (Xanthipi) Daskalopoulou != Xenia
    ]

# filepath = input("Enter name of automated file: ")
filepath = "02-13-2022/LEAD Screener List 02-13-2022.xlsx"
automated_sheet = pd.read_excel(filepath)

# filepath2 = input("Enter name of manually created file: ")
filepath = "data/Screener List 02-09-2022.xlsx"
manual_sheet = pd.read_excel(filepath)

name_to_screener = {}

for index, row in manual_sheet.iterrows():
    name = row[VOLUNTEER_NAME]
    screener = row[SCREENER]

    if name in different:
        continue

    if name not in name_to_screener:
        name_to_screener[name] = screener.strip()


for index, row in automated_sheet.iterrows():

    name = row[VOLUNTEER_NAME]
    screener = row[SCREENER]

    if not pd.isnull(screener) and name in name_to_screener:
        assert screener == name_to_screener[name]