import os
import mysql.connector

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

    # character_category 테이블 생성
    cur.execute("""
        CREATE TABLE IF NOT EXISTS character_category (
            id INT AUTO_INCREMENT PRIMARY KEY,
            category_name VARCHAR(255) NOT NULL
        );
    """)
    
    cur.execute("DROP TABLE IF EXISTS character_info")

    # character_info 테이블 생성
    cur.execute("""
    CREATE TABLE IF NOT EXISTS character_info (
        id INT AUTO_INCREMENT UNIQUE,
        character_name VARCHAR(255) NOT NULL,
        character_description TEXT,
        character_image LONGBLOB,
        character_first_message TEXT,
        character_author VARCHAR(255) NOT NULL,
        category_id INT,
        PRIMARY KEY (character_name, character_author),
        FOREIGN KEY (category_id) REFERENCES character_category(id)
        );
    """)


    # 카테고리 데이터 삽입
    categories = [
        "로맨스", "애니메이션/만화", "엔터테인먼트/연예",
        "업무/생산성", "게임", "교육", "유머", "생활", "영화/드라마", "기타"
    ]
    
    # 혹시나 있을 기존 데이터를 삭제
    cur.execute("DELETE FROM character_category;")

    cur.executemany(
        "INSERT INTO character_category (category_name) VALUES (%s);",
        [(category,) for category in categories]
    )

    conn.commit()
    print("테이블 생성 및 데이터 삽입 완료!")

    cur.close()
    conn.close()

    # 플래그 파일 생성
    with open("/done/init_done", "w") as f:
        f.write("init done")

if __name__ == "__main__":
    main()
