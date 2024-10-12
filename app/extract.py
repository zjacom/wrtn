import asyncio
from playwright.async_api import async_playwright
import json
import aiofiles
import sys
import os

def create_index_tracking_file(idx):
    if os.path.exists(f"/temp/index{idx}.json"):
        return
    
    keys = [
        "로맨스", "애니메이션/만화", "엔터테인먼트/연예",
        "업무/생산성", "게임", "교육", "유머", "생활", "영화/드라마", "기타"
    ]

    data = {keys[idx - 1] : -1}

    print("생성된 딕셔너리:", data)

    with open(f"/temp/index{idx}.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    print(f"index{idx}.json 파일이 생성되었습니다.")


async def open_page(browser):
    while True:
        try:
            await page.close()
            page = await browser.new_page()
            await page.goto("https://wrtn.ai/character", wait_until="load")
            await page.wait_for_load_state("load")
            print("페이지를 새로 열었습니다.")
            break
        except:
            asyncio.sleep(1)
            pass
    return page

# 파일에 비동기적으로 JSON 객체 추가 함수 정의
async def append_json_to_file(file_name, data):
    async with aiofiles.open(file_name, 'a') as file:
        # 딕셔너리를 JSON 문자열로 변환하여 줄 단위로 추가
        await file.write(json.dumps(data) + "\n")

async def find_previous_idx(browser, page, category, data):
    """특정 카테고리에서 이전 index를 찾는 비동기 함수."""
    idx, path = 0, data[category]
    print(f"{category} 카테고리의 이전 idx 찾는중...")

    while True:
        try:
            while idx <= path:
                # 해당 index가 있는 요소를 찾아 스크롤
                await page.wait_for_selector(f'div[data-index="{idx + 1}"]', timeout=1000)
                scroll_div = await page.query_selector(f'div[data-index="{idx + 1}"]')
                await scroll_div.scroll_into_view_if_needed()
                idx += 1
            print(f"{category}의 이전 index {idx}를 찾았습니다.")
            return idx
        except:
            try:
                await page.wait_for_selector("#character-home-scroll")
                await page.evaluate("document.querySelector('#character-home-scroll').scrollBy(0, 500)")
            except:
                await open_page(browser)

# 비동기 함수 정의
async def crawling_character_info(num, limit):
    # Playwright 실행
    async with async_playwright() as p:
        # 크롬 브라우저 실행
        # browser = await p.chromium.launch(headless=True)
        browser = await p.chromium.launch_persistent_context(user_data_dir=f"/temp/playwright_data/session_{num}", headless=True)
        # context = await browser.new_context(ignore_https_errors=True)
        page = await browser.new_page()
        
        # 웹사이트 열기
        await page.goto("https://wrtn.ai/character")
        # 웹 페이지가 완전히 로드되었을 때까지 대기
        await page.wait_for_load_state('networkidle')

        await page.wait_for_selector("div.css-1fzkvcn")
        categories = await page.query_selector_all('div.css-1fzkvcn div')

        await categories[num].wait_for_element_state("visible")
        p_element = await categories[num].query_selector("p")
        category = await p_element.text_content()
        
        await categories[num].click()
        await page.wait_for_timeout(1000)

        # 캐릭터 둘러보기 요소 찾고 이동
        await page.wait_for_selector("div.css-1iaf8e")
        target_element = await page.query_selector("div.css-1iaf8e")
        if target_element:
            await target_element.scroll_into_view_if_needed()

        # 이전 idx 불러오기
        with open(f"/temp/index{num}.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        async def crawling():
            nonlocal page
            flag = True

            while flag:
                idx = await find_previous_idx(browser, page, category, data)
                while True:
                    try:
                        # idx 기준으로 스크롤 다운하고, 에러가 발생하면 한 번은 scrollBy로 스크롤 다운
                        try:
                            await page.wait_for_selector(f'div[data-index="{idx + 1}"]', timeout=1000)
                            scroll_div = await page.query_selector(f'div[data-index="{idx + 1}"]')
                            await scroll_div.scroll_into_view_if_needed()
                        except:
                            print("[CRASH X] scrollBy로 한번 더 스크롤 다운합니다.")
                            await page.wait_for_selector("#character-home-scroll")
                            await page.evaluate("document.querySelector('#character-home-scroll').scrollBy(0, 500)")

                        # 스크롤 다운된 페이지에서 탐색할 컨텐츠 찾기
                        await page.wait_for_selector(f'div[data-index="{idx}"]')
                        target_div = await page.query_selector(f'div[data-index="{idx}"]')

                        # 컨텐츠를 찾았다면 클릭 후 세부 페이지 로딩 대기
                        await target_div.click()
                        await page.wait_for_load_state("load")

                        # 세부 페이지에서 첫 번째 메시지 추출
                        await page.wait_for_selector('div.css-1ff969x')
                        content_area = await page.query_selector('div.css-1ff969x')
                        p_elements = await content_area.query_selector_all("p")
                        first_msg = " ".join([await p.text_content() for p in p_elements])

                        # 원래 페이지로 돌아가기
                        await page.go_back()

                        # 컨텐츠 정보 한 번 더 찾기
                        await page.wait_for_selector(f'div[data-index="{idx}"]')
                        target_div = await page.query_selector(f'div[data-index="{idx}"]')

                        # 캐릭터 이름, 설명, 썸네일, 작가 추출하기
                        await page.wait_for_selector('img[alt="character_thumbnail"]')
                        img_element = await target_div.query_selector("img")
                        img_src = await img_element.get_attribute("src")

                        await page.wait_for_selector("p.css-sjt0pv")
                        title_element = await target_div.query_selector("p.css-sjt0pv")
                        title = await title_element.text_content()
                        await page.wait_for_selector("p.css-9xnb32")
                        description_element = await target_div.query_selector("p.css-9xnb32")
                        description = await description_element.text_content()
                        await page.wait_for_selector("p.css-uoinwu")
                        author_element = await target_div.query_selector("p.css-uoinwu")
                        author = await author_element.text_content()

                        # 추출한 정보들로 딕셔너리 생성
                        dic = {"character_name" : title, "character_description" : description, "character_image" : img_src, "character_first_message" : first_msg, "author" : author, "category" : category}

                        # 딕셔너리 데이터를 텍스트 파일에 줄 단위로 붙여쓰기
                        file_name = '/temp/data.txt'
                        await append_json_to_file(file_name, dic)

                        # 현재까지 탐색한 index 수정
                        data[category] = idx
                        with open(f"/temp/index{num}.json", "w", encoding="utf-8") as json_file:
                            json.dump(data, json_file, ensure_ascii=False, indent=4)

                        # 하나의 컨텐츠가 저장됐음을 출력
                        print(f"{category}의 {idx}번 째 데이터를 DB에 저장")

                        # 다음 컨텐츠 탐색
                        idx += 1
                        if limit and idx == limit:
                            print("[LIMIT] 설정한 값에 도달했습니다.")
                            flag = False
                            break
                    except Exception as e1:
                        print(f"[CRASH X] 데이터 추출 과정 중에 문제 발생: {e1}")
                        try:
                            await page.wait_for_selector("p.css-13wxndx")
                            print("모든 컨텐츠를 찾았습니다.")
                            flag = False
                            break
                        except Exception as e2:
                            print(f"[CRASH O] 기존 창을 닫고 새로운 창을 엽니다: {e2}")
                            page = await open_page(browser)
                            idx = await find_previous_idx(browser, page, category, data)

            await browser.close()

        await crawling()

# 순차적으로 실행
async def main():
    if len(sys.argv) != 2:
        sys.exit(1)
    number = int(sys.argv[1])

    create_index_tracking_file(number)

    # 모든 캐릭터를 가져오려면 아래 코드의 주석을 풀어주세요!
    # limit = 0

    # 카테고리 별로 제한된 수의 캐릭터를 가져오려면 설정하세요!
    limit = 100
    
    await crawling_character_info(number, limit)

    # 플래그 파일 생성
    with open(f"/done/extract-{number}", "w") as f:
        f.write(f"extract-{number} done!")

if __name__ == "__main__":
    asyncio.run(main())