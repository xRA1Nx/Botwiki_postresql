import requests
from bs4 import BeautifulSoup
from config import *

parser_data = {}

label_for_dict_list = ["город", "городской округ", "ОКАТО", "население", ]

r = requests.get(url).content
soup = BeautifulSoup(r, 'lxml')

table = soup.find("table", class_="standard sortable")
# print(table)
tbody = table.find("tbody")
trs = tbody.find_all("tr")
for tr in trs:
    tds = tr.find_all("td")
    tds = tds[1:2] + tds[4:5]
    for td in tds:
        if td.get('data-sort-value'):
            parser_data[td.get('data-sort-value')] = "население"
        else:
            parser_data[(td.getText())] = "город"
            parser_data[td.a.get("href")] = "Ссылка на Wiki"
print(parser_data)

# for tr in tbody:
#     # td = tr.find("td")
#     print(tr)
#     break



