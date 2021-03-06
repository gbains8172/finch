from flask import Flask, jsonify, render_template, request
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json


# google cloud constants
CRED = credentials.Certificate("/Users/adithya/Desktop/big-finch-f2bb0512347f.json")   # Use the application default credentials
COLLECTION_ID = 'immigrants'

# XPRING Constants
XPRING_HEADERS = {
    'Authorization': 'Bearer c79kaiqjjf6fudu3329wek',
    'Content-Type': 'application/json',
}
XPRING_URL = "http://localhost:3000/v1"
SOURCEADDR = "rUUwxDuTwFNS9Zr9dFq2A285nzsnWd8MXq"
DESTADDR = "rY7juXVg78bWvqmnSieAbfJywkf72HViN"

# chatbot constants
IMMIGRANT_DATA = {
    'name': '',
    'alien_id': '',
    'date_of_birth': '',
    'det_center': '',
    'country_of_origin': '',
    'point_of_contact': '',
    'spoken_languages': '',
    'preferred_language': '',
    'written_language': '',
    'prev_council': ''
}

# initialize firebase
firebase_admin.initialize_app(CRED, {
  'projectId': "finch-b50f9",
})
db = firestore.client()

# initialize flask
app = Flask(__name__)


# default route
@app.route('/')
def index():
    return 'Hello World!'

# create a route for webhook
@app.route('/webhook', methods=['GET', 'POST'])
def webhook_main():

    data = request.get_json(force=True)
    action = data['queryResult']['action']
    fulfillmentText = 'We are working on getting a solution...'


    print("~~~~~YOU HAVE GOTTEN A RESPONSE~~~~~~~~")
    print(action)

    if action == 'input.welcome':
        name = data['queryResult']['parameters']['name'][0]
        a_id = data['queryResult']['parameters']['alien_id'][0]
        IMMIGRANT_DATA['name'] = name
        IMMIGRANT_DATA['alien_id'] = a_id
        fulfillmentText = 'Hello {}! Nice to meet you. Everything will be ok. Would you like a lawyer to represent you?'.format(name)

        print('~~WELCOME VALUES:')
        print(name, a_id)

    elif action == 'input.request_lawyer':
        date_of_birth = data['queryResult']['parameters']['dob']
        det_center = data['queryResult']['parameters']['det_center']
        country_of_origin = data['queryResult']['parameters']['origin']
        point_of_contact = data['queryResult']['parameters']['point_of_contact']
        IMMIGRANT_DATA['date_of_birth'] = date_of_birth
        IMMIGRANT_DATA['det_center'] = det_center
        IMMIGRANT_DATA['country_of_origin'] = country_of_origin
        IMMIGRANT_DATA['point_of_contact'] = point_of_contact
        fulfillmentText = 'Thank You. This will help a lot. I have a few more questions for you. Do you speak any other languages?'

        print('~~LAWYERS CHOICE VALUES:')
        print(date_of_birth, det_center, country_of_origin)

    elif action == 'input.question_6':
        spoken_languages = data['queryResult']['parameters']['spoken_language']
        IMMIGRANT_DATA['spoken_languages'] = spoken_languages
        fulfillmentText = 'Great! Next question. What language would you like to be interviewed in?'

        print('~~LANGUAGES SPOKEN:')
        print(spoken_languages)

    elif action == 'input.question_7':
        preferred_language = data['queryResult']['parameters']['preferred_language']
        IMMIGRANT_DATA['preferred_language'] = preferred_language
        fulfillmentText = 'We will find someone to interview you in {}. Next question. In which languages can you read?'.format(preferred_language)

        print('~~PREFERRED LANGUAGE:')
        print(preferred_language)

    elif action == 'input.question_8':
        written_language = data['queryResult']['parameters']['written_language']
        IMMIGRANT_DATA['written_language'] = written_language
        fulfillmentText = 'Great! All this information will be sent to a lawyer who will help you. Next Question. Have you ever spoken with or had an attorney represent you before the immigration court?'

        print('~~WRITTEN LANGUAGE:')
        print(written_language)

    elif action == 'input.question_9':
        prev_council = data['queryResult']['parameters']['prev_council']
        IMMIGRANT_DATA['prev_council'] = prev_council
        fulfillmentText = 'Thank you for your time. We will now send this information to a group of lawyers who will try and help you. we hope to help you soon.'

        print('~PREVIOUS COUNCIL?')
        print(prev_council)


    update_db = IMMIGRANT_DATA['alien_id']!='' and IMMIGRANT_DATA['name']!=''
    print(IMMIGRANT_DATA)
    if(update_db):
        print("YOUR IMMIGRANT DATA IS COMPLETE")
        doc_ref = db.collection(u'immigrants').document(u'{}'.format(IMMIGRANT_DATA['alien_id']))
        doc_ref.set({
            u'name': u'{}'.format(IMMIGRANT_DATA['name']),
            u'alien_id': u'{}'.format(IMMIGRANT_DATA['alien_id']),
            u'date_of_birth': u'{}'.format(IMMIGRANT_DATA['date_of_birth']),
            u'country_of_birth': u'{}'.format(IMMIGRANT_DATA['country_of_origin']),
            u'detention_center': u'{}'.format(IMMIGRANT_DATA['det_center']),
            u'point_of_contact':u'{}'.format(IMMIGRANT_DATA['point_of_contact']),
            u'spoken_language': u'{}'.format(IMMIGRANT_DATA['spoken_languages']),
            u'preferred_language': u'{}'.format(IMMIGRANT_DATA['preferred_languages']),
            u'written_language': u'{}'.format(IMMIGRANT_DATA['written_language']),
            u'previous_represented_by_lawyer': u'{}'.format(IMMIGRANT_DATA['prev_council'])
        })
        full = True
        for key in IMMIGRANT_DATA:
            full &= IMMIGRANT_DATA[key]!=''
        if full:
            IMMIGRANT_DATA['name'] = ''
            IMMIGRANT_DATA['alien_id'] = ''
            IMMIGRANT_DATA['date_of_birth'] = ''
            IMMIGRANT_DATA['country_of_origin'] = ''
            IMMIGRANT_DATA['det_center'] = ''
            IMMIGRANT_DATA['point_of_contact'] = ''
            IMMIGRANT_DATA['spoken_languages'] = ''
            IMMIGRANT_DATA['written_language'] = ''
            IMMIGRANT_DATA['prev_council'] = ''
    reimburse(1)
    return {'fulfillmentText': fulfillmentText}


# create a route for getAccount
@app.route('/getAccount')
def getAccount():
    response = requests.get(XPRING_URL + '/accounts/' + SOURCEADDR + '/info')
    return response.json()

# create a route for reimburse
@app.route('/reimburse')
def reimburse(value=2):
    data = {
        "payment": {
            "source_address": SOURCEADDR,
            "source_amount": {
                "value": "{}".format(value),
                "currency": "XRP"
            },
            "destination_address": DESTADDR,
            "destination_amount": {
                "value": "{}".format(value),
                "currency": "XRP"
            }
        },
        "submit": True
    }
    response = requests.post(XPRING_URL + '/payments', headers=XPRING_HEADERS, data=json.dumps(data))
    print(response.json())
    return response.json()

# create a route for laywerfunds
@app.route('/addImmigrant')
# name, alien_id, date_of_birth, country_of_birth, detention_center, spoken_language, written_language, previous_represented_by_lawyer
def addImmigrant():
    doc_ref = db.collection(u'{}'.format(COLLECTION_ID)).document(u'alovelace')
    doc_ref.set({
        u'name': u'Ada Lovelace',
        u'alien_id': u'1234',
        u'date_of_birth': u'1815',
        u'country_of_birth': u'Canada',
        u'detention_center': u'1234',
        u'spoken_language': u'English',
        u'written_language': u'English',
        u'previous_represented_by_lawyer': False,
    })
    return 'ADDED immigrants'

# create a route for laywerfunds
@app.route('/getImmigrants')
# name, alien_id, date_of_birth, country_of_birth, detention_center, spoken_language, written_language, previous_represented_by_lawyer
def getImmigrants():
    users_ref = db.collection(u'immigrants')
    docs = users_ref.stream()
    ans = []
    for doc in docs:
        ans.append(doc.to_dict())
    print(ans)
    return render_template('lawyers.html', immigrants=ans)


@app.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return response



# run the app
if __name__ == '__main__':
   app.run()
