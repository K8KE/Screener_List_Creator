from helper import *

# download sheets and do some formatting
original_sheet, yesterday_sheet = open_files()
original_sheet = preliminary_formatting(original_sheet)

# fill in default values
sheet_1, wrong_region = closed_and_wrong_region(original_sheet)
sheet_2, wrong_region, bgc_agreed = auto_assignments(sheet_1, wrong_region)

# match up screeners
screener_map = build_screener_map(yesterday_sheet)
sheet_3 = apply_same_screener(sheet_2, screener_map)

output_sheets(sheet_3, wrong_region, bgc_agreed)