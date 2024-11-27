
import requests
from bs4 import BeautifulSoup


def getRules():
    try:
        response = requests.get("https://chop2.school.org.ua/pravila-dorozhnogo-ruhu-dlya-shkolyariv-15-13-22-22-03-2019/")
        rules = []
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text)
            main_form = soup.find("main")
            all_p = main_form.find_all("p")
            for p in all_p:
                text:str = p.get_text().strip()
                if text[0].isdecimal():
                    text = text.split(".", 1)[-1].strip()
                    rules.append(text)
            all_br = all_p[-2]
            for br in all_br:
                text = br.get_text().strip()
                if text:
                    if text[0].isdecimal():
                        text = text.split(".", 1)[-1].strip()
                        rules.append(text)             
        else:
            print(f"Помилка завантаження: {response.status_code}")
    except requests.RequestException as e:
        print(f"Помилка запиту: {e}")
        rules = ["Не вдалося завантажити правила. Перевірте підключення до Інтернету."]
        
    return rules