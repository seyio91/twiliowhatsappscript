import json, sys, requests, random, os
import urllib.parse
from dotenv import load_dotenv
from twilio.rest import Client
from bs4 import BeautifulSoup as bs

load_dotenv(override=True)

# reading the environment variables
account_sid = os.environ.get('TWILIOSID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
gtranslateApiKey = os.environ.get('GOOGLEAPIKEY')

def getMessage():
    url = 'https://www.serenataflowers.com/pollennation/love-messages/'
    res = requests.get(url)
    try:
        res.raise_for_status()
    except requests.exceptions.HTTPError:
        sys.exit(1)
    soup = bs(res.text, features="html.parser")
    listOfMessages = soup.select('.simple-list li')
    textMessages = [item.text for item in listOfMessages]
    return random.choice(textMessages)

def _get_request(url, payload):
    r = requests.get(url, params=payload)
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError:
        print('Error: the Request failed.')
        sys.exit(1)
    response = json.loads(r.content.decode('utf-8-sig'))
    return response

transUrl = 'https://translation.googleapis.com/language/translate/v2'
randomLangUrl = 'https://translation.googleapis.com/language/translate/v2/languages'

client = Client(twiliosid, twiliotoken)

randomLangPayload = {'key': gtranslateApiKey}

destResponse = _get_request(randomLangUrl, randomLangPayload)
dest_language = random.choice(destResponse['data']['languages'])

transPayload = {
        'source': 'en',
        'target': dest_language,
        'key': gtranslateApiKey,
        'q': urllib.parse.quote('I Love You')
    }

transResponse = _get_request(transUrl, transPayload)
msg = transResponse.get('data').get('translations')[0].get('translatedText')

randomquote = getMessage()
msg = translate('I Love You', 'en', dest_language, gtranslateApiKey)
fulltextmsg = randomquote + " \n P.S. " + msg


message = client.messages.create(
                            from_='whatsapp:+14155238886',
                            body=fulltextmsg,
                            to='whatsapp:<your number>'
                        )

return {
        'statusCode': 200,
        'body': message.sid
    }