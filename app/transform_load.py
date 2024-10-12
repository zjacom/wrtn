import json
import os
import mysql.connector
import requests

# 환경 변수에서 MySQL 접속 정보 가져오기
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3307"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "password")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "test_db")

def main():
    # MySQL 데이터베이스 연결
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )
    
    # 커서 생성
    cur = conn.cursor()

    # character_category 테이블의 모든 데이터를 조회하여 category_name을 기준으로 id를 매핑한 딕셔너리 생성
    cur.execute("SELECT id, category_name FROM character_category;")
    categories = cur.fetchall()
    category_dict = {name: id for id, name in categories}

    # 텍스트 파일을 읽어 각 줄을 JSON 객체로 변환하여 리스트로 저장
    characters = []
    with open("/temp/data.txt", "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                character = json.loads(line)
                characters.append(character)

    # 데이터 삽입
    count = 1
    for character in characters:
        character_name = character.get("character_name", "")
        character_description = character.get("character_description", "")
        character_first_message = character.get("character_first_message", "")
        character_author = character.get("author", "")
        category_name = character.get("category", "")

        # 이미지 URL을 BLOB 데이터로 변환
        image_url = character.get("character_image", "")
        response = requests.get(image_url)
        if response.status_code == 200:
            character_image = response.content
        else:
            print(f"다운로드 실패: {image_url}")
            character_image = None

        # category_name으로 category_id를 조회
        category_id = category_dict.get(category_name, None)
        if category_id is None:
            print(f"{category_id} 정보가 category_dict에 없습니다.")
            continue

        # character_info 테이블에 데이터 삽입
        insert_query = """
            INSERT IGNORE INTO character_info 
            (character_name, character_description, character_image, character_first_message, character_author, category_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        try:
            cur.execute(insert_query, (character_name, character_description, character_image, character_first_message, character_author, category_id))
            print(f"{count}개의 정보가 테이블에 적재되었습니다.")
            count += 1
        except mysql.connector.Error as e:
            print(f"적재 중 오류 발생: {e}")
    

    conn.commit()
    print("모든 데이터 적재 완료!")

    cur.close()
    conn.close()

    # 플래그 파일 생성
    with open("/done/load-done", "w") as f:
        f.write("load done!")

if __name__ == "__main__":
    main()
