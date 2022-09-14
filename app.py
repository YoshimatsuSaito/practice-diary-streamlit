import os
import sys
import yaml

import streamlit as st
import streamlit_authenticator as stauth

from modules.practice_table_handler import PracticeTableHandler
from modules.users_table_handler import UsersTableHandler
from modules.authenticator_handler import AuthenticatorHandler
from modules.utils import read_config
from views.add_practice import add_practice
from views.show_practice import show_practice

current_dir = os.path.dirname(__file__)

# yamlで扱う場合：テスト用
# with open(os.path.join(current_dir, "../config.yaml")) as file:
#     config = yaml.load(file, Loader=yaml.SafeLoader)

# Usersテーブル操作用インスタンスを作成し、認証関連操作用インスタンスを作成する
uth = UsersTableHandler(create_table=False)
ah = AuthenticatorHandler(users_table_handler=uth)

# 各ページの準備
def logout_or_change_account_info():
    st.header("Logout")
    ah.logout()
    st.header("Change account info")
    ah.updateuserinfo()
    ah.resetpassword()

page_names_to_funcs = {
    "Add practice": add_practice,
    "See practice diary": show_practice,
    "Logout or Change account info": logout_or_change_account_info,
}

# ログインウィジェット
ah.login()
if ah.authentication_status is None:
    st.warning('Enter your Username/password')
    ah.forgetpassword()
    ah.forgetusername()
    ah.signup()
elif ah.authentication_status == False:
    st.error('Username/password is incorrect')
    ah.forgetpassword()
    ah.forgetusername()
    ah.signup()
elif ah.authentication_status == True:
    st.title(f"This is {ah.name}'s page")
    selected_page = st.radio("", page_names_to_funcs.keys())
    page_names_to_funcs[selected_page]()

