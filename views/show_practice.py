import datetime
import os
import sys
from datetime import datetime as dt

import streamlit as st

current_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(current_dir, "../"))

from modules.practice_table_handler import PracticeTableHandler


def get_today():
    """
    練習日のデフォルトを取得してくるための便利関数
    """
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    dt = datetime.datetime.now(JST)
    return dt.year, dt.month, dt.day


def show_practice():
    """
    各日の練習内容の結果を確認する
    bqh: BigqueryHandler
    """
    # bigqueryとの接続
    pth = PracticeTableHandler()

    if st.session_state["authentication_status"]:
        st.header("Practice diary")
        # 結果を表示する期間を選ばせる
        year_today, month_today, day_today = get_today()
        # クエリを発行する期間を選択させる場合
        # day_start = st.date_input("From", datetime.date(2022, 1, 1))
        # day_end = st.date_input(
        #     "Until", datetime.date(year_today, month_today, day_today))
        day_start = datetime.date(2020, 1, 1)
        day_end = datetime.date(year_today, month_today, day_today)
        str_day_start = day_start.strftime("%Y-%m-%d")
        str_day_end = day_end.strftime("%Y-%m-%d")

        # 結果の取得
        df = pth.read(str_day_start, str_day_end, st.session_state["username"])
        if df is None or len(df) == 0:
            pass
        elif len(df) > 0:
            for day in df.day.unique():
                str_day = dt.strftime(day, "%Y-%m-%d")
                with st.expander(str_day):
                    df_target = df[df["day"] == day].reset_index(drop=True)
                    df_target.index = range(1, len(df_target) + 1)
                    df_target.drop(columns=["day", "order_menu"], inplace=True)
                    st.dataframe(df_target)
                    if st.button(
                            "Delete \r\n ※The records added over 1h ago are deleteble",
                            key=day):
                        pth.delete(target_day=str_day,
                                   username=st.session_state["username"])
                        st.info("Sent deleted command to db")
        elif len(df) == 0:
            st.warning("There is no data")
