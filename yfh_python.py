# Yu-Gi-Oh! Forbidden Memories Fusion Helper (PlayStation 1)
# Based on https://yugipedia.com data
# Ignacio Rodriguez Abraham (nacho.rodriguez.a@gmail.com)
# Edited and updated by Maxwell Moore-Billings (maxwell.moorebillings@gmail.com)

import sys, requests
from bs4 import BeautifulSoup
from typing import List

# URLs setup, this is the url for a Yu-Gi-Oh wiki
BASE_URL = "https://yugipedia.com"
# A list of fusion pages is made because the wiki splits the fusion list into multiple pages
fusions_pages = [
        BASE_URL + "/wiki/List_of_Yu-Gi-Oh!_Forbidden_Memories_Fusions_(001-200)",
        BASE_URL + "/wiki/List_of_Yu-Gi-Oh!_Forbidden_Memories_Fusions_(201-400)",
        BASE_URL + "/wiki/List_of_Yu-Gi-Oh!_Forbidden_Memories_Fusions_(401-600)",
        BASE_URL + "/wiki/List_of_Yu-Gi-Oh!_Forbidden_Memories_Fusions_(601-722)"
]

# Scrapes Forbidden Memories wiki page for fusions and uses user input to return a fusion list
# cards_ids is a list of card ids as strings
# gui_mode is a superfluous parameter left in case a commit is made which introduces a GUI
# By default, an empty dictionary is returned, and the function is annotated with that in mind
def card_fusions_scrp(cards_ids: List[str], gui_mode=False) -> dict:
    # If the user input is empty, then return an empty dictionary
    if cards_ids == None or len(cards_ids) < 1:
        return {}

    # Commented code for possible ritual summon functionality
    # ritual_summons_page = BASE_URL + "/wiki/Yu-Gi-Oh!_Forbidden_Memories#Ritual_Summon"

    # Counts the amount of fusions we have to be displayed later
    fusions_counter = 0
    # Used to keep track of the current maximum attack/defense from our possible fusions
    atk_max = 0
    def_max = 0
    # Used to keep track of whether or not our maximum attack/defense has been outdone by a new possible fusion
    max_changed = False
    # Used to keep track of card types used for the current best fusion
    best_card_merge_type = ''
    # Used to keep track of fusion materials for the current best fusion
    best_card_materials = []
    # Used to keep track of card id for the current best fusion
    best_card_id = ''
    # String that consists of the name of our current best fusion and all it's statistics
    best_card = ''
    # Used later on to list a new set of card ids, eliminating the cards used for fusion material and adding the resulting fusion
    result_ids_using_best_fusion = cards_ids.copy()
    
    # For each of the fusion list pages on the wiki...
    for fusion_page in fusions_pages:
        '''
        soup variable is initialized by creating a BeautifulSoup object, with two parameters
        The first parameter is a Python get request that gets all of the content from fusion_page
        The second parameter is our selected parser, the html.parser that Python includes by default
        '''
        soup = BeautifulSoup(requests.get(fusion_page).content, "html.parser")
        '''
        tables variable is initialized by using the BeautifulSoup method find_all() on our previously defined soup variable
        The first parameter targets HTML content named table
        The second parameter ensures we only target HTML content that also has the wikitable class...
        wikitables typically consist of content formatted as tables that appears in the main content of wiki articles
        The above wikitable class attribute parameter is necessary to avoid selecting tables that don't contain info on fusions
        '''
        tables = soup.find_all('table', attrs={'class':'wikitable'})
        
        # We loop through each of the tables on the page, because each fusion has its own table
        for table in tables:
            '''
            merged_card is initialized by using find_previous to select the "Main Article" section above the fusion table
            Then the HTML tag that names the resulting fusion above the fusion table is selected
            '''
            merged_card = table.find_previous('div').contents[1]
            '''
            merged_card is then redefined as a list of two strings 
            The first string is defined using the text that appears next to the "Main article:" text, below the numbering and
            naming of the fusion
            '"' characters are removed (is this code necessary?)
            '(FMR)' is also removed from the string
            Lastly, any spaces at the beginning or end of the string are removed
            The second string specifies the URL that the hyperlinked fusion name text points to
            (Should I use merged_card.string instead of merged_card.text?)
            '''
            merged_card = [merged_card.text.replace('\"', '').replace('(FMR)', '').strip(), merged_card['href']]
            '''
            merge_type is defined as a list of the types listed for each fusion
            If there are no types listed, then merge_type instead gets defined as a list of strings consisting of all the text from the fusion table
            table.find_previous('div') selects the "Main article:" text and the text for the listed fusion
            table.find_previous('div').next_sibling.next selects the element that occurs next, either the fusion type listing or the fusion table
            Then the text is formatted through the removal of backslashes, leading/trailing spaces, 
            and splits the strings a maximum of one time if a '+' occurs between them
            '''
            merge_type = table.find_previous('div').next_sibling.next.text.replace('\"', '').strip().split(' + ', 1)
            '''
            If more or less than 2 strings occur in merge_type, 
            then we know we didn't receive text listing the two types for the fusion, and we redefine merge_type as an empty list
            '''
            if len(merge_type) != 2:
                merge_type = []
            # Selecting the table rows within the body content of the table and initializing two column variables as empty lists
            rows = table.select('tbody tr')
            col1 = []
            col2 = []
            # Iterating through each row (monsters listed as materials for the current selected fusion), and skipping the "Material 1/Material 2" rows/text           
            for row in rows[1:]:
                # Initializing col1_elem as the first 'td ul' tag that appears, this selects all 'Material 1' monsters
                col1_elem = row.select_one('td ul')
                '''
                Redefining col1 as a list that contains pairs of strings - card ids and card names
                col1_elem.select('li') selects the tags that are formatted as #CARD_ID: "CARD_NAME"
                Then we iterate through each of those tags using a list comprehension, removing '#' and '"' characters, 
                stripping the string, and splitting it along the ':'
                '''
                col1 = [ele.text.replace('#', '').replace('\"', '').strip().split(': ', 1) for ele in col1_elem.select('li')]
                '''
                We do the same process here with col2, using the nth-child(even) CSS selector to ensure we select the 'Material 2' monsters
                '''
                col2_elem = row.select_one('td:nth-child(even)')
                col2 = [ele.text.replace('#', '').replace('\"', '').strip().split(': ', 1) for ele in col2_elem.select('li')]
                '''
                col1_match is initialized as a list that contains pairs of strings - card ids and card names
                for each (id, name) pair in col1, if the id is in our user inputted list of card ids, then we add the pair to our col1_match variable
                '''
                col1_match = [(id, name) for id, name in col1 if id in cards_ids]
                # Then, if we have at least one match...
                if len(col1_match) > 0:
                    # Initialize cards_ids_sub as a copy of our list of user inputted card ids
                    cards_ids_sub = cards_ids.copy()
                    '''
                    Remove each card in col1_match from our cards_ids_sub variable
                    This will prevent fusions that require two of the same card from being listed unless you have two in your hand
                    '''
                    for id, name in col1_match:
                        cards_ids_sub.remove(id)
                    '''
                    Initialize col2_match as a list that contains pairs of strings (card ids and card names)
                    If a card from our col2 variable exists in cards_ids_sub, then add it to col2_match
                    '''
                    col2_match = [(id, name) for id, name in col2 if id in cards_ids_sub]
                    # If we have at least one match...
                    if len(col2_match) > 0:
                        # Increment our fusion counter by one
                        fusions_counter += 1
                        # Initialize fusion materials as a list of cards in our hand that can be used as fusion materials for the current selected fusion
                        fusion_materials = col1_match + col2_match
                        # Initializing a variable which grabs the content of the wiki page for the currently selected fusion
                        sub_soup = BeautifulSoup(requests.get(BASE_URL + merged_card[1]).content, "html.parser")
                        # Initializing a variable which selects the stat table for our selected fusion
                        merged_card_stats_table = sub_soup.find('table', attrs={'class':'innertable'})
                        # Initializing a variable which selects the rows of the stat table for our selected fusion
                        merged_card_stats_rows = merged_card_stats_table.select('tbody tr td')

                        # Max ATK / DEF
                        '''
                        Initializes attack and defense as integers equal to our fusions attack/defense values
                        The attack/defense values are obtained by accessing merged_card_stats_rows and then stripping the text and removing backdashes
                        '''
                        attack = int(merged_card_stats_rows[2].text.strip().split(' / ', 1)[0])
                        defense = int(merged_card_stats_rows[2].text.strip().split(' / ', 1)[1])
                        # If the attack of our fusion is the largest we've seen so far...
                        if attack > atk_max:
                            # Make the current maximum attack value equal to the attack of our fusion
                            atk_max = attack
                            # If our maximum attack value is larger than our maximum defense value...
                            if atk_max > def_max:
                                # Then the current maximum attack/defense value has changed
                                max_changed = True
                        # If the defense of our fusion is the largest we've seen so far...
                        if defense > def_max:
                            # Make the current maximum defense value equal to the defense of our fusion
                            def_max = defense
                            # If our maximum defense value is larger than our maximum attack value...
                            if def_max > atk_max:
                                # Then the current maximum attack/defense value has changed
                                max_changed = True
                        # If our current maximum attack/defense value has changed...
                        if max_changed:
                            # And if our fusion has a pair of fusion material types...
                            if len(merge_type) > 0:
                                # The typing for our fusion will be the pair of types joined by a '+'
                                best_card_merge_type = '[' + ' + '.join(merge_type) + ']'
                            else:
                                # Otherwise our fusion is a specific pairing of cards, and isn't based on card types
                                best_card_merge_type = '[Specific fusion]'
                            # best_card_materials is initialized equal to the fusion_materials variable
                            best_card_materials = fusion_materials
                            # best_card_id is initialized by grabbing the card id from the stat box on the fusion card page and formatting it using strip()
                            best_card_id = merged_card_stats_rows[5].text.strip()
                            '''
                            best_card is initialized as a string of text using the card id, the name of the card, 
                            the attack and defense values, the card type, and the card's guardian stars
                            a new line is added at the end for formatting
                            '''
                            best_card = '====> ' \
                                        + merged_card_stats_rows[5].text.strip() + ' ' \
                                        + merged_card[0] + ' (' \
                                        + merged_card_stats_rows[2].text.strip() + ')  ' \
                                        + merged_card_stats_rows[0].text.strip() + ' | ' \
                                        + merged_card_stats_rows[1].text.replace('\n', ' ').strip()
                        # Case for if our maximum attack/defense values haven't changed
                        max_changed = False

                        # Console prints
                        # If we aren't in GUI Mode...
                        if not gui_mode:
                            # If our fusion uses card types...
                            if len(merge_type) > 0:
                                # Print the fusion typing
                                print('[' + ' + '.join(merge_type) + ']')
                            else:
                                # Otherwise print that it's a specific fusion
                                print('[Specific fusion]')
                            # Print each of the materials that can be used for the fusion
                            for id, name in fusion_materials:
                                print(id, name)
                            # Printing the best card and card statistics like how we defined best_card
                            print('\n====> ' \
                                + merged_card_stats_rows[5].text.strip() + ' ' \
                                + merged_card[0] + ' (' \
                                + merged_card_stats_rows[2].text.strip() + ')  ' \
                                + merged_card_stats_rows[0].text.strip() + ' | ' \
                                + merged_card_stats_rows[1].text.replace('\n', ' ').strip()
                                )
                            print('----------\n')
    # Console prints
    # If we aren't in GUI Mode...
    if not gui_mode:
        # Print the amount of fusions found
        print('\nTOTAL FUSIONS FOUND: ' + str(fusions_counter))
        print('----------\n')
        # If we found possible fusions...
        if fusions_counter > 0:
            # Print the best fusion...
            print('BEST FUSION: \n')
            # Print the fusion typing
            print(best_card_merge_type)
            # For each fusion material's card id and name...
            for id, name in best_card_materials:
                # Remove those cards from our list of card_ids left over after we fuse our best card
                result_ids_using_best_fusion.remove(id)
                # Print the fusion material cards
                print(id, name)
            # Add our fusion's card id to the list of card ids we have left over after we fuse our best card
            result_ids_using_best_fusion.append(best_card_id)
            # Print the best fusion and all its statistics
            print('\n' + best_card + '\n')
            # Print the list of card ids after we've fused our best card
            print('Card IDs using best fusion:')
            print(','.join(result_ids_using_best_fusion))
            print('----------\n')

    return {}
    

# Welcome and help print
def print_welcome_and_help():
    print('Yu-Gi-Oh! Forbidden Memories Fusion Helper\n')
    print('Usage: python yugioh_fusion_helper.py [-l CARDS_ID_LIST]')
    print('CARDS_ID_LIST example: 008,125,357,695,224\n')

# Entry point: CLI help
if len(sys.argv) == 2 and (sys.argv[1] == '-h' or sys.argv[1] == '--help'):
    print_welcome_and_help()
    exit()


# Entry point: CLI param '-l' / '--list'
def entry_point_list_fusions():
    cards_ids = []
    for card_id in sys.argv[2].strip().split(','):
        if len(card_id) == 1:
            card_id = '00' + card_id
        elif len(card_id) == 2:
            card_id = '0' + card_id
        cards_ids.append(card_id)
    card_fusions_scrp(cards_ids)

if len(sys.argv) == 3 and (sys.argv[1] == '-l' or sys.argv[1] == '--list'):
    print('Listing card fusions...\n')
    entry_point_list_fusions()


if len(sys.argv) == 1:
    print_welcome_and_help()
#    entry_point_gui()
