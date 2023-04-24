import json
import urllib.request



def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

def invoke(action, **params):
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:8765', requestJson)))
    if len(response) != 2:
        raise ValueError('response has an unexpected number of fields')
    if 'error' not in response:
        raise ValueError('response is missing required error field')
    if 'result' not in response:
        raise ValueError('response is missing required result field')
    if response['error'] is not None:
        raise ValueError(response['error'])
    return response['result']


def retrieve_words(deck_name = None, query = None, field = None):
    if not deck_name:
        deck_name = "current"
    if not query:
        # retrieve only the first introduced words today
        query = f'"deck:{deck_name}" introduced:1'
    
    cards = invoke("findCards", query=query)
    cards_info = invoke("cardsInfo", cards=cards)

    # # Send a request to get the note for each card ID
    words = []
    for card_info in cards_info:
        if field != "":
            word = card_info["fields"][field]["value"]
        else:
            # if field is not specified, default is the first field
            for field, value in card_info["fields"].items():
                if value["order"] == 0:
                    word = value["value"]
                    break
        
        words.append(word)
    
    return words
