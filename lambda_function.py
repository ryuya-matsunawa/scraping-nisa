"""app/lambda_function.py
"""
import os
import time
import datetime
import gspread
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
# ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成します。
from oauth2client.service_account import ServiceAccountCredentials

def lambda_handler(event, context):
    """lambda_handler
    """
    print('event: {}'.format(event))
    print('context: {}'.format(context))

    driver = connect_sbi()
    result = get_data_from_sbi(driver)
    save_to_spreadsheet(result)

def connect_sbi():
    headless_chromium = os.getenv('HEADLESS_CHROMIUM', '')
    chromedriver = os.getenv('CHROMEDRIVER', '')

    print('env取得')

    options = Options()
    options.binary_location = headless_chromium
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--single-process')
    options.add_argument('--disable-dev-shm-usage')

    print('option設定')

    driver = webdriver.Chrome(chromedriver, chrome_options=options)
    driver.get('https://www.sbisec.co.jp/ETGate/')

    return driver

def get_data_from_sbi(driver):
    user_name = os.getenv('USERNAME', '')
    password = os.getenv('PASSWORD', '')
    try:
        time.sleep(4)
        # ユーザーIDとパスワード
        input_user_id = driver.find_element_by_name('user_id')
        input_user_id.send_keys(user_name)
        input_user_password = driver.find_element_by_name('user_password')
        input_user_password.send_keys(password)

        # ログインボタンをクリック
        driver.find_element_by_name('ACT_login').click()

        # 遷移するまで待つ
        time.sleep(4)

        print('ここまではきたよ')

        count = len(driver.find_elements_by_link_text('口座管理'))
        if count == 0:
            # TODO: 確認必須のお知らせがあったらLINEに通知を送る
            print('お知らせあり')

        # ポートフォリオの画面に遷移
        driver.find_element_by_xpath('//*[@id="link02M"]/ul/li[3]/a/img').click()

        # 遷移するまで待つ
        time.sleep(4)

        # 文字コードをUTF-8に変換
        html = driver.page_source.encode('utf-8')

        # BeautifulSoupでパース
        soup = BeautifulSoup(html, "html.parser")

        # 株式
        table_data = soup.find('table', border="0", cellspacing="1", cellpadding="1", width="400")
        valuation_gains = table_data.find_all(
            'tr', align="right", bgcolor="#eaf4e8")

        result = []
        today = datetime.date.today().strftime('%Y年%m月%d日')
        result.append(today)

        for element in valuation_gains:
            text = element.find('font', color="red").text
            text = text.replace('+', '')
            result.append(text)
    except Exception as e:
        print(e)
    finally:
        driver.close()
        driver.quit()
        return result

def save_to_spreadsheet(result):
    sbi_spreadsheet_json = os.getenv('SBI_SPREADSHEET_JSON', '')
    spreadsheet_id = os.getenv('SPREADSHEET_ID', '')

    # 2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    # 認証情報設定
    # ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        sbi_spreadsheet_json, scope)

    # OAuth2の資格情報を使用してGoogle APIにログインします。
    gc = gspread.authorize(credentials)

    # 共有設定したスプレッドシートのシート1を開く
    worksheet = gc.open_by_key(spreadsheet_id).sheet1
    worksheet.append_row(result, value_input_option='USER_ENTERED')

    return { 'status': 204 }

if __name__ == '__main__':
    lambda_handler(event=None, context=None)
