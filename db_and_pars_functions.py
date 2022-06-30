import requests
import os
import psycopg2

from bs4 import BeautifulSoup
from config import *
from pathlib import Path
from dotenv import load_dotenv

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


def start_connection() -> tuple:
    conn = psycopg2.connect(f"dbname={os.getenv('DB')} user={os.getenv('USER')} password={os.getenv('PASSWORD')}")
    cur = conn.cursor()
    return conn, cur


def get_cities() -> list:
    conn, cur = start_connection()
    cur.execute("SELECT city from cityinfo")
    query_list = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return list(map(lambda x: str(x[0]).title(), query_list))


def get_city_info(city) -> tuple:
    conn, cur = start_connection()
    cur.execute(f"SELECT population, link from cityinfo WHERE city = '{city}'")
    item = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return str(item[0]), str(item[1])


def start_parser() -> None:
    # Подключаемся к БД и создаем таблицу(если она еще не была создана)
    conn, cur = start_connection()
    cur.execute("""CREATE TABLE IF NOT EXISTS cityinfo (
        id serial PRIMARY KEY, 
        city varchar(50), 
        population INTEGER, 
        link VARCHAR
        );""")

    # делаем запро по всем горадам в базе данных
    cur.execute("SELECT * from cityinfo")
    query_list = cur.fetchall()
    # переводим список множест в множество городов для дальнейшего быстрого поиска
    cities_query_list = set(map(lambda x: x[1], query_list))
    check_for_upd_dict = {}  # cловарь который будем использовать при проверки на необходимость UPD записи в БД
    for row in query_list:
        check_for_upd_dict[row[1]] = str(row[2]) + row[3]

    r = requests.get(url).content
    soup = BeautifulSoup(r, 'lxml')
    table = soup.find("table", class_="standard sortable")
    tbody = table.find("tbody")
    trs = tbody.find_all("tr")

    # формируем словарь с номерами полей, на случай если столбцы в таблици в wiki поменяется
    field_name_dict = {}
    for ind, item in enumerate(trs[0]):
        field_name_dict[item.getText()] = ind
    pop_ind = field_name_dict["население,чел."]  # индекс поля с населением
    city_ind = field_name_dict["город"]  # индекс поля с названием города

    for tr in trs[1:]:
        tds = tr.find_all("td")
        population = tds[pop_ind].get('data-sort-value')
        city = tds[city_ind].getText().title()
        link = root_wiki_url + tds[city_ind].a.get("href")

        if city not in cities_query_list:  # если нет в БД записи с таким городом, то делаем INSERT
            cur.execute(f"""
                INSERT INTO cityinfo (city, population, link)
                VALUES ('{city}', {population}, '{link}')
                """)
        # если спарсенные данные ссылки+популяция не совпадают, то обновляем эту строку в БД
        elif str(population) + link != check_for_upd_dict[city]:
            cur.execute(f"""
                UPDATE cityinfo 
                SET population = {population}, link = '{link}' 
                WHERE city = '{city}'
                """)

    conn.commit()
    cur.close()
    conn.close()
