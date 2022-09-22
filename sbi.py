"""app/lambda_function.py
"""
import os
import time
import datetime
import gspread
import json

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
# ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成します。
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()


def lambda_handler(event, context):
    """lambda_handler
    """
    print('event: {}'.format(event))
    print('context: {}'.format(context))

    # headless_chromium = os.getenv('HEADLESS_CHROMIUM', '')
    chromedriver = os.environ['CHROMEDRIVER']
    user_name = os.environ['USERNAME']
    password = os.environ['PASSWORD']

    print('env取得')

    options = Options()
    # options.binary_location = headless_chromium
    # options.add_argument('--headless')
    # options.add_argument('--no-sandbox')
    # options.add_argument('--single-process')
    # options.add_argument('--disable-dev-shm-usage')

    print('option設定')

    driver = webdriver.Chrome(
        executable_path=chromedriver, options=options)
    print('SBI証券開く直前')
    driver.get('https://www.sbisec.co.jp/ETGate/')
    time.sleep(4)

    print('ログイン画面表示')
    # ユーザーIDとパスワード
    input_user_id = driver.find_element_by_name('user_id')
    input_user_id.send_keys(user_name)
    input_user_password = driver.find_element_by_name('user_password')
    input_user_password.send_keys(password)

    # ログインボタンをクリック
    driver.find_element_by_name('ACT_login').click()

    print('ログイン成功')

    # 遷移するまで待つ
    time.sleep(4)

    # ポートフォリオの画面に遷移
    driver.find_element_by_link_text('口座管理').click()

    # 遷移するまで待つ
    time.sleep(4)

    print('移動完了')

    # 文字コードをUTF-8に変換
    html = driver.page_source.encode('utf-8')

    # BeautifulSoupでパース
    soup = BeautifulSoup(html, "html.parser")

    # 株式
    table_data = soup.find('table', border="0",
                           cellspacing="1", cellpadding="1", width="400")
    valuation_gains = table_data.find_all(
        'tr', align="right", bgcolor="#eaf4e8")

    result = []
    today = datetime.date.today().strftime('%Y年%m月%d日')
    result.append(today)

    for element in valuation_gains:
        text = element.find('font', color="red").text
        text = text.replace('+', '')
        result.append(text)

    driver.close()
    driver.quit()

    print('ブラウザ閉じた')

    sbi_spreadsheet = os.environ['SBI_SPREADSHEET', '']
    SPREADSHEET_KEY = os.environ['SPREADSHEET_KEY', '']

    # 2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    # 認証情報設定
    # ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        sbi_spreadsheet, scope)

    # OAuth2の資格情報を使用してGoogle APIにログインします。
    gc = gspread.authorize(credentials)

    # 共有設定したスプレッドシートのシート1を開く
    worksheet = gc.open_by_key(SPREADSHEET_KEY).sheet1
    worksheet.append_row(result, value_input_option='USER_ENTERED')

    print('complete')
    return {'status': 200}


if __name__ == '__main__':
    print(lambda_handler(event=None, context=None))
