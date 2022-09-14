import datetime
import os
import sys
from datetime import datetime as dt

import streamlit as st
from google.cloud import bigquery

current_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(current_dir, "../"))

from modules.bq_handler import BigqueryHandler
from modules.utils import read_config

current_dir = os.path.dirname(__file__)

class UsersTableHandler:
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
        table_name = config_dict["users_table_name"]
        self.bqh = BigqueryHandler(service_account_info_path=service_account_info_path,
                              dataset_name=dataset_name,
                              table_name=table_name)
        
        # このスクリプトがmainで使用されるとき、create_table=Trueでテーブル自体のCREATEを行う
        if create_table:
            # テーブル作成
            schema = [
                bigquery.SchemaField("usernames", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("email", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("password", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("created_at", "DATETIME", mode="REQUIRED")
            ]
            self.bqh.create_table(schema)
        
        self.get_status(update_self=True)
    
    def read(self):
        """
        DBの登録情報を読み込む
        その際、ユーザ毎にcreated_atが最新のもののみを読み込む
        """
        query = f"""
        WITH TMP1 AS (
          SELECT usernames, MAX(created_at) AS created_at
          FROM `{self.bqh.dataset_name}.{self.bqh.table_name}`
          GROUP BY usernames
        )
        SELECT TMP2.usernames, TMP2.email, TMP2.name, TMP2.password, TMP2.created_at
        FROM `{self.bqh.dataset_name}.{self.bqh.table_name}` AS TMP2
        RIGHT JOIN TMP1
        ON TMP1.usernames = TMP2.usernames
        AND TMP1.created_at = TMP2.created_at
        """
        df = self.bqh.read(query)
        return df
    
    def cvt_to_authenticator_format(self, df):
        """
        DBの内容をstreamlit_authenticatorのconfigの形式に変換する
        """
        config = {
            "credentials":{
                    "usernames": {
                    }
            },
            "cookie":{
                "expiry_days":30,
                "key": "some_signature_key",
                "name": "some_cookie_name"
            },
            "preauthorized":{
                "emails":[]
            }
        }
        for idx in df.index:
            username = df.at[idx, "usernames"]
            email = df.at[idx, "email"]
            name = df.at[idx, "name"]
            password = df.at[idx, "password"]
            config["credentials"]["usernames"][username] = dict()
            config["credentials"]["usernames"][username]["email"] = email
            config["credentials"]["usernames"][username]["name"] = name
            config["credentials"]["usernames"][username]["password"] = password
        return config
    
    def update(self, config):
        """
        アカウント情報はどのような変更であれ、streamlit_authenticatorによるconfigのdictの更新の形で行われる
        その時点でのDBの状態と差分が発生したusernamesの情報のみ改めてinsertする
        """
        # 現DBの情報を取得する
        config_original = self.get_status(update_self=False)
        list_update_rows = list()
        for username in config["credentials"]["usernames"].keys():
            # 更新（の可能性がある）情報を取り出す
            email = config["credentials"]["usernames"][username]["email"]
            name = config["credentials"]["usernames"][username]["name"]
            password = config["credentials"]["usernames"][username]["password"]
            created_at = dt.strftime(dt.now(), "%Y-%m-%d %H:%M:%S")
            # 新規ユーザ情報ではない場合、旧情報から更新があるかどうかを比べる
            if username in config_original["credentials"]["usernames"].keys():
                email_original = config_original["credentials"]["usernames"][username]["email"]
                name_original = config_original["credentials"]["usernames"][username]["name"]
                password_original = config_original["credentials"]["usernames"][username]["password"]
                if (email != email_original) or (name != name_original) or (password != password_original):
                    list_update_rows.append([username, email, name, password, created_at])
                else:
                    pass
            # 新規ユーザ情報であれば、追加する
            else:
                list_update_rows.append([username, email, name, password, created_at, 0])
        
        # 更新
        if len(list_update_rows) > 0:
            # データ追加
            self.bqh.insert(list_update_rows)
            # 重複した同一ユーザのデータを削除（streaming buffer対策で、データ追加が1日前までの場合）
            self.delete_duplicates()
            # 内部状態更新
            self.get_status(update_self=True)
            return
        else:
            pass
    
    def delete_duplicates(self):
        """
        同一ユーザの重複したアカウント情報を削除する
        現状ではupdateがなされたときにしか実行されない（定期実行されるわけではない）ので、
        updateがなされない場合は重複したデータはusersテーブルに残り続ける
        """
        query_at = dt.now()
        deletable_from = query_at - datetime.timedelta(hours=1)
        str_deletable_from = dt.strftime(deletable_from, "%Y-%m-%d %H:%M:%S")
        query = f"""DELETE FROM `{self.bqh.dataset_name}.{self.bqh.table_name}`
            WHERE STRUCT(usernames, created_at) NOT IN (
              SELECT AS STRUCT usernames, MAX(created_at)
              FROM `{self.bqh.dataset_name}.{self.bqh.table_name}` 
              GROUP BY usernames
            ) 
            AND
            created_at < '{str_deletable_from}'
            """
        self.bqh.query(query)
        return

    def get_status(self, update_self=True):
        """
        現状のDBの情報を読み込む
        update_self=Trueのとき、インスタンス変数を更新する
        """
        if update_self:
            self.df = self.read()
            self.config = self.cvt_to_authenticator_format(self.df)
        else:
            df = self.read()
            config = self.cvt_to_authenticator_format(df)
            return config

if __name__ == "__main__":
    UsersTableHandler(create_table=True)