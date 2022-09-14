import datetime
import os
import sys
from datetime import datetime as dt

from google.cloud import bigquery


current_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(current_dir, "../"))

from modules.bq_handler import BigqueryHandler
from modules.utils import read_config

class PracticeTableHandler:
    """
    practiceテーブル操作用のクラス
    データベースを扱う際のコーディングのベストプラクティスがあると思われるので、折りを見て修正しても良い
    """
    def __init__(self, create_table=False):
        # bigquery操作用インスタンスの作成
        config_dict = read_config(os.path.join(current_dir, "../config.ini"))
        service_account_info_path = os.path.join(
            current_dir, f"../{config_dict['service_account_info_path']}")
        dataset_name = config_dict["dataset_name"]
        table_name = config_dict["practice_table_name"]
        self.bqh = BigqueryHandler(service_account_info_path=service_account_info_path,
                              dataset_name=dataset_name,
                              table_name=table_name)

        # このスクリプトがmainで使用されるとき、create_table=Trueでテーブル自体のCREATEを行う
        if create_table:
            # テーブル作成
            schema = [
                bigquery.SchemaField("day", "DATE", mode="REQUIRED"),
                bigquery.SchemaField("order_menu", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("distance", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("sec", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("rest_meter", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("rest_minutes", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("rest_way", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("user", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("created_at", "DATETIME", mode="REQUIRED")
            ]
            self.bqh.create_table(schema)
    
    def read(self, day_start, day_end, username):
        query = f"""
        SELECT day, order_menu, distance, sec, rest_meter, rest_minutes, rest_way
        FROM `{self.bqh.dataset_name}.{self.bqh.table_name}`
        WHERE day >= '{day_start}'
        AND day <= '{day_end}'
        AND user = '{username}'
        """
        df = self.bqh.read(query)
        df = df.sort_values(by="day", ascending=False)
        return df
    
    def insert(self, dict_input):
        """
        BigqueryHandlerを用いて実際にpracticeテーブルに情報を追加する
        このテーブルに関するspecificな処理はこのクラスに集合させるという思想
        """
        list_rows_to_insert = list()
        created_at = dt.strftime(dt.now(), "%Y-%m-%d %H:%M:%S")
        for idx in range(20):
            if dict_input["distance"][idx] == 0:
                break
            else:
                list_to_insert = list()
                for key in dict_input.keys():
                    list_to_insert.append(dict_input[key][idx])
                # 各レコードに対して追加する
                list_to_insert.append(created_at)
                list_rows_to_insert.append(list_to_insert)
    
        if len(list_rows_to_insert) == 0:
            is_insert = False
        else:
            self.bqh.insert(list_rows_to_insert)
            is_insert = True
        return is_insert
    
    def delete(self, target_day, username):
        query_at = dt.now()
        deletable_from = query_at - datetime.timedelta(hours=1)
        str_deletable_from = dt.strftime(deletable_from, "%Y-%m-%d %H:%M:%S")
        query = f"""
        DELETE FROM `{self.bqh.dataset_name}.{self.bqh.table_name}`
        WHERE user = '{username}'
        AND
        day = '{target_day}'
        AND
        created_at < '{str_deletable_from}'
        """
        self.bqh.query(query)
        return


if __name__ == "__main__":
    PracticeTableHandler(create_table=True)