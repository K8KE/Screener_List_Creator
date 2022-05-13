from input_output import *
from rules import *
from same_screener import *
from divide_names import *

# download sheets and do some formatting
original_sheet, yesterday_sheet = open_files()
original_sheet = preliminary_formatting(original_sheet)

# fill in default values
sheet_1, wrong_region = closed_and_wrong_region(original_sheet)
sheet_2, wrong_region, bgc_agreed = auto_assignments(sheet_1, wrong_region)

# match up screeners
screener_map = build_screener_map(yesterday_sheet)
sheet_3 = apply_same_screener(sheet_2, screener_map)

screener_limits, weekly_limits = create_roster_limits()
sheet_4 = assign_remaining(sheet_3, screener_limits, weekly_limits)

names, new_names = get_screener_workload(sheet_4)
workload_df = create_workload_df(names, new_names)
print(workload_df)

output_sheets(sheet_4, wrong_region, bgc_agreed)