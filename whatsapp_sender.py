import json
import sys
import boto3
import requests
import urllib.parse
import random
from twilio.rest import Client
from bs4 import BeautifulSoup as bs

ssm = boto3.client('ssm')



url = 'https://www.serenataflowers.com/pollennation/love-messages/'
res = requests.get(url)
try:
    res.raise_for_status()
except requests.exceptions.HTTPError:
    sys.exit(1)
soup = bs(res.text, features="html.parser")
listOfMessages = soup.select('.simple-list li')
textMessages = [item.text for item in listOfMessages]
randomquote = random.choice(textMessages)

def _get_request(url, payload):
    r = requests.get(url, params=payload)
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError:
        print('Error: the Request failed.')
        sys.exit(1)
    response = json.loads(r.content.decode('utf-8-sig'))
    return response

def _getParameter(someString):
    paramObject = ssm.get_parameter(Name=someString, WithDecryption=True)
    return paramObject['Parameter']['Value']

transUrl = 'https://translation.googleapis.com/language/translate/v2'
randomLangUrl = 'https://translation.googleapis.com/language/translate/v2/languages'


def lambda_handler(event, context):
    # TODO implement
    gtranslateApiKey = _getParameter('GtranslateApiKey')
    twiliotoken = _getParameter('valapptokentwilio')
    twiliosid = _getParameter('whatsappsidtwilio')

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

    msg = translate('I Love You', 'en', dest_language, gtranslateApiKey)
    fulltextmsg = randomquote + " \n P.S. " + msg

    loved_ones = {'seyi': '+26878514450'}

    for key, value in loved_ones.items():
        message = client.messages.create(
                                    body="Dear " + key + ",\n" + fulltextmsg,
                                    from_='whatsapp:+14155238886',
                                    to='whatsapp:' + value
                                )
        
    return {
        'statusCode': 200,
        'body': message.sid
    }
