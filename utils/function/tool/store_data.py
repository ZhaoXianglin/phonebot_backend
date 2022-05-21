
import json
import pandas as pd

def store_data_to_json(data, file_json):
    with open (file_json, 'w') as file_json:
        json.dump(data, file_json, indent=4)

    return "[Successfully store in json file]"

def store_data_to_xlsx(data_df, file_excel):

    data_df.to_excel('data/critique_related/%s.xlsx' % file_excel)
    return "[Successfully store in excel file]"