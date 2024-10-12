import requests
from collections import defaultdict
import mysql.connector
import os

# 환경 변수에서 MySQL 접속 정보 가져오기
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3307"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "password")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "test_db")

def fetch_data(url, visited, dic):
    response = requests.get(url)
    if response.status_code == 200:
        response_data = response.json()
        for character in response_data["data"]["characters"]:
            if character["_id"] not in visited:
                dic[character["categories"][0]["name"]] += 1
                visited.add(character["_id"])
        return response_data["data"]["nextCursor"]
    else:
        return None

# wrtn API를 사용하여 모든 캐릭터 정보 가져오는 함수
def using_api():
        url = "https://api.wrtn.ai/be/characters?limit=1000&sort=likeCount"
        character_count = defaultdict(int)
        visited = set()

        next_cursor = fetch_data(url, visited, character_count)

        # next_cursor가 있을 때까지 호출
        while next_cursor:
            next_url = f"https://api.wrtn.ai/be/characters?limit=500&cursor={next_cursor}&sort=likeCount"
            next_cursor = fetch_data(next_url, visited, character_count)

        total_character_count = sum([v for v in character_count.values()])
        
        return character_count, total_character_count

def main():
    # 카테고리 별 캐릭터의 수, 총 캐릭터 수
    character_count, total_character_count = using_api()

    # MySQL 데이터베이스 연결
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )
    cur = conn.cursor()

    # character_category 테이블의 NULL 값 및 데이터 확인
    cur.execute("SELECT * FROM character_category")
    categories = cur.fetchall()

    category_list = ["로맨스", "애니메이션/만화", "엔터테인먼트/연예", "업무/생산성", "게임", "교육", "유머", "생활", "영화/드라마", "기타"]

    for category in categories:
        id, name = category

        assert name is not None, f"ID가 {id}인, 카테고리 이름이 NULL입니다."
        assert name in category_list, f"{name} 카테고리는 뤼튼의 카테고리가 아닙니다."

    assert len(categories) == 10, f"카테고리 개수는 10개입니다. -> 테이블에 존재하는 카테고리 개수: {len(categories)}"

    cur.execute("SELECT * FROM character_info")
    characters = cur.fetchall()

    for character in characters:
        id, name, description, image, first_msg, author, category_id = character
        
        assert name is not None, f"ID가 {id}인, 캐릭터 이름이 NULL입니다."
        assert description is not None, f"ID가 {id}인, 캐릭터 설명이 NULL입니다."
        assert image is not None, f"ID가 {id}인, 캐릭터 썸네일이 NULL입니다."
        assert first_msg is not None, f"ID가 {id}인, 캐릭터 첫 메시지가 NULL입니다."
        assert author is not None, f"ID가 {id}인, 캐릭터 작성자가 NULL입니다."
        assert category_id is not None, f"ID가 {id}인, 캐릭터 카테고리가 NULL입니다."

        assert isinstance(name, str), f"ID가 {id}인, 캐릭터 이름이 NULL입니다."
        assert isinstance(description, str), f"ID가 {id}인, 캐릭터 설명이 NULL입니다."
        assert isinstance(image, bytes), f"ID가 {id}인, 캐릭터 썸네일이 NULL입니다."
        assert isinstance(first_msg, str), f"ID가 {id}인, 캐릭터 첫 메시지가 NULL입니다."
        assert isinstance(author, str), f"ID가 {id}인, 캐릭터 작성자가 NULL입니다."
        assert isinstance(category_id, int), f"ID가 {id}인, 캐릭터 카테고리가 NULL입니다."

    # 총 수집한 캐릭터 수 테스트
    try:
        assert len(characters) == total_character_count, f"전체 캐릭터의 수가 {total_character_count - len(characters)}개 부족합니다."
    except AssertionError as e:
        print(str(e))

    # 카테고리 별 캐릭터 수 테스트
    cur.execute("""
                SELECT ca.category_name, ch.cnt
                FROM (
                    SELECT category_id, count(*) cnt
                    FROM character_info
                    GROUP BY category_id
                ) ch
                INNER JOIN character_category ca ON ch.category_id = ca.id
                """)
    category_per_count = cur.fetchall()

    for info in category_per_count:
        category_name, count = info

        try:
            assert character_count[category_name] == count, f"{category_name} 카테고리의 캐릭터 수가 {character_count[category_name] - count}개 부족합니다."
        except AssertionError as e:
            print(str(e))

    print("테스트 완료!")
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
