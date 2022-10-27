from yfh_python import BASE_URL, fusions_pages

from dotenv import load_dotenv
import os, requests, string

from bs4 import BeautifulSoup

import psycopg2
from psycopg2 import OperationalError

# function to scrape a full list of cards from the wiki
def card_list_scrape() -> list:
    wiki_URL = "https://yugipedia.com"
    card_list_URL = "/wiki/List_of_Yu-Gi-Oh!_Forbidden_Memories_cards"

    # initializing BeautifulSoup object using the card list URL, and finding the first table
    soup = BeautifulSoup(requests.get(f"{wiki_URL}{card_list_URL}").content, "html.parser")
    table = soup.find('table', attrs={'class':'wikitable'})

    # navigating the table to select the card list
    card_list = table.find_next('tbody').find_all('tr')[1:]
    card_table_list = []

    # for each card in the list...
    for card in card_list:
        # navigate to the name of the card and format it by lower casing it, removing punctuation, and replacing spaces with underscores
        card_name = card.find_next('td').find_next('td')
        card_name_formatted = card_name.a.string.lower().translate(str.maketrans('', '', string.punctuation)).replace(' ', '_')
        # find the card's type
        card_type = card.find_next('td').find_next('td').find_next('td').a.string
        # find the URL for the individual card page
        card_url = card_name.a['href']
        # if the card is a monster...
        if card_type == 'Monster':
            # navigate to the individual card page and select the table to find its attack points
            soup = BeautifulSoup(requests.get(f"{wiki_URL}{card_url}").content, "html.parser")
            table = soup.find('table', attrs={'class':'innertable'})

            atk_points = table.find_next('tr').find_next('tr').find_next('tr').find_next('td').string.split('/')[0].strip()
        else:
            # if it isn't a monster, set the atk_points to -1
            atk_points = -1
        # append the card with its attack points to our formatted list of cards
        card_table_list.append([card_name_formatted, atk_points])
        # print statement for testing purposes
        print(card_name_formatted)
   # return our full card list
    return(card_table_list)

def material_checker(mc_mat1_options, mc_mat2_options, mc_card_name, mc_fusion_name, mc_fusion_list) -> list:
    # formatting material strings
    mc_mat1_options = [card1.a.string.lower().translate(str.maketrans('', '', string.punctuation)).replace(' ', '_') 
    for card1 in mc_mat1_options]
    mc_mat2_options = [card2.a.string.lower().translate(str.maketrans('', '', string.punctuation)).replace(' ', '_') 
    for card2 in mc_mat2_options]
    
    # for each material 1...
    for card in mc_mat1_options:
        # if material 1 is the same card as our parameter for the function...
        if mc_card_name == card:
            # append an item to our fusion list, a list containing a list of material 2 options and the name of our fusion
            mc_fusion_list.append([mc_mat2_options, mc_fusion_name])
    # for each material 2...
    for card in mc_mat2_options:
        # if material 2 is the same card as our parameter for the function...
        if mc_card_name == card:
            # append an item to our fusion list, a list containing a list of material 1 options and the name of our fusion
            mc_fusion_list.append([mc_mat1_options, mc_fusion_name])

    return mc_fusion_list

# function to create a list of all possible fusions that can be made using a particular card by scraping from the wiki
def fusion_material_scrape(card_name) -> list:
    fusion_list = []
    # for each of the 4 pages on the wiki that list fusions... 
    for fusion_page in fusions_pages:
        # create a BeautifulSoup object and select all tables (each table is a fusion)
        soup = BeautifulSoup(requests.get(fusion_page).content, "html.parser")
        tables = soup.find_all('table', attrs={'class':'wikitable'})

        # for each table (fusion)...
        for table in tables:
            # create a fusion_name variable by formatting the name of the fusion from the wiki
            fusion_name = table.find_previous('div').a.text.lower().replace(' (fmr)', '')
            fusion_name = fusion_name.translate(str.maketrans('', '', string.punctuation)).replace(' ', '_')    

            if "mystical_sheep" in fusion_name:
                fusion_name = "mystical_sheep_1"
            # selecting a section for each possible way to make a particular fusion
            materials = table.find_all('tr')[1:]
             # for each material within each section...
            for material_option in materials:
                # make a formatted list of materials that can be used as material one and two
                material_one_options = material_option.find_next('td').find_all('li')
                material_two_options = material_option.find_next('td').find_next('td').find_all('li')
            # checking combinations for any possible fusions and appending them to our list
            fusion_list = material_checker(material_one_options, material_two_options, card_name, fusion_name, fusion_list)
    
    # creating a soup object that scrapes the glitch fusion page on the wiki
    soup = BeautifulSoup(requests.get("https://yugipedia.com/wiki/Glitch_fusion").content, "html.parser")
    glitch_table = soup.find('table', attrs={'class':'wikitable'})

    glitch_fusion_list = glitch_table.find_all('tr')[1:]

    # these row variables are used as counts for the amount of listed combinations for a particular fusion
    result_row_amounts = [3, 1, 4, 1, 2, 4]
    current_row = [3, 1, 4, 1, 2, 4]
    # keeps track of which fusion we're currently checking
    fusion_index = 0
    # iterating through each listed fusion
    for fusion in glitch_fusion_list:
        # if we've iterated through all combinations for the current fusion, then increment our fusion index
        if current_row[fusion_index] == 0:
            fusion_index += 1
        # pulling and formatting the materials and results for each fusion
        # if we're selecting the first combination for a listed fusion, then grab the name of the fusion and assign it to result
        if current_row[fusion_index] == result_row_amounts[fusion_index]:
            result = fusion.find_next('td')
            result = result.a.string.lower().translate(str.maketrans('', '', string.punctuation)).replace(' ', '_')

            material_one = fusion.find_next('td').find_next('td')
            material_two = fusion.find_next('td').find_next('td').find_next('td')
        else:
            material_one = fusion.find_next('td')
            material_two = fusion.find_next('td').find_next('td')

        # decrement our current row count
        current_row[fusion_index] -= 1

        # string formatting our materials
        material_one = material_one.a.string.lower().translate(str.maketrans('', '', string.punctuation)).replace(' ', '_')
        material_two = material_two.a.string.lower().translate(str.maketrans('', '', string.punctuation)).replace(' ', '_')

        # checking for matches and appending them to our list
        if card_name == material_one:
            fusion_list.append([material_two, result])
        elif card_name == material_two:
            fusion_list.append([material_one, result])

    # return the fusion list
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
    # unique id for identifying fusions
    fusion_id_count = 1

    # for each card in our full list of cards scraped from the wiki
    for card in card_name_list:
        print(card)
        # grab a list of possible fusions using our fusion_material_scrape function
        fusion_list = fusion_material_scrape(card)

        # grab the id of our currently selected card
        select_material_one_id = f"SELECT card_id FROM scraped_card_list WHERE card_name='{card}'"
        cursor.execute(select_material_one_id)
        material_one_id = cursor.fetchall()[0][0]

        # for each fusion in our list of possible fusions for our selected card...
        for fusion in fusion_list:
            # grab the id of the possible fusion
            print(fusion[1])
            select_result_id = f"SELECT card_id FROM scraped_card_list WHERE card_name='{fusion[1]}'"
            cursor.execute(select_result_id)
            result_id = cursor.fetchall()[0][0]

            if type(fusion[0]) is not str:
                # for each material that can be used as a second material for the possible fusion...
                for material_two in fusion[0]:
                    # grab the id of the second material
                    select_material_two_id = f"SELECT card_id FROM scraped_card_list WHERE card_name='{material_two}'"
                    cursor.execute(select_material_two_id)
                    print(material_two)
                    material_two_test_id = cursor.fetchall()
                    print(material_two_test_id)
                    material_two_id = material_two_test_id[0][0]

                    # insert a new record with our unique fusion id, the ids for materials used for the fusion, and the resulting fusion id
                    insert_fusion_sql = f"INSERT INTO fusion_list (fusion_id, material_one, material_two, result) VALUES ({fusion_id_count}, {material_one_id}, {material_two_id}, {result_id})"                
                    cursor.execute(insert_fusion_sql)

                    # prints for testing purposes and displaying progress while adding records to our database
                    print(f"entry added - {card}, {material_two}, {fusion[1]}")
                    print(f"fusion count {fusion_id_count}")
                    fusion_id_count += 1
            else:
                material_two = fusion[0]
                select_material_two_id = f"SELECT card_id FROM scraped_card_list WHERE card_name='{material_two}'"
                cursor.execute(select_material_two_id)
                print(material_two)
                material_two_test_id = cursor.fetchall()
                print(material_two_test_id)
                material_two_id = material_two_test_id[0][0]

                # insert a new record with our unique fusion id, the ids for materials used for the fusion, and the resulting fusion id
                insert_fusion_sql = f"INSERT INTO fusion_list (fusion_id, material_one, material_two, result) VALUES ({fusion_id_count}, {material_one_id}, {material_two_id}, {result_id})"                
                cursor.execute(insert_fusion_sql)

                # prints for testing purposes and displaying progress while adding records to our database
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
