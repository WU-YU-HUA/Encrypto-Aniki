from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time

def get_info(url):
    opt = Options()
    opt.add_argument("--headless")  # 啟用無頭模式
    opt.add_argument("--disable-gpu")  # 禁用 GPU，加快處理速度（可選）
    driver = webdriver.Chrome(options=opt)
    driver.get(url)
    wait = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="Overview_defiItem__1e5s9"]/div[1]/div[2]/div[2]/span'))
    )

    show_all = driver.find_element(By.XPATH, '//*[@id="Overview_defiItem__1e5s9"]/div[1]/div[2]/div[2]/span')
    show_all.click()
    time.sleep(20)
    rows = driver.find_elements(By.CLASS_NAME, "db-table-wrappedRow")
    token_amount = dict()
    for row in rows:
        info = row.text.split('\n')
        token = info[0]
        price = info[1]
        amount = info[2]
        value = info[3]
        token_amount[token] = str(amount)
    driver.quit()
    # token_amount = dict(sorted(token_amount.items()))
    return token_amount

def save_to_csv(data: dict, path):
    df = pd.DataFrame([data])
    df.to_csv(path, index=False, encoding='utf-8')

def compare_csv_data(data: dict, path, name):
    df = pd.read_csv(path, index_col=False)
    text_list = []
    text_list.append(f'<p style="font-size: 16px;"><b>{name}</b></p>')
    for key, value in data.items(): #Find Amount-Changing
        if key in df.columns:
            if str(df[key][0]) != value:
                text = f"<p><b>{key}</b> amount is changed: Origin-> {df[key][0]} ， New-> {value}</p>"
                text_list.append(text)
    
    #Find New or Sold
    ori_key = set(df.columns)
    new_key = set(data.keys())
    if ori_key != new_key:
        text_list.append("<p><b>Buy:</b></p>")
        boughts = sorted(new_key - ori_key)
        for bought in boughts:
            text_list.append(f"<p>{bought}: {data[bought]}</p>")

        text_list.append("<p><b>Sell:</b></p>")
        sold = sorted(ori_key - new_key)
        for sell in sold:
            text_list.append(f"<p>{sell}: {df[sell][0]}</p>")

    if len(text_list) != 1:
        send_mail(text_list)

def send_mail(text: list):
    message_body = "\n".join(text)
    sender_email = "a0973350996@gmail.com"
    receiver = "a0973350996@gmail.com"
    subject = "Encrypto AniKi"

    msg = MIMEMultipart("alternative")
    msg['From'] = sender_email
    msg['To'] = receiver
    msg['Subject'] = subject
    html_content = MIMEText(message_body, "html")
    msg.attach(html_content)
    try:
        # 配置 SMTP 伺服器，這裡使用 Gmail 為例
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # 開始 TLS 加密
        server.login(sender_email, 'abfy jvva qtjv nvpk')  # 用發件人郵箱的密碼登錄

        # 發送郵件
        server.sendmail(sender_email, receiver, msg.as_string())
        print("郵件發送成功！")

    except Exception as e:
        print(f"郵件發送失敗: {e}")

    finally:
        server.quit()  # 關閉 SMTP 伺服器連接

url = 'https://debank.com/profile/0x28a55c4b4f9615fde3cdaddf6cc01fcf2e38a6b0?chain=eth'
url2 = ' https://debank.com/profile/0x741aa7cfb2c7bf2a1e7d4da2e3df6a56ca4131f3?chain=eth'

account1 = get_info(url)
account2 = get_info(url2)
compare_csv_data(account1, 'account1.csv', "Account1")
compare_csv_data(account2, 'account2.csv', "Account2")
save_to_csv(account1, 'account1.csv')
save_to_csv(account2, 'account2.csv')