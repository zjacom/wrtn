# 뤼튼 캐릭터 크롤링

## 캐릭터 둘러보기에 있는 캐릭터를 카테고리 별로 크롤링합니다.
<img width="861" alt="스크린샷 2024-10-12 오후 6 58 02" src="https://github.com/user-attachments/assets/dee97da0-05b6-4f7a-a973-c7021a791d60">

## 실행 방법
1. 현재 디렉토리에서 `poetry lock` 실행
2. `docker compose up --build` 실행
    - 만약 다음과 같은 오류가 발생하면, 도커 재시작 후 `docker compose up` 실행
        - `failed to solve: Unavailable: error reading from server: EOF`
        - `request returned Internal Server Error for API route and version [특정 메시지], check if the server supports the requested API version`
3. [중요] 카테고리 별 수집할 캐릭터의 수를 지정할 수 있습니다.
    - `extract.py`에서 `limit` 값 수정
    - <img width="425" alt="스크린샷 2024-10-12 오후 7 03 52" src="https://github.com/user-attachments/assets/14fa75b3-95c6-47f1-b553-4a19c655409f">
4. 처음부터 다시 수집하고 싶다면, `done` 폴더와 `temp` 폴더를 비워주세요!

## 추가 안내
1. `docker-compose.yml` 파일을 빌드하는데, 15분~20분 정도 소요됩니다.
2. 카테고리 별 캐릭터 수에 제한을 설정하지 않으면, 상당한 시간이 소요됩니다.
    - 뤼튼은 가상 스크롤링으로 컨텐츠를 동적 렌더링하고 있습니다.
    - 따라서 웹 페이지를 스크롤 다운할 때마다, 부하가 발생합니다.
3. 데이터를 빠르고 신뢰성있게 가져오려면, `test.py`에 존재하는 `fetch_data` 함수와 `using_api` 함수를 활용하세요!
    - 두 함수는 API를 사용합니다.
4. 데이터는 MySQL `test_db` 데이터베이스에 저장됩니다.
    - MySQL 접속 명령어: `mysql -h 127.0.0.1 -P 3307 -u root -p`
    - MySQL 비밀번호: `password`
    - 테이블 정보 및 관계
    <img width="552" alt="스크린샷 2024-10-12 오후 8 24 22" src="https://github.com/user-attachments/assets/c3645188-0ecc-44e9-8fe5-fd7cd1f0bb46">