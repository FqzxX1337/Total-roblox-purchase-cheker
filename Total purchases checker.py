import requests
import time
import json
import re

total = 0
cookie = str(input("Enter your cookie: "))

with requests.Session() as session:
    # Настройка заголовков для имитации обычного браузера
    session.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.roblox.com/',
        'Origin': 'https://www.roblox.com'
    }
    
    # Установка cookie
    session.cookies['.ROBLOSECURITY'] = cookie
    
    # Получение UserID новым методом
    try:
        # Сначала попробуем получить данные с домашней страницы
        home_page = session.get('https://www.roblox.com/home')
        if home_page.status_code != 200:
            print(f"Ошибка при доступе к домашней странице: {home_page.status_code}")
            exit(1)
            
        # Проверка валидности cookie
        auth_check = session.get('https://users.roblox.com/v1/users/authenticated')
        if auth_check.status_code == 200:
            auth_data = auth_check.json()
            if 'id' in auth_data:
                userId = auth_data['id']
                print(f"Успешно получен UserID: {userId}")
            else:
                print("Не удалось получить ID пользователя. Проверьте cookie.")
                exit(1)
        else:
            print(f"Ошибка при проверке аутентификации: {auth_check.status_code}")
            print(auth_check.text)
            exit(1)
    except Exception as e:
        print(f"Произошла ошибка при получении UserID: {e}")
        exit(1)

    def main():
        global total
        cursor = ''
        page_count = 0
        
        print("Начинаем сбор данных о покупках...")
        
        while cursor is not None:
            try:
                url = f'https://economy.roblox.com/v2/users/{userId}/transactions'
                params = {
                    'transactionType': 'Purchase',
                    'limit': 100,
                    'cursor': cursor
                }
                
                response = session.get(url, params=params)
                
                # Проверка статуса ответа
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'data' in data and len(data['data']) > 0:
                        page_count += 1
                        print(f'Страница {page_count}: Найдено {len(data["data"])} покупок')
                        
                        for purchase in data['data']:
                            if purchase['currency']['type'] == 'Robux':
                                total += purchase['currency']['amount']
                        
                        cursor = data.get('nextPageCursor')
                        if not cursor:
                            print("Достигнут конец данных")
                            break
                    else:
                        print("Нет данных о покупках или достигнут конец списка")
                        break
                elif response.status_code == 429:
                    print("Слишком много запросов. Ожидание 60 секунд...")
                    time.sleep(60)
                elif response.status_code == 401:
                    print("Ошибка авторизации. Cookie недействителен или срок его действия истек.")
                    break
                else:
                    print(f"Ошибка API: {response.status_code}")
                    print(response.text)
                    time.sleep(30)
            except Exception as e:
                print(f"Произошла ошибка: {e}")
                time.sleep(30)
            
            # Добавляем небольшую задержку между запросами
            time.sleep(2)

    try:
        main()
        
        total = str(total).replace('-', '')
        print(f'\nТвой тотал: {total} робуксов')
    except KeyboardInterrupt:
        print("\nПрограмма остановлена пользователем")
    except Exception as e:
        print(f"\nПроизошла непредвиденная ошибка: {e}")

print("\nРабота программы завершена")
time.sleep(10) 