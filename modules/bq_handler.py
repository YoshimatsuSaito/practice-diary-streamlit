from google.cloud import bigquery
from google.oauth2 import service_account
from google.cloud.exceptions import NotFound

class BigqueryHandler:
    """
    BigQueryに直接CRUDの指示を与えるためのクラス
    各テーブルの扱いの際、このクラスを基底クラス的に用いる
    """
    def __init__(self, service_account_info_path, dataset_name=None, table_name=None):
        self.credentials = credentials = service_account.Credentials.from_service_account_file(
            service_account_info_path)
        self.client = bigquery.Client(credentials=self.credentials,
                                 project=self.credentials.project_id)
        self.dataset_name = dataset_name
        self.table_name = table_name
        self.dataset_id = f"{self.credentials.project_id}.{self.dataset_name}"
        self.table_id = f"{self.dataset_id}.{self.table_name}"
    
    def create_dataset(self):
        """
        datasetの存在を確認し、存在しなければ作成する
        """
        try:
            self.client.get_dataset(self.dataset_id)  # Make an API request.
            print(f"Dataset {self.dataset_id} already exists")
        except NotFound:
            dataset = bigquery.Dataset(self.dataset_id)
            dataset.location = "US"
            self.client.create_dataset(dataset)
            print(f"Created dataset {self.dataset_id}")
    
    def create_table(self, schema):
        try:
            self.client.get_table(self.table_id)
            print(f"Table {self.table_id} already exists")
        except NotFound:
            table = bigquery.Table(self.table_id, schema=schema)
            table = self.client.create_table(table)
            print(f"Created table {self.table_id}")
    
    def read(self, query):
        result = self.client.query(query)
        df = result.to_dataframe()
        return df
    
    def insert(self, rows):
        table = self.client.get_table(self.table_id)
        errors = self.client.insert_rows(table, rows)
        if len(errors) == 0:
            print("New rows have been added.")
        else:
            print(errors)
        # rows_to_insert = [("2022-07-21", 200, 25.11), ("2022-07-21", 100, 12.26)] # 挿入形式のイメージ

    def query(self, query):
        """
        指定されたqueryを実行する
        SQLで実行可能な全てを指示することができる
        """
        self.client.query(query)