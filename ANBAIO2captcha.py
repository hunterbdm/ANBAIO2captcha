import requests
import time
import threading
import webbrowser
from bs4 import BeautifulSoup as bs

current_verson = '1.1.0.0'

apikey = None
site = None

active_threads = 0
captchas_sent = 0

"""
0 - Adidas
1 - SNS
2 - RuVilla
3 - Bodega
4 - YeezySupply
5 - PalaceSB
6 - Consortium
"""

site_names = [
        'Adidas',
        'SNS',
        'RuVilla',
        'Bodega',
        'YeezySupply',
        'PalaceSB',
        'Consortium'
    ]

site_urls = [
        'http://www.adidas.com',
        'http://www.sneakersnstuff.com',
        'http://www.ruvilla.com',
        'http://www.bodega.com',
        'http://www.yeezysupply.com',
        'http://www.palaceskateboards.com',
        'http://www.consortium.co.uk'
    ]

solver_urls = [
        'http://anb.adidas.com:54785/AdidasCaptcha.html',
        'http://anb.sneakersnstuff.com:54785/SNSCaptcha.html',
        'http://anb.ruvilla.com:54785/RuVillaCaptcha.html',
        'bodega Unknown',            # Unconfirmed
        'yeezysupply Unknown',  # Unconfirmed
        'palaceskateboards Unknown',     # Unconfirmed
        'http://anb.consortium.co.uk:54785/ConsortiumCaptcha.html'
    ]

post_urls = [
        'http://anb.adidas.com:54785/resadidas',
        'http://anb.sneakersnstuff.com:54785/ressns',
        'http://anb.ruvilla.com:54785/resruvilla',
        'bodega Unknown',            # Unconfirmed
        'yeezysupply Unknown',  # Unconfirmed
        'palaceskateboards Unknown',       # Unconfirmed
        'http://anb.consortium.co.uk:54785/resConsortium'
    ]

def main():
    global apikey
    global site


    print(
        """
  ___                 _       _                      _____ ____
 |__ \               | |     | |               /\   |_   _/ __ \\
    ) |___ __ _ _ __ | |_ ___| |__   __ _     /  \    | || |  | |
   / // __/ _` | '_ \| __/ __| '_ \ / _` |   / /\ \   | || |  | |
  / /| (_| (_| | |_) | || (__| | | | (_| |  / ____ \ _| || |__| |
 |____\___\__,_| .__/ \__\___|_| |_|\__,_| /_/    \_\_____\____/
               | |   Twitter - https://twitter.com/hunter_bdm
               |_|   Github - https://github.com/hunterbdm
        """
    )

    check_updates()

    apikey_file = open('apikey.txt')
    apikey = apikey_file.read()
    apikey_file.close()

    print('Got APIKEY:', apikey)
    print('Balance:', get_balance(), '\n')

    for i in range(0, len(site_names)):
        print(i, '-', site_names[i])
    x = int(input('Pick a site: '))
    site = x

    print('Captcha Solver URL:', solver_urls[x])

    x = int(input('How many captchas?: '))

    sitekey = get_sitekey()

    if sitekey is None:
        return

    print('Got sitekey', sitekey)

    for i in range(0, int(x)):
        t = threading.Thread(target=get_token_from_2captcha, args=(sitekey, ))
        t.daemon = True
        t.start()
        time.sleep(0.1)
    print('Requested ' + str(x) + ' captcha(s).')
    print('Will exit when all captcha solutions arrived.')
    while not active_threads == 0:
        print('-------------------------')
        print('Active Threads          -', active_threads)
        print('Captchas Sent to ANBAIO -', captchas_sent)
        time.sleep(5)

    print('-------------------------')
    print('Active Threads          -', active_threads)
    print('Captchas Sent to ANB AIO -', captchas_sent)


def check_updates():
    # Check if the current version is outdated
    try:
        response = requests.get('https://raw.githubusercontent.com/hunterbdm/ANBAIO2captcha/master/README.md')
    except:
        print('Unable to check for updates.')
        return

    # If for some reason I forget to add the version to readme I dont want it to fuck up
    if 'Latest Version' in response.text:
        # Grab first line in readme. Will look like this 'Latest Version: 1.0.0.0'
        latest = (response.text.split('\n')[0])
        # Will remove 'Latest Version: ' from string so we just have the version number
        latest = latest[(latest.index(':') + 2):]
        if not latest == current_verson:
            print('You are not on the latest version.')
            print('Your version:', current_verson)
            print('Latest version:', latest)
            x = input('Would you like to download the latest version? (Y/N) ').upper()
            while not x == 'Y' and not x == 'N':
                print('Invalid input.')
                x = input('Would you like to download the latest version? (Y/N) ').upper()
            if x == 'N':
                return
            print('You can find the latest version here https://github.com/hunterbdm/ANBAIO2captcha')
            webbrowser.open('https://github.com/hunterbdm/ANBAIO2captcha')
            exit()
    print('Unable to check for updates.')
    return

def get_balance():
    session = requests.Session()
    session.verify = False
    session.cookies.clear()

    while True:
        data = {
            'key': apikey,
            'action': 'getbalance',
            'json': 1,
        }
        response = session.get(url='http://2captcha.com/res.php', params=data)
        if "ERROR_WRONG_USER_KEY" in response.text or "ERROR_KEY_DOES_NOT_EXIST" in response.text:
            print('Incorrect APIKEY, exiting.')
            exit()

        try:
            json = response.json()
        except:
            time.sleep(3)
            continue

        if json['status'] == 1:
            balance = json['request']
            return balance


def get_token_from_2captcha(sitekey):
    """
    All credit here to https://twitter.com/solemartyr, just stole this from his script
    """
    global active_threads

    active_threads += 1

    session = requests.Session()
    session.verify = False
    session.cookies.clear()
    pageurl = site_urls[site]

    while True:
        data = {
            'key': apikey,
            'action': 'getbalance',
            'json': 1,
        }
        response = session.get(url='http://2captcha.com/res.php', params=data)
        if "ERROR_WRONG_USER_KEY" in response.text or "ERROR_KEY_DOES_NOT_EXIST" in response.text:
            print('Incorrect APIKEY, exiting.')
            exit()

        captchaid = None
        proceed = False
        while not proceed:
            data = {
                'key': apikey,
                'method': 'userrecaptcha',
                'googlekey': sitekey,
                'proxy': 'localhost',
                'proxytype': 'HTTP',
                'pageurl': pageurl,
                'json': 1
            }
            response = session.post(url='http://2captcha.com/in.php', data=data)
            try:
                json = response.json()
            except:
                time.sleep(3)
                continue

            if json['status'] == 1:
                captchaid = json['request']
                proceed = True
            else:
                time.sleep(3)
        time.sleep(3)

        token = None
        proceed = False
        while not proceed:
            data = {
                'key': apikey,
                'action': 'get',
                'json': 1,
                'id': captchaid,
            }
            response = session.get(url='http://2captcha.com/res.php', params=data)
            json = response.json()
            if json['status'] == 1:
                token = json['request']
                proceed = True
            else:
                time.sleep(3)

        if token is not None:
            send_captcha(token)
            return


def get_sitekey():
    try:
        session = requests.Session()
        session.verify = False
        session.cookies.clear()
        resp = session.get(solver_urls[site])
        soup = bs(resp.text, "html.parser")
        sitekey = soup.find("div", class_="g-recaptcha")["data-sitekey"]
        if sitekey is None:
            print('Unable to get sitekey, server may be down.')
            return None
        return sitekey
    except:
        print('Unable to get sitekey, server may be down.')
        return None


def send_captcha(captcha_response):
    global active_threads
    global captchas_sent

    try:
        session = requests.Session()
        session.verify = False
        session.cookies.clear()

        post_url = post_urls[site]
        data_name = post_url[(post_url.index('54785/') + 6):]

        data = {
                data_name: captcha_response
            }
        resp = session.post(post_url, data=data)
        if resp.status_code is 200:
            active_threads -= 1
            captchas_sent += 1
            return
    except:
        print('Unable to send captcha, server may be down.')
        active_threads -= 1
        return None


if __name__ == "__main__":
    main()