import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pdb as pdb
import time
import os
import random


#1. 2024년 투수 ID Crawling
def get_pitcher_id():
    # 크롤링 대상 URL
    pitcher_url_2024 = 'http://statiz.sporki.com/stats/?m=main&m2=pitching&m3=default&so=&ob=&year=2024&sy=&ey=&te=&po=&lt=10100&reg=C3&pe=&ds=&de=&we=&hr=&ha=&ct=&st=&vp=&bo=&pt=&pp=&ii=&vc=&um=&oo=&rr=&sc=&bc=&ba=&li=&as=&ae=&pl=&gc=&lr=&pr=1000&ph=&hs=&us=&na=&ls=0&sf1=G&sk1=&sv1=&sf2=G&sk2=&sv2='

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



#2. 2024년 타자 ID Crawling
def get_batter_id():
    # 크롤링 대상 URL
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
    df.to_csv('batter_player_ids.csv', index=False, encoding='utf-8-sig')
    print("✅ 크롤링 완료! pitcher_player_ids.csv로 저장됨")





#3. 투수 ID 기준으로, Matchup 기록 크롤링
def get_match_result():
    save_path = "all_pitcher_vs_batter_stats.csv"
    first_write = not os.path.exists(save_path)

    options = Options()

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4_1) AppleWebKit/605.1.15 Version/16.4 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/113.0.0.0 Safari/537.36"
    ]
    ua = random.choice(USER_AGENTS)
    options.add_argument(f"user-agent={ua}")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # 드라이버 실행
    driver = webdriver.Chrome(options=options)

    # webdriver 감지 우회
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
        """
    })

    pitcher_df = pd.read_csv("pitcher_player_ids.csv")

    for idx, pitcher_id in enumerate(pitcher_df["player_id"]):
        try:
            # 매 루프마다 User-Agent 변경
            ua = random.choice(USER_AGENTS)
            driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": ua})

            url = f'https://statiz.sporki.com/player/?m=rival&p_no={pitcher_id}&pos=pitching&year=2024'
            driver.get(url)

            # 랜덤 대기 시간 (6~12초)
            delay = random.uniform(6, 12)
            print(f"[{idx+1}/{len(pitcher_df)}] ⏱ Waiting {delay:.2f}s for pitcher_id={pitcher_id}")
            time.sleep(delay)

            # 30명마다 쿨다운
            if idx != 0 and idx % 30 == 0:
                cooldown = random.uniform(30, 60)
                print(f"🧊 Cooldown for {cooldown:.2f}s")
                time.sleep(cooldown)

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



#4. 투수의 손잡이 크롤링
def get_pitch_type_info():
    save_path = "pitch_pitching_type.csv"
    first_write = not os.path.exists(save_path)

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4_1) AppleWebKit/605.1.15 Version/16.4 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/113.0.0.0 Safari/537.36"
    ]

    # Selenium Options
    options = Options()
    ua = random.choice(USER_AGENTS)
    options.add_argument(f"user-agent={ua}")
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    
    pitcher_df = pd.read_csv("pitcher_player_ids.csv")
    
    # start_idx = 147
    # for idx, pitcher_id in enumerate(pitcher_df["player_id"].iloc[start_idx:], start=start_idx):
    for idx, pitcher_id in enumerate(pitcher_df["player_id"]):
        try:
            # 랜덤 User-Agent 변경 (매 루프마다 설정)
            ua = random.choice(USER_AGENTS)
            driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": ua})

            url = f"https://statiz.sporki.com/player/?m=playerinfo&p_no={pitcher_id}"
            driver.get(url)

            # 랜덤한 딜레이
            delay = random.uniform(6, 12)
            print(f"[{idx+1}/{len(pitcher_df)}] ⏱ Waiting {delay:.2f}s for pitcher_id={pitcher_id}")
            time.sleep(delay)

            # 쿨다운 시간: 30명마다 30~60초 대기
            if idx != 0 and idx % 30 == 0:
                cooldown = random.uniform(30, 60)
                print(f"🧊 Cooldown for {cooldown:.2f}s")
                time.sleep(cooldown)

            soup = BeautifulSoup(driver.page_source, "html.parser")

            pitch_type = None
            spans = soup.find_all("span")
            for span in spans:
                text = span.get_text(strip=True)
                if text in ["좌투좌타", "우투우타", "좌투우타", "우투좌타", "우투", "좌투", "우타", "좌타", "우투양타", "좌투양타", "우언좌타", "좌언좌타", "우언우타", "우언좌타"]:
                    pitch_type = text
                    break

            result_row = {"player_id": pitcher_id, "pitch_type": pitch_type}
            df = pd.DataFrame([result_row])

            df.to_csv(save_path, mode='a', index=False, header=first_write, encoding="utf-8-sig")
            first_write = False

            if pitch_type:
                print(f"✅ 저장 완료: pitcher_id={pitcher_id} → {pitch_type}")
            else:
                print(f"⚠ 정보 없음: pitcher_id={pitcher_id}")

        except Exception as e:
            print(f"❌ 에러 발생: pitcher_id={pitcher_id}, {e}")
            continue

    driver.quit()
    print("🎉 전체 크롤링 종료")


#5. 타자의 손잡이 크롤링
def get_batter_type_info():
    save_path = "batter_batting_type.csv"
    first_write = not os.path.exists(save_path)

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4_1) AppleWebKit/605.1.15 Version/16.4 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/113.0.0.0 Safari/537.36"
    ]

    # Selenium Options
    options = Options()
    ua = random.choice(USER_AGENTS)
    options.add_argument(f"user-agent={ua}")
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    
    pitcher_df = pd.read_csv("batter_player_ids.csv")
    
    # start_idx = 147
    # for idx, pitcher_id in enumerate(pitcher_df["player_id"].iloc[start_idx:], start=start_idx):
    for idx, pitcher_id in enumerate(pitcher_df["player_id"]):
        try:
            # 랜덤 User-Agent 변경 (매 루프마다 설정)
            ua = random.choice(USER_AGENTS)
            driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": ua})

            url = f"https://statiz.sporki.com/player/?m=playerinfo&p_no={pitcher_id}"
            driver.get(url)

            # 랜덤한 딜레이
            delay = random.uniform(6, 12)
            print(f"[{idx+1}/{len(pitcher_df)}] ⏱ Waiting {delay:.2f}s for pitcher_id={pitcher_id}")
            time.sleep(delay)

            # 쿨다운 시간: 30명마다 30~60초 대기
            if idx != 0 and idx % 30 == 0:
                cooldown = random.uniform(30, 60)
                print(f"🧊 Cooldown for {cooldown:.2f}s")
                time.sleep(cooldown)

            soup = BeautifulSoup(driver.page_source, "html.parser")

            pitch_type = None
            spans = soup.find_all("span")
            for span in spans:
                text = span.get_text(strip=True)
                if text in ["좌투좌타", "우투우타", "좌투우타", "우투좌타", "우투", "좌투", "우타", "좌타", "우투양타", "좌투양타", "우언좌타", "좌언좌타", "우언우타", "우언좌타"]:
                    pitch_type = text
                    break

            result_row = {"player_id": pitcher_id, "pitch_type": pitch_type}
            df = pd.DataFrame([result_row])

            df.to_csv(save_path, mode='a', index=False, header=first_write, encoding="utf-8-sig")
            first_write = False

            if pitch_type:
                print(f"✅ 저장 완료: pitcher_id={pitcher_id} → {pitch_type}")
            else:
                print(f"⚠ 정보 없음: pitcher_id={pitcher_id}")

        except Exception as e:
            print(f"❌ 에러 발생: pitcher_id={pitcher_id}, {e}")
            continue

    driver.quit()
    print("🎉 전체 크롤링 종료")



#6. 2024년 심화 타자 지표 추출
def get_batter_info_2():
    url = "https://statiz.sporki.com/stats/?m=main&m2=batting&m3=deepen&so=&ob=&year=2024&reg=C5&lt=10100&pr=9999"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36"
    }

    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    columns = [
        "Rank", "Name", "Team", "Sort", "K%", "BB%", "BB/K", "BABIP", "IsoP", "IsoD", "R/ePA",
        "wOBA", "wRC", "RC27", "Own%", "wRC+"
    ]

    rows = []
    table = soup.find("table")

    for tr in table.find_all("tr")[2:]:  # 앞의 2줄은 헤더
        tds = tr.find_all("td")
        if len(tds) < len(columns):
            continue

        name = tds[1].text.strip()

        team_div = tds[2].find("div")
        team_spans = team_div.find_all("span")
        year = team_spans[0].text.strip()
        position = team_spans[2].text.strip()
        team_str = f"{year} {position}"

        row = [td.text.strip() for td in tds]
        row[1] = name
        row[2] = team_str
        rows.append(row[:len(columns)])

    df = pd.DataFrame(rows, columns=columns)

    for col in columns[3:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df.to_csv("statiz_2024_batting_deepen_full.csv", index=False, encoding='utf-8-sig')
    print(f"✅ 저장 완료: 총 {len(df)}명 → statiz_2024_batting_deepen_full.csv")
    return df



#7. 2024년 심화 투수 지표 추출
def get_pitcher_info_2():
    url = "https://statiz.sporki.com/stats/?m=main&m2=pitching&m3=deepen&year=2024&reg=C3&lt=10100&pr=9999"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36"
    }

    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table")

    # ✅ 컬럼 수동 정의 (제시된 HTML에 기반)
    columns = [
        "Rank", "Name", "Team", "Sort", "G", "K/9", "BB/9", "K/BB", "HR/9", "K%", "BB%", "K-BB%",
        "BABIP", "LOB", "ERA", "RA9", "rRA9", "rRA9pf", "FIP", "xFIP", "kwERA", "ERA-FIP",
        "ERA-", "rRA9-", "FIP-", "AVG", "OBP", "SLG", "OPS", "NP", "P/G", "P/IP", "P/PA"
    ]

    rows = []

    for tr in table.find_all("tr")[2:]:  # 첫 두 줄은 헤더
        tds = tr.find_all("td")
        if len(tds) < len(columns):
            continue

        name = tds[1].text.strip()

        # 팀 정보 조합: 연도 + 포지션 (예: "24 P")
        team_spans = tds[2].find_all("span")
        year = team_spans[0].text.strip()
        position = team_spans[2].text.strip()
        team_str = f"{year} {position}"

        row = [td.text.strip() for td in tds]
        row[1] = name
        row[2] = team_str
        rows.append(row[:len(columns)])

    df = pd.DataFrame(rows, columns=columns)

    # 숫자형 변환 (첫 4개 제외)
    for col in columns[3:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df.to_csv("statiz_2024_pitching_deepen.csv", index=False, encoding="utf-8-sig")
    print(f"✅ 저장 완료: 총 {len(df)}명 → statiz_2024_pitching_deepen.csv")
    return df




if __name__ == "__main__":
    get_batter_info()
    
