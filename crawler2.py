import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pdb as pdb
import time
import os
import random


def get_batter_info_2():
    url = "https://statiz.sporki.com/stats/?m=main&m2=batting&m3=deepen&so=&ob=&year=2024&reg=C5&lt=10100"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # 표(table) 태그 추출
    table = soup.find("table")

    # 컬럼 이름 추출
    headers = [th.text.strip() for th in table.find_all("th")]

    # 데이터 행 추출
    rows = []
    for tr in table.find_all("tr")[1:]:
        cols = [td.text.strip() for td in tr.find_all("td")]
        if len(cols) == len(headers):  # 길이가 맞을 때만 추가
            rows.append(cols)

    # DataFrame 생성
    df = pd.DataFrame(rows, columns=headers)

    # 숫자형 컬럼은 변환
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except:
            continue

    # 저장
    df.to_csv("statiz_2024_batting_deepen.csv", index=False, encoding="utf-8-sig")
    print("✅ 저장 완료: statiz_2024_batting_deepen.csv")
    return df


if __name__ == "__main__":
    get_batter_info()
    


if __name__ == "__main__":
    get_batter_info_2()
    