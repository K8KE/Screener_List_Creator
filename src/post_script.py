import os
from datetime import date
from divide_names import *

today = date.today()
foldername = str(today.strftime("%m-%d-%Y"))
today_sheetname = "LEAD Screener List " + str(today.strftime("%m-%d-%Y")) + ".xlsx"
today_path = os.path.join(foldername, today_sheetname)

sheet = pd.read_excel(today_path)

names, new_names = get_screener_workload(sheet)
workload_df = create_workload_df(names, new_names)
print(workload_df)