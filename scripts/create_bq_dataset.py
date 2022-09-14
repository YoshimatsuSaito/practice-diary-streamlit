import os
import sys

from google.cloud import bigquery
from google.oauth2 import service_account

current_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(current_dir, "../"))

from modules.bq_handler import BigqueryHandler
from modules.utils import read_config


def main():
    # bigquery操作用インスタンスの作成
    config_dict = read_config(os.path.join(current_dir, "../config.ini"))
    service_account_info_path = os.path.join(
        current_dir, f"../{config_dict['service_account_info_path']}")
    dataset_name = config_dict["dataset_name"]
    bqh = BigqueryHandler(service_account_info_path=service_account_info_path,
                          dataset_name=dataset_name)

    # データセット作成
    bqh.create_dataset()



if __name__ == "__main__":
    main()

