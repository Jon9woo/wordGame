# word_game.py
# 단어 맞추기 게임

import os
import pymysql
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수에서 값 가져오기
HOST = os.getenv('HOST')
PORT = int(os.getenv('PORT'))
USER = os.getenv('DB_USER')
PASSWD = os.getenv('PASSWD')
DB = os.getenv('DB')

import pyglet
from random import randint
import time

# words 불러와서 저장하는 함수 파일을 인자로 받음
def wordLoad(file):
    with open(file, 'r') as f:
        words = f.readlines()
        words = [word.strip() for word in words]
    return words

# 게임을 실행하는 함수
def gameRun(words):
    # 게임 소요 시간 측정
    start_time = time.time()  # 시작 시간 기록
    wrong_count = 0
    i = 0
    while True:
        i+=1
        if i > 5:
            break
        sample = words[randint(0, len(words))] 
        print(sample)
        input_word = input()
        if sample == input_word:
            correct_music = pyglet.resource.media('assets/good.wav')
            correct_music.play()
        else:
            wrong_count += 1
            player_wrong = pyglet.media.Player()
            wrong_music = pyglet.resource.media('assets/bad.wav')
            wrong_music.play()
    
    end_time = time.time()  # 끝 시간 기록

    if wrong_count > 2:
        print("맞춘 개수는:", 5-wrong_count)
        print("소요시간은:", end_time - start_time)
        print('Game Over')
    else:
        print("맞춘 개수는:", 5-wrong_count)
        print("소요시간은:", end_time - start_time)
        print('Game Clear')

    return 5-wrong_count, round(end_time - start_time, 3)


# DB연결하고 순위 저장하는 함수
def save_game_result(corr_cnt, exe_time):
    conn = pymysql.connect(host=HOST, port=PORT, user=USER, passwd=PASSWD, db=DB)
    cursor = conn.cursor()
    
    # 새 게임 결과를 테이블에 삽입
    insert_query = """
    INSERT INTO wordgame (corr_cnt, exe_time, reg_date)
    VALUES (%s, %s, %s)
    """
    reg_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    cursor.execute(insert_query, (corr_cnt, exe_time, reg_date))
    conn.commit()

    # 삽입된 마지막 게임 결과의 id 가져오기
    last_game_id = cursor.lastrowid
    
    # 모든 데이터 가져와서 정렬
    select_query = "SELECT id, corr_cnt, exe_time FROM wordgame ORDER BY corr_cnt DESC, exe_time ASC"
    cursor.execute(select_query)
    results = cursor.fetchall()
    
    # 등수 매기기 및 업데이트
    rank = 1
    for result in results:
        update_query = "UPDATE wordgame SET irank = %s WHERE id = %s"
        cursor.execute(update_query, (rank, result[0]))
        rank += 1
    
    conn.commit()
    cursor.close()
    conn.close()

    return last_game_id

# 순위 출력 함수
def print_rankings(last_game_id):
    conn = pymysql.connect(host=HOST, port=PORT, user=USER, passwd=PASSWD, db=DB)
    cursor = conn.cursor()
    
    # 상위 3개의 기록 가져오기
    cursor.execute("SELECT id, corr_cnt, exe_time, reg_date, irank FROM wordgame ORDER BY irank ASC LIMIT 3")
    top3_results = cursor.fetchall()
    
    # 마지막 게임 기록 가져오기
    cursor.execute("SELECT id, corr_cnt, exe_time, reg_date, irank FROM wordgame WHERE id = %s", (last_game_id,))
    last_game_result = cursor.fetchone()
    
    print("========== 역대 순위 (Top 3) =============")
    print(f"{'ID':<2} {'맞춘갯수':<3} {'걸린시간':<8} {'등록날짜':<8} {'등수':<5}")
    for result in top3_results:
        print(result)
    
    print("\n========== 마지막 게임 결과 =============")
    print(f"{'ID':<2} {'맞춘갯수':<3} {'걸린시간':<8} {'등록날짜':<8} {'등수':<5}")
    print(last_game_result)
    
    cursor.close()
    conn.close()


if __name__ == '__main__':
    words = wordLoad('/Users/jongwoom1pro/Coding/개인프로젝트/word_game_problem/data/word.txt')
    correct_count, exe_time = gameRun(words)
    last_game_id = save_game_result(correct_count, exe_time)
    print_rankings(last_game_id)

