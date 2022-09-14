import os
import sys
import yaml

import streamlit as st
import streamlit_authenticator as stauth

current_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(current_dir, "../"))

from modules.practice_table_handler import PracticeTableHandler


class AuthenticatorHandler:
    """
    streamlit_authenticatorを用いてユーザアカウント周りの操作を行うクラス
    """
    def __init__(self, users_table_handler):
        self.config = users_table_handler.config
        self.authenticator = stauth.Authenticate(
            self.config["credentials"], self.config["cookie"]["name"],
            self.config["cookie"]["key"], self.config["cookie"]["expiry_days"],
            self.config["preauthorized"])
        self.name = None
        self.authentication_status = None
        self.username = None
        self.uth = users_table_handler

    def login(self):
        """
        ログイン画面（既にアカウント作成済みのユーザが使用）
        """
        # ログインメソッドで入力フォームを配置
        self.name, self.authentication_status, self.username = self.authenticator.login(
            "Login", "main")

    def logout(self):
        self.authenticator.logout("Logout", 'main')

    def updateuserinfo(self):
        """
        ユーザ情報更新
        """
        try:
            if self.authenticator.update_user_details(self.username,
                                                      "Update user details"):
                self.uth.update(self.config)
                st.success("Entries updated successfully")
        except Exception as e:
            st.error(e)

    def resetpassword(self):
        """
        パスワードリセット
        """
        try:
            if self.authenticator.reset_password(self.username,
                                                 "Reset password"):
                self.uth.update(self.config)
                st.success("Password modified successfully")
        except Exception as e:
            st.error(e)

    def signup(self):
        """
        アカウントの作成（アカウント未作成のユーザが使用）
        """
        try:
            if self.authenticator.register_user("Create Account",
                                                preauthorization=False):
                self.uth.update(self.config)
                st.success("User account created successfully")
        except Exception as e:
            st.error(e)

    def forgetpassword(self):
        """
        パスワード忘れ
        """
        try:
            username_forgot_pw, email_forgot_password, random_password = self.authenticator.forgot_password(
                "Forgot password")
            if username_forgot_pw:
                self.uth.update(self.config)
                st.success("New password sent securely")
                # Random password to be transferred to user securely
            elif username_forgot_pw == False:
                st.error("Username not found")
        except Exception as e:
            st.error(e)

    def forgetusername(self):
        """
        ユーザネーム忘れ
        """
        try:
            username_forgot_username, email_forgot_username = self.authenticator.forgot_username(
                "Forgot username")
            if username_forgot_username:
                st.success("Username sent securely")
                # Username to be transferred to user securely
            elif username_forgot_username == False:
                st.error("Email not found")
        except Exception as e:
            st.error(e)

    def delete(self, username):
        """
        usernameの使い回しを避ける実装をする必要があり、データ自体の永久削除はいずれにせよ認められない
        よって、ひとまず削除機能は実装しないことにする
        """
        # if st.button(
        #         "Delete your account ※The account created or edited over 30 minutes ago is deletable"
        # ):
        #     self.uth.delete(username=username)
        #     st.info("Sent delete command to db")
