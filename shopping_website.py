import requests
from bs4 import BeautifulSoup as bs
# from PIL import Image
# import os
import re
import json
user_input = input('請輸入商品名稱 (英文、數字或2個以上中文字): ')

def find_product(user_input):
    pchome_page = 'https://24h.pchome.com.tw'
    search = user_input.replace(" ", "%20")
    search_page_url = pchome_page + "/search/?q=" + search
    try:
        response = requests.get(search_page_url)
        response.raise_for_status()
    except Exception as e:
        print(e)
    soup = bs(response.text, 'lxml')
    if soup.select('.c-pagination__item') is None: 
        num_of_pages = int(soup.select('.c-pagination__item')[-1].text)
    else: 
        num_of_pages = 1
    print(f"搜尋結果有 {num_of_pages} 頁")
    page = 1
    for i in range(num_of_pages):
        # i==1為第二頁，網址列加 &p=2
        if i >= 1:
            page = i + 1
            current_page_url = search_page_url + f"&p={page}"
            response = requests.get(current_page_url)
        try:
            response.raise_for_status()
            soup = bs(response.text, 'lxml')
            real_products = soup.select('li.c-listInfoGrid__item > div.c-prodInfoV2--gridCard')
            # cnt = 0 ##
            for real_product in real_products:
                # if cnt > 1:
                #     break
                product_title = real_product.find('div', class_="c-prodInfoV2__title").text
                
                # 如果 (1)有中文 且 (2)user_input的前2個中文字不在product_title裡面
                if len(re.findall(r'[\u4e00-\u9fff]+', user_input)) > 0 and (not re.search(r'[\u4e00-\u9fff]{2}', user_input).group(0) in product_title):
                    print('以下商品名稱不符，或拼字錯誤')
                    print(f"商品名稱: {product_title}")
                # 如果 (1)沒有中文 且 (2)user_input小寫&去除空白後不在product_title裡面
                elif len(re.findall(r'[\u4e00-\u9fff]+', user_input)) == 0 and (not user_input.lower().replace(' ', '') in product_title.lower().replace(' ', '')):
                    print('以下商品名稱不符，或拼字錯誤')
                    print(f"商品名稱: {product_title}")
                else:
                    print(f"商品名稱: {product_title}")
                    product_img_link = real_product.select("div.c-prodInfoV2__img > img")[0]['src']
                    print(f"商品圖片連結: {product_img_link}")
                    # image_content = requests.get(product_img_link).content
                    # with open(f"./product_images/product_0.png", "wb") as f:
                    #     f.write(image_content)
                    # img = Image.open("./product_images/product_0.png")
                    # img.show()

                    product_price = real_product.find('div', class_="c-prodInfoV2__priceValue").text
                    print(f"商品價格: {product_price}")

                    product_link = real_product.find('a', class_="c-prodInfoV2__link")['href']
                    print(f"購買連結: {pchome_page + product_link}")

                    response_proc_detail = requests.get(pchome_page + product_link)

                    soup_proc_detail = bs(response_proc_detail.text, 'lxml')
                    product_slogans = soup_proc_detail.select_one('ul.c-blockCombine__list')
                    product_descriptions = product_slogans.select('li')
                    print('商品說明: ')
                    product_description_str = ""
                    for product_description in product_descriptions:
                        product_description_str += f"{product_description.text} "
                        print(f"> {product_description.text}")
                    print(' ')
                    data = {
                        "商品名稱":product_title, 
                        "商品價格":product_price, 
                        "購買連結":pchome_page + product_link, 
                        "商品圖片連結":product_img_link, 
                        "商品說明":product_description_str
                    }
                    with open("output.json", "a", encoding="utf8") as outfile:
                        json.dump(data, outfile, ensure_ascii=False, indent=4)
                # cnt += 1
        except Exception as e:
            print("網頁無法連線，或是沒有下一頁")
            print(e)
        print(f'第{page}頁找完\n')
        i += 1
        
find_product(user_input)