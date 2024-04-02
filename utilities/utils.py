import gspread
import tldextract
import validators
import utils_credentials

import pyspark as spark
from pyspark.sql import SparkSession

# Google Sheets #################################################################
sc = spark.sparkContext

gsheet_credential = utils_credentials.gsheet_credential


class GSheetsUtils:
    def __init__(self, credential=gsheet_credential):
        self.credential = gsheet_credential

    def gs_to_dict(self, tab_name, spreadsheet_id):
        gc = gspread.service_account(filename=self.credential)
        sh = gc.open_by_key(spreadsheet_id)
        wks = sh.worksheet(tab_name)
        results_json = wks.get_all_records()
        return results_json

    def gs_to_df(self, tab_name, spreadsheet_id):
        json_data = self.gs_to_dict(tab_name, spreadsheet_id)
        gspread_result = sc.parallelize(json_data).toDF()
        return gspread_result

    def gs_to_list(self, tab_name, spreadsheet_id, relevant_key):
        json_data = self.gs_to_dict(tab_name, spreadsheet_id)
        results_list = [result[relevant_key] for result in json_data]
        return results_list


#################################################################################

# Domain Extraction #############################################################


def extract_domain(url: str) -> str:
    """This function checks wether the input url string is a valid domain name,
    and then returns the domain."""
    domain = f"{tldextract.extract(url).domain}.{tldextract.extract(url).suffix}"
    if not bool(validators.domain(domain)):
        domain = f"{tldextract.extract(url).subdomain}.{tldextract.extract(url).domain}"
    return domain


#################################################################################
