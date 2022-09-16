import os, requests

from yfh_dbscrape import card_list_scrape, create_db_connection

from dotenv import load_dotenv

import psycopg2
from psycopg2 import OperationalError

card_list = card_list_scrape()
load_dotenv()

hand_cards = ['mystical_elf', 'battle_warrior', 'wing_egg_elf', 'wing_egg_elf', 'time_wizard']

def fusions_request(cursor, hand_cards):
    current_card_count = 0
    second_material_count = 1
    match_found = False
    for card in hand_cards[:-1]: 
        print(f"---{card}---")
        get_fusions_sql = f"SELECT second_material from {hand_cards[current_card_count]}"
        cursor.execute(get_fusions_sql)
        fusion_list = cursor.fetchall()
        for second_hand_material in hand_cards[current_card_count + 1:]:
            print(f"-{hand_cards[current_card_count]} + {hand_cards[current_card_count + second_material_count]}")
            for second_material in fusion_list:
                if second_material[0] == hand_cards[current_card_count + second_material_count]:
                    print("match found")
                    match_found = True
                    break
            if match_found:
                match_found = False
            else:
                print("no match found")
            second_material_count += 1
        second_material_count = 1
        current_card_count += 1

connection = create_db_connection(
    os.environ['db_name'], os.environ['user_name'], os.environ['password'], os.environ['host'], os.environ['port']
)
dbcurs = connection.cursor()

fusions_request(dbcurs, hand_cards)

dbcurs.close()
connection.close()