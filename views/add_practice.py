import datetime
import os
import sys
from collections import OrderedDict

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


def add_practice():
    """
    各日の練習内容の入力を受け付け、bigqueryに登録する
    bqh: BigqueryHandler
    """
    # bigqueryとの接続
    pth = PracticeTableHandler()
    
    if st.session_state["authentication_status"]:
        st.header("Add practice")
        # 便宜上最大10本までの練習を登録できることとする
        n_max_practice = 10
        list_distance = list(range(0, 300, 50)) + list(range(300, 2500, 100)) + list(range(3000, 11000, 1000))
        list_minutes = [None] + list(range(0, 21, 1))
        list_restway = ["walk", "jog", "duration", None]
        
        year_today, month_today, day_today = get_today()
        day = st.date_input("Practice day", datetime.date(year_today, month_today, day_today))
        str_day = day.strftime("%Y-%m-%d")
        
        # 後にテーブルにinsertする際の順序保持のためにordereddictで定義
        dict_input = OrderedDict()
        dict_input["day"] = [str_day]*n_max_practice
        dict_input["order_menu"] = range(1, n_max_practice+1)
        dict_input["distance"] = [0]*n_max_practice
        dict_input["sec"] = [0]*n_max_practice
        dict_input["rest_meter"] = [0]*n_max_practice
        dict_input["rest_minutes"] = [0]*n_max_practice
        dict_input["rest_way"] = [None]*n_max_practice
        dict_input["user"] = [st.session_state["username"]]*n_max_practice
        
        # 最大10本のメニューを登録
        for i in range(0, n_max_practice):
            # 本メニュー
            cols_menu = st.columns(5)
            with cols_menu[0]:
                st.subheader(f"{i+1}")
            with cols_menu[1]:
                dict_input["distance"][i] = st.selectbox(f"meter", list_distance, index=list_distance.index(0), key=i)
            with cols_menu[2]:
                dict_input["sec"][i] = st.number_input(f"sec", 0.0, 600.0, 0.0, key=i)
            with cols_menu[3]:
                dict_input["rest_way"][i] = st.selectbox(f"rest", list_restway, list_restway.index(None), key=i)
            if dict_input["rest_way"][i] in ["walk", "jog"]:
                with cols_menu[4]:
                    dict_input["rest_meter"][i] = st.selectbox(f"meter (rest)", list_distance, index=list_distance.index(0), key=i)
            elif dict_input["rest_way"][i] == "duration":
                with cols_menu[4]:
                    dict_input["rest_minutes"][i] = st.selectbox(f"minutes (rest)", list_minutes, list_minutes.index(None), key=i)
            st.markdown("---")
    
        # 結果の登録
        cols_tmp = st.columns(3)
        with cols_tmp[1]:
            if st.button("Submit"):
                is_insert = pth.insert(dict_input)
                if is_insert:
                    st.info("Inserted data")
                else:
                    st.warning("Nothing to insert")
    else:
        st.warning('You have to login')
    
