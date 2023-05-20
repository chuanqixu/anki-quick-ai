from aqt import mw



def get_words(browse_cmd):
    words = mw.col.find_cards(browse_cmd)
    return words
