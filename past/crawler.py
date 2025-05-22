import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pdb as pdb
import time
import os
import random


def get_players_id():
    # 크롤링 대상 URL
    pitcher_url_2024 = 'http://statiz.sporki.com/stats/?m=main&m2=pitching&m3=default&so=&ob=&year=2024&sy=&ey=&te=&po=&lt=10100&reg=C3&pe=&ds=&de=&we=&hr=&ha=&ct=&st=&vp=&bo=&pt=&pp=&ii=&vc=&um=&oo=&rr=&sc=&bc=&ba=&li=&as=&ae=&pl=&gc=&lr=&pr=1000&ph=&hs=&us=&na=&ls=0&sf1=G&sk1=&sv1=&sf2=G&sk2=&sv2='
    batter_url_2024 = 'https://statiz.sporki.com/stats/?m=main&m2=batting&m3=default&so=&ob=&year=2024&sy=&ey=&te=&po=&lt=10100&reg=C5&pe=&ds=&de=&we=&hr=&ha=&ct=&st=&vp=&bo=&pt=&pp=&ii=&vc=&um=&oo=&rr=&sc=&bc=&ba=&li=&as=&ae=&pl=&gc=&lr=&pr=1000&ph=&hs=&us=&na=&ls=0&sf1=G&sk1=&sv1=&sf2=G&sk2=&sv2='

    url = pitcher_url_2024

    # User-Agent를 넣지 않으면 차단될 가능성 있음
    headers = {
        #'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4_1) AppleWebKit/605.1.15 Version/16.4 Safari/605.1.15"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 결과 저장용 리스트
    players = []

    # 선수 목록이 담긴 table 찾기
    table = soup.find('div', class_='table_type01')  # 외곽 div
    rows = table.find_all('tr')

    for row in rows:
        a_tag = row.find('a', href=True)
        if a_tag and '/player/' in a_tag['href']:
            name = a_tag.text.strip()
            href = a_tag['href'].strip()
            # 예: "/player/?m=playerinfo&p_no=16313"
            player_id = href.split('p_no=')[-1]
            players.append({'name': name, 'player_id': player_id})

    # CSV로 저장
    df = pd.DataFrame(players)
    df.to_csv('pitcher_player_ids.csv', index=False, encoding='utf-8-sig')
    print("✅ 크롤링 완료! pitcher_player_ids.csv로 저장됨")



def get_match_result():
    save_path = "all_pitcher_vs_batter_stats.csv"
    first_write = not os.path.exists(save_path)

    # Chrome 우회 설정
    options = Options()
    options.add_argument('--headless')  # 실제 브라우저 보고 싶다면 주석 처리
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/124.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # ChromeDriver 실행
    driver = webdriver.Chrome(options=options)
    pitcher_df = pd.read_csv("pitcher_player_ids.csv")

    # for idx, pitcher_id in enumerate(pitcher_df["player_id"]):
    start_idx = 77
    for idx, pitcher_id in enumerate(pitcher_df["player_id"].iloc[start_idx:], start=start_idx):
        try:
            url = f'https://statiz.sporki.com/player/?m=rival&p_no={pitcher_id}&pos=pitching&year=2024'
            driver.get(url)

            # ⏳ 사람처럼 랜덤한 시간 대기
            delay = random.uniform(5, 10.0)
            print(f"[{idx+1}/{len(pitcher_df)}] ⏱ Waiting {delay:.2f}s for pitcher_id={pitcher_id}") ## 77번까지 완료
            time.sleep(delay)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            table = soup.find('table')
            if not table:
                print(f"⚠ 테이블 없음: pitcher_id={pitcher_id}")
                continue

            header_row = table.find('tr')
            headers = [th.text.strip() for th in header_row.find_all('th')]

            rows = []
            for tr in table.find_all('tr')[1:]:
                cols = [td.text.strip() for td in tr.find_all('td')]

                a_tag = tr.find('a', href=True)
                if a_tag and 'p_no=' in a_tag['href']:
                    batter_id = a_tag['href'].split('p_no=')[-1].strip()
                    cols[0] = batter_id

                if len(cols) == len(headers):
                    rows.append(cols)

            if not rows:
                print(f"⚠ 데이터 없음: pitcher_id={pitcher_id}")
                continue

            df = pd.DataFrame(rows, columns=headers)
            df.rename(columns={"상대": "Batter_id"}, inplace=True)
            df["Pitcher_id"] = pitcher_id
            df = df[["Pitcher_id", "Batter_id"] + [col for col in df.columns if col not in ["Pitcher_id", "Batter_id"]]]

            df.to_csv(save_path, mode='a', index=False, header=first_write, encoding='utf-8-sig')
            first_write = False
            print(f"✅ 저장 완료: pitcher_id={pitcher_id} ({len(df)} rows)")

        except Exception as e:
            print(f"❌ 에러 발생: pitcher_id={pitcher_id}, {e}")
            continue

    driver.quit()
    print("🎉 전체 크롤링 종료")




if __name__ == "__main__":
    get_match_result()
    
