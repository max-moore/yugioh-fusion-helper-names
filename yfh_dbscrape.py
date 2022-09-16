from yfh_python import BASE_URL, fusions_pages

from dotenv import load_dotenv
import os, requests, string

from bs4 import BeautifulSoup

import psycopg2
from psycopg2 import OperationalError

def card_list_scrape() -> list:
    wiki_URL = "https://yugipedia.com"
    card_list_URL = "/wiki/List_of_Yu-Gi-Oh!_Forbidden_Memories_cards"

    soup = BeautifulSoup(requests.get(f"{wiki_URL}{card_list_URL}").content, "html.parser")
    table = soup.find('table', attrs={'class':'wikitable'})

    card_list = table.find_next('tbody').find_all('tr')[1:]
    card_table_list = []

    for card in card_list:
        card_name = card.find_next('td').find_next('td')
        card_name_formatted = card_name.a.string.lower().translate(str.maketrans('', '', string.punctuation)).replace(' ', '_')

        card_type = card.find_next('td').find_next('td').find_next('td').a.string

        card_url = card_name.a['href']

        if card_type == 'Monster':
            soup = BeautifulSoup(requests.get(f"{wiki_URL}{card_url}").content, "html.parser")
            table = soup.find('table', attrs={'class':'innertable'})

            atk_points = table.find_next('tr').find_next('tr').find_next('tr').find_next('td').string.split('/')[0].strip()
        else:
            atk_points = -1

        card_table_list.append([card_name_formatted, atk_points])
        print(card_name_formatted)
   
    return(card_table_list)

def fusion_material_scrape(card_name) -> list:
    fusion_list = []

    for fusion_page in fusions_pages:
        soup = BeautifulSoup(requests.get(fusion_page).content, "html.parser")
        tables = soup.find_all('table', attrs={'class':'wikitable'})

        for table in tables:
            fusion_name = table.find_previous('div').a.text.lower().replace(' (fmr)', '')
            fusion_name = fusion_name.translate(str.maketrans('', '', string.punctuation)).replace(' ', '_')
            materials = table.find_all('tr')[1:]
            for material_option in materials:
                material_one_options = material_option.find_next('td').find_all('li')
                material_two_options = material_option.find_next('td').find_next('td').find_all('li')

                material_one_options = [card1.a.string.lower().translate(str.maketrans('', '', string.punctuation)).replace(' ', '_') for card1 in material_one_options]
                material_two_options = [card2.a.string.lower().translate(str.maketrans('', '', string.punctuation)).replace(' ', '_') for card2 in material_two_options]

                for card in material_one_options:
                    if card_name == card:
                        fusion_list.append([material_two_options, fusion_name])
    
                for card in material_two_options:
                    if card_name == card:
                        fusion_list.append([material_one_options, fusion_name])

    return(fusion_list)

def create_db_connection(db_name, db_user, db_password, db_host, db_port):
    connection = None
    try:
        connection = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
        print("Connection to PostgreSQL DB successful")
    except OperationalError as e:
        print(f"The error '{e}' occurred")
    return connection

# Used to create card list table
def create_card_table(cursor):
    create_sql = "CREATE TABLE scraped_card_list (card_id smallint, card_name varchar(255), atk_points smallint)"
    cursor.execute(create_sql)

# Used to delete card table
def delete_card_table(cursor):
    delete_sql = "DROP TABLE scraped_card_list"
    cursor.execute(delete_sql)

# Used to delete fusion table
def delete_fusion_table(cursor):
    delete_sql = "DROP TABLE fusion_list"
    cursor.execute(delete_sql)

# Used to populate card list table
def card_list_table_populate(card_table_list, cursor):
    id_count = 1
    for card in card_table_list:
        insert_name_sql = f"INSERT INTO scraped_card_list (card_id, card_name, atk_points) VALUES ({id_count}, '{card[0]}', '{card[1]}')"
        cursor.execute(insert_name_sql)
        id_count += 1

# Used to create fusion table
def fusion_table_creator(cursor):
    create_fusion_sql = "CREATE TABLE fusion_list (fusion_id int, material_one smallint, material_two smallint, result smallint)"
    cursor.execute(create_fusion_sql)

# Used to populate fusion table
def fusion_table_populate(card_name_list, cursor):
    fusion_id_count = 1

    for card in card_name_list:
        fusion_list = fusion_material_scrape(card)

        select_material_one_id = f"SELECT card_id FROM scraped_card_list WHERE card_name='{card}'"
        cursor.execute(select_material_one_id)
        material_one_id = cursor.fetchall()[0][0]

        for fusion in fusion_list:
            select_result_id = f"SELECT card_id FROM scraped_card_list WHERE card_name='{fusion[1]}'"
            cursor.execute(select_result_id)
            result_id = cursor.fetchall()[0][0]

            for material_two in fusion[0]:
                select_material_two_id = f"SELECT card_id FROM scraped_card_list WHERE card_name='{material_two}'"
                cursor.execute(select_material_two_id)
                material_two_id = cursor.fetchall()[0][0]

                insert_fusion_sql = f"INSERT INTO fusion_list (fusion_id, material_one, material_two, result) VALUES ({fusion_id_count}, {material_one_id}, {material_two_id}, {result_id})"                
                cursor.execute(insert_fusion_sql)

                print(f"entry added - {card}, {material_two}, {fusion[1]}")
                print(f"fusion count {fusion_id_count}")
                fusion_id_count += 1

'''Database Operations'''

# loads environment variables and creates connection
load_dotenv()
connection = create_db_connection(
    os.environ['db_name'], os.environ['user_name'], os.environ['password'], os.environ['host'], os.environ['port']
)
dbcurs = connection.cursor()

# deletes tables      
# delete_card_table(dbcurs)
# delete_fusion_table(dbcurs)

# [Optional] list of cards scraped from wiki
# card_name_list_final = card_list_scrape()  

# [Alternative] grab list of cards from our already created table instead
# select_card_list_sql = "SELECT card_name FROM scraped_card_list"
# dbcurs.execute(select_card_list_sql)
# card_name_list_final = dbcurs.fetchall()
# card_name_list_final = [card[0] for card in card_name_list_final]

# creates the card list table
# create_card_table(dbcurs)

# create and populate card/fusion list tables
# card_list_table_populate(card_name_list_final, dbcurs)
# fusion_table_creator(dbcurs)
# fusion_table_populate(card_name_list_final, dbcurs)

# commit changes and close connection
connection.commit()

dbcurs.close()
connection.close()

print("Changes committed and connection closed.")
