import time
import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

def lambda_handler(event, context):
    options = Options()
    # options.add_argument('--headless')
    print('option設定')

    driver = webdriver.Chrome(executable_path='../../chromedriver', options=options)
    print('ブラウザを開く直前')

    driver.get('https://www.sbisec.co.jp/ETGate/')
    # 遷移するまで待つ
    time.sleep(4)
    print('ログイン画面表示')

    # ユーザーIDとパスワード
    input_user_id = driver.find_element_by_name('user_id')
    input_user_id.send_keys('ruymtnw')
    input_user_password = driver.find_element_by_name('user_password')
    input_user_password.send_keys('conan4869')

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
    table_data = soup.find('table', border="0", cellspacing="1", cellpadding="1", width="400")
    valuation_gains = table_data.find_all('tr', align="right", bgcolor="#eaf4e8")
    
    result = []
    today = datetime.date.today().strftime('%Y年%m月%d日')
    result.append(today)
    
    for element in valuation_gains:
      text = element.find('font', color="red").text
      text = text.replace('+', '')
      result.append(int(text))
    print(result)

    driver.close()
    driver.quit()
    print('ブラウザ閉じた')
    
if __name__ == '__main__':
    print(lambda_handler(event=None, context=None))