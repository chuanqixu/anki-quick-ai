from configure import settings
import json
from requests_html import HTMLSession



session = HTMLSession()

# 1. log in to AnkiWeb
#   (1) AnkiWeb requires cookies
#   (2) AnkiWeb inlcudes two additional hidden inputs for log in form

#   a. get the cookies and these two additional hidden inputs
r = session.get("https://ankiweb.net/account/login")
input_elem_list = r.html.find('input')


headers = {
    "content-type": "application/x-www-form-urlencoded"
}
payload = {
    'username': settings.email,
    'password': settings.password
}
# two additional inputs for log in form
payload[input_elem_list[0].attrs['name']] = input_elem_list[0].attrs['value']
payload[input_elem_list[1].attrs['name']] = input_elem_list[1].attrs['value']
cookies = dict(r.cookies)

#   b. log in
r = session.post("https://ankiweb.net/account/login", headers=headers, verify=True, data=payload, cookies=cookies)


# 2. go to the study page
r = session.get("https://ankiweb.net/study/", verify=True)


# 2. retrieve new words
headers = {
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest"
}
payload = {"answers":[],"saveAnswersOnly":False}

r = session.post("https://ankiuser.net/study/getCards", headers=headers, verify=True, json=payload)
card_list = json.loads(r.text)["cards"]



# TODO: parsing question HTML 
