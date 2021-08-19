# Yu-Gi-Oh! Forbidden Memories Fusion Helper (PlayStation 1)
# Based on https://yugipedia.com data
# -/-\-El coni-/-\-

import sys, requests
from bs4 import BeautifulSoup
from typing import List


def card_fusions_scrap(cards_ids: List[str], gui_mode=False) -> dict:
    if cards_ids == None or len(cards_ids) < 1:
        return {}

    # URLs setup
    BASE_URL = "https://yugipedia.com"
    fusions_pages = [
        BASE_URL + "/wiki/List_of_Yu-Gi-Oh!_Forbidden_Memories_Fusions_(001-200)",
        BASE_URL + "/wiki/List_of_Yu-Gi-Oh!_Forbidden_Memories_Fusions_(201-400)",
        BASE_URL + "/wiki/List_of_Yu-Gi-Oh!_Forbidden_Memories_Fusions_(401-600)",
        BASE_URL + "/wiki/List_of_Yu-Gi-Oh!_Forbidden_Memories_Fusions_(601-722)"
    ]
#    ritual_summons_page = BASE_URL + "/wiki/Yu-Gi-Oh!_Forbidden_Memories#Ritual_Summon"

    # Scrap
    fusions_counter = 0
    atk_max = 0
    def_max = 0
    max_changed = False
    best_card_merge_type = ''
    best_card_materials = []
    best_card_id = ''
    best_card = ''
    result_ids_using_best_fusion = cards_ids.copy()

    for fusion_page in fusions_pages:
        soup = BeautifulSoup(requests.get(fusion_page).content, "html.parser")
        tables = soup.find_all('table', attrs={'class':'wikitable'})

        for table in tables:
            merged_card = table.find_previous('div').findChild('a')
            merged_card = [merged_card.text.replace('\"', '').replace('(FMR)', '').strip(), merged_card['href']]
            merge_type = table.find_previous('div').next_sibling.next.text.replace('\"', '').strip().split(' + ', 1)
            if len(merge_type) != 2:
                merge_type = []
            rows = table.select('tbody tr')
            col1 = []
            col2 = []

            for row in rows[1:]:
                col1_elem = row.select_one('td ul')
                col1 = [ele.text.replace('#', '').replace('\"', '').strip().split(': ', 1) for ele in col1_elem.select('li')]
                col2_elem = row.select_one('td:nth-child(even)')
                col2 = [ele.text.replace('#', '').replace('\"', '').strip().split(': ', 1) for ele in col2_elem.select('li')]

                col1_match = [(id, name) for id, name in col1 if id in cards_ids]
                if len(col1_match) > 0:
                    cards_ids_sub = cards_ids.copy()
                    for id, name in col1_match:
                        cards_ids_sub.remove(id)
                    col2_match = [(id, name) for id, name in col2 if id in cards_ids_sub]
                    if len(col2_match) > 0:

                        # Match found
                        fusions_counter += 1
                        fusion_materials = col1_match + col2_match
                        sub_soup = BeautifulSoup(requests.get(BASE_URL + merged_card[1]).content, "html.parser")
                        merged_card_stats_table = sub_soup.find('table', attrs={'class':'innertable'})
                        merged_card_stats_rows = merged_card_stats_table.select('tbody tr td')

                        # Max ATK / DEF
                        attack = int(merged_card_stats_rows[2].text.strip().split(' / ', 1)[0])
                        defense = int(merged_card_stats_rows[2].text.strip().split(' / ', 1)[1])
                        if attack > atk_max:
                            atk_max = attack
                            if atk_max > def_max:
                                max_changed = True
                        if defense > def_max:
                            def_max = defense
                            if def_max > atk_max:
                                max_changed = True
                        if max_changed:
                            best_card_merge_type = '[' + ' + '.join(merge_type) + ']'
                            best_card_materials = fusion_materials
                            best_card_id = merged_card_stats_rows[5].text.strip()
                            best_card = '====> ' \
                                        + merged_card_stats_rows[5].text.strip() + ' ' \
                                        + merged_card[0] + ' (' \
                                        + merged_card_stats_rows[2].text.strip() + ')  ' \
                                        + merged_card_stats_rows[0].text.strip() + ' | ' \
                                        + merged_card_stats_rows[1].text.replace('\n', ' ').strip()
                        max_changed = False

                        # Console prints
                        if not gui_mode:
                            if len(merge_type) > 0:
                                print('[' + ' + '.join(merge_type) + ']')
                            else:
                                print('[Specific fusion]')
                            for id, name in fusion_materials:
                                print(id, name)
                            print('\n====> ' \
                                + merged_card_stats_rows[5].text.strip() + ' ' \
                                + merged_card[0] + ' (' \
                                + merged_card_stats_rows[2].text.strip() + ')  ' \
                                + merged_card_stats_rows[0].text.strip() + ' | ' \
                                + merged_card_stats_rows[1].text.replace('\n', ' ').strip()
                                )
                            print('----------\n')
    # Console prints
    if not gui_mode:
        print('\nTOTAL FUSIONS FOUND: ' + str(fusions_counter))
        print('----------\n')
        if fusions_counter > 0:
            print('BEST FUSION: \n')
            print(best_card_merge_type)
            for id, name in best_card_materials:
                result_ids_using_best_fusion.remove(id)
                print(id, name)
            result_ids_using_best_fusion.append(best_card_id)
            print('\n' + best_card + '\n')
            print('Card IDs using best fusion:')
            print(','.join(result_ids_using_best_fusion))
            print('----------\n')

    return {}


# Welcome and help print
def print_welcome_and_help():
    print('Yu-Gi-Oh! Forbidden Memories Fusion Helper\n')
    print('Usage: python yugiparser.py [-l CARDS_ID_LIST]')
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
    card_fusions_scrap(cards_ids)

if len(sys.argv) == 3 and (sys.argv[1] == '-l' or sys.argv[1] == '--list'):
    print('Listing card fusions...\n')
    entry_point_list_fusions()


# Entry point: CLI without params (wizard)
#def entry_point_cli_wizard():
#    return

if len(sys.argv) == 1:
    print_welcome_and_help()
#    entry_point_cli_wizard()
