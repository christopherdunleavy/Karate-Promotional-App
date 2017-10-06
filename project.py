from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from PyPDF2 import PdfFileReader, PdfFileWriter
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Promotional, Application, Pairing
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import StringIO

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Board Game Catalog Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///promotional.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

errors = {"1":"Error: Duplicate"}

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

@app.route('/home')
def home():
    promotionals = session.query(Promotional).order_by(asc(Promotional.date))
    return render_template('home.html', title="Shinkyu Shotokan Promotional Builder", promotionals=promotionals)

@app.route('/addPromotional', methods=['GET', 'POST'])
def addPromotional():
    if request.method == 'POST':
        newPromotional = Promotional(
            date=request.form['promotionalDate'], type=request.form['type'])
        session.add(newPromotional)
        # flash('New Promotional %s Successfully Created' % newPromotional.name)
        session.commit()
        return redirect(url_for('home'))

@app.route('/<int:promotional_id>', methods=['GET', 'POST'])
def showPromotional(promotional_id):
    promotional = session.query(Promotional).filter_by(id=promotional_id).one()
    applications = session.query(Application).filter_by(promotional_id=promotional_id).order_by(Application.lastName).all()
    title = promotional.date + " - " + promotional.type
    return render_template('promotional.html', title=title, promotional_id=promotional_id, applications=applications)

@app.route('/<int:promotional_id>/<string:color>', methods=['GET', 'POST'])
def showPromotionalColor(promotional_id, color):
    promotional = session.query(Promotional).filter_by(id=promotional_id).one()
    applications = session.query(Application).filter_by(promotional_id=promotional_id, color=color).order_by(Application.lastName).all()
    unmatchedApplications = session.query(Application).filter_by(promotional_id=promotional_id, color=color, pairingA=None, pairingB=None).order_by(Application.lastName).all()
    existingPairings = session.query(Pairing).filter_by(promotional_id=promotional_id, color=color).all()
    title = promotional.date + " - " + promotional.type + ": " + color

    error = None
    if request.args.get('error') != None:
    		error = errors[request.args.get('error')] 

    def makeSelect(selected, name):
        if selected != None:
            select = "<select name='%s'>" % name
            endSelect = "</select>"

            for application in applications:
                fullName = application.fullName
                value = application.id
                if application == selected:
                    option = "<option value='%s' selected>%s</option>" % (value, fullName)
                else:
                    option = "<option value='%s'>%s</option>" % (value, fullName)
                select = select + option

            select = select + endSelect
        else:
            select = None
        return select
    
    pairings = []
    for pairing in existingPairings:
        sideA = pairing.application_A
        sideB = pairing.application_B

        if sideB == None and len(unmatchedApplications) > 0:
            sideB = unmatchedApplications.pop(0)

        tup = {"sideA":makeSelect(sideA, str(existingPairings.index(pairing)) + "sideA"),"sideB":makeSelect(sideB, str(existingPairings.index(pairing)) + "sideB")}
        print tup
        pairings.append(tup)

    if len(unmatchedApplications) > 0:
        i = 0
        name = len(existingPairings)
        while i < len(unmatchedApplications):
            tup = {"sideA":makeSelect(unmatchedApplications[i], str(name) + "sideA"),"sideB":makeSelect(unmatchedApplications[i+1], str(name) + "sideB") if i+1 < len(unmatchedApplications) else None}
            i += 2
            name += 1
            pairings.append(tup)

    return render_template('promotional.html', title=title, promotional_id=promotional_id, applications=applications, color=color, pairings=pairings, error=error)



@app.route('/<int:promotional_id>/<string:color>/certificates', methods=['GET', 'POST'])
def generateCertificates(promotional_id, color):
    promotional = session.query(Promotional).filter_by(id=promotional_id).one()
    #yellow = session.query(Application).filter_by(promotional_id=promotional_id, color="yellow").order_by(Application.lastName).all()
    applications = session.query(Application).filter_by(promotional_id=promotional_id, color=color).order_by(Application.lastName).all()
    title = promotional.date + " - " + promotional.type + ": " + color

    output = PdfFileWriter()
    
    date = promotional.date

    for application in applications:
        name = application.firstName + " " + application.lastName
        certificate = PdfFileReader(open("promotionalCertificate.pdf", "rb"))
        certificatePage = certificate.getPage(0)
        
        infoBuffer = StringIO.StringIO()
        
        def hello(c):
            c.setFont('Helvetica', 24)
            c.drawCentredString(305,452, name)
            c.setFont('Helvetica', 36)
            c.drawCentredString(305,372, application.rank)
            c.setFont('Helvetica', 15)
            c.drawCentredString(210,330, date)
            c.drawCentredString(200,285,"Sensei Sue, Sensei Nobu")

        c = canvas.Canvas(infoBuffer)

        hello(c)
        c.showPage()
        c.save()
        
        infoBuffer.seek(0)
        info = PdfFileReader(infoBuffer)
        certificatePage.mergePage(info.getPage(0))
        output.addPage(certificatePage)
        infoBuffer.close()

    outputStream = StringIO.StringIO()
    output.write(outputStream)

    pdfOut = outputStream.getvalue()
    outputStream.close()
    
    fileName = color + " certificates.pdf"
    
    response = make_response(pdfOut)
    response.headers['Content-Disposition'] = "attachment; filename=" + fileName
    response.mimetype = 'application/pdf'
    return response

    #return render_template('promotional.html', title=title, promotional_id=promotional_id, applications=applications, color=color)

@app.route('/<int:promotional_id>/<string:color>/judgesPackets', methods=['GET', 'POST'])
def generateJudgesPackets(promotional_id, color):
    promotional = session.query(Promotional).filter_by(id=promotional_id).one()
    #yellow = session.query(Application).filter_by(promotional_id=promotional_id, color="yellow").order_by(Application.lastName).all()
    applications = session.query(Application).filter_by(promotional_id=promotional_id, color=color).order_by(Application.lastName).order_by(Application.rank).all()
    title = promotional.date + " - " + promotional.type + ": " + color

    output = PdfFileWriter()
    infoBuffer = StringIO.StringIO()
    c = canvas.Canvas(infoBuffer)
    date = promotional.date
    judgesPacket = PdfFileReader(open("RankingSheet.pdf", "rb"))
    judgesPacketPage = judgesPacket.getPage(0)
    counter = 0
    previousRank = applications[0].rank

    for application in applications:
        name = application.firstName + " " + application.lastName

        if counter == 4 or previousRank != application.rank:
            counter = 0
            c.showPage()
            c.save()

            infoBuffer.seek(0)
            info = PdfFileReader(infoBuffer)
            judgesPacketPage.mergePage(info.getPage(0))
            output.addPage(judgesPacketPage)
            infoBuffer.close()

            infoBuffer = StringIO.StringIO()
            c = canvas.Canvas(infoBuffer)
            judgesPacket = PdfFileReader(open("RankingSheet.pdf", "rb"))
            judgesPacketPage = judgesPacket.getPage(0)

        if counter == 0:
            c.setFont('Helvetica', 24)
            c.drawCentredString(300, 700, application.rank + " " + color.title() + " Belt")
            c.setFont('Helvetica', 12)
            c.drawCentredString(450, 566, name)
            counter += 1
        elif counter == 1:
            c.setFont('Helvetica', 12)
            c.drawCentredString(450, 417, name)
            counter += 1
        elif counter == 2:
            c.setFont('Helvetica', 12)
            c.drawCentredString(450, 270, name)
            counter += 1
        elif counter == 3:
            c.setFont('Helvetica', 12)
            c.drawCentredString(450, 115, name)
            counter += 1

        if applications.index(application) == len(applications)-1:
            counter = 0
            c.showPage()
            c.save()

            info = PdfFileReader(infoBuffer)
            judgesPacketPage.mergePage(info.getPage(0))
            output.addPage(judgesPacketPage)

            infoBuffer = StringIO.StringIO()

        previousRank = application.rank
        # infoBuffer.seek(0)
        # info = PdfFileReader("output.pdf")
        # judgesPacketPage.mergePage(info.getPage(0))
        # output.addPage(judgesPacketPage)
        #infoBuffer.close()

    outputStream = StringIO.StringIO()
    output.write(outputStream)

    pdfOut = outputStream.getvalue()
    outputStream.close()

    fileName = color + " judgesPacket.pdf"

    response = make_response(pdfOut)
    response.headers['Content-Disposition'] = "attachment; filename=" + fileName
    response.mimetype = 'application/pdf'
    return response
    #return render_template('promotional.html', title=title, promotional_id=promotional_id, applications=applications, color=color)

@app.route('/<int:promotional_id>/<string:color>/pairings', methods=['GET', 'POST'])
def updatePairings(promotional_id, color):
    if request.method == 'POST':
        print request.form
        session.query(Pairing).delete()

        existingApplications = []
        error = "1"
        i = 0
        while i <= len(request.form)/2:
            sideA_id=request.form[str(i)+"sideA"]

            if sideA_id in existingApplications:
            	return redirect(url_for('showPromotionalColor', promotional_id=promotional_id, color=color, error=error))

            existingApplications.append(sideA_id)

            if (str(i)+"sideB") in request.form:
                sideB_id=request.form[str(i)+"sideB"] 
                if sideB_id in existingApplications:
            		return redirect(url_for('showPromotionalColor', promotional_id=promotional_id, color=color, error=error))
            	existingApplications.append(sideB_id)
            else:
                sideB_id = None
            newPairing = Pairing(promotional_id=promotional_id, sideA_id=sideA_id, sideB_id=sideB_id, color=color)
            session.add(newPairing)
            i += 1

        session.commit()
        return redirect(url_for('showPromotionalColor', promotional_id=promotional_id, color=color, error=None))


@app.route('/<int:promotional_id>/addApplication', methods=['GET', 'POST'])
def addApplication(promotional_id):
    if request.method == 'POST':
        color = rank_to_belt(request.form['rank'])
        newApplication = Application(
            firstName=request.form['firstName'], lastName=request.form['lastName'], birthDate=request.form['birthDate'], rank=request.form['rank'],
                 color=color, promotional_id=promotional_id)
        session.add(newApplication)
        # flash('New Promotional %s Successfully Created' % newPromotional.name)
        session.commit()
        return redirect(url_for('showPromotional', promotional_id=promotional_id))

def rank_to_belt(argument):
    switcher = {
        "10thkyu": "yellow",
        "9thkyu": "blue",
        "8thkyu": "blue",
        "7thkyu": "green",
        "6thkyu": "green",
        "5thkyu": "purple",
        "4thkyu": "purple",
        "3rdkyu": "brown",
        "2ndkyu": "brown",
        "1stkyu": "brown",
        "1stdan": "black",
        "2nddan": "black",
        "3rddan": "black",
        "4thdan": "black",
        "5thdan": "black",
        "6thdan": "black",
        "7thdan": "black",
        "8thdan": "black",
        "9thdan": "black",
        "10thdan": "black"
    }
    return switcher.get(argument, "nothing")























# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    data = json.loads(result)

    # Extract the access token from response
    token = 'access_token=' + data['access_token']


    url = 'https://graph.facebook.com/v2.9/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
                json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Publisher Information
@app.route('/publishers/<int:publisher_id>/games/JSON')
def publisherJSON(publisher_id):
    publisher = session.query(Publisher).filter_by(id=publisher_id).one()
    games = session.query(Game).filter_by(publisher_id=publisher_id).all()
    return jsonify(games=[g.serialize for g in games])

@app.route('/games/JSON')
def gamesJSON():
    games = session.query(Game).all()
    return jsonify(games=[g.serialize for g in games])

@app.route('/publishers/<int:publisher_id>/games/<int:game_id>/JSON')
def gameJSON(publisher_id, game_id):
    game = session.query(Game).filter_by(id=game_id).one()
    return jsonify(game=game.serialize)


@app.route('/publishers/JSON')
def publishersJSON():
    publishers = session.query(Publisher).all()
    return jsonify(publishers=[p.serialize for p in publishers])

####
#Do JSON stuff above later
####

# Show all publishers

@app.route('/publishers/')
def showPublishers():
    publishers = session.query(Publisher).order_by(asc(Publisher.name))
    if 'username' not in login_session:
        return render_template('publicpublishers.html', publishers=publishers)
    else:
        return render_template('publishers.html', publishers=publishers)

# Create a new publisher


@app.route('/publishers/new/', methods=['GET', 'POST'])
def newPublisher():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newPublisher = Publisher(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newPublisher)
        flash('New Publisher %s Successfully Created' % newPublisher.name)
        session.commit()
        return redirect(url_for('showPublishers'))
    else:
        return render_template('newpublisher.html')

# Edit a publisher


@app.route('/publishers/<int:publisher_id>/edit/', methods=['GET', 'POST'])
def editPublisher(publisher_id):
    editedPublisher = session.query(Publisher).filter_by(id=publisher_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedPublisher.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('That's an illegal move.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedPublisher.name = request.form['name']
            flash('Publisher Successfully Edited %s' % editedPublisher.name)
            return redirect(url_for('showPublishers'))
    else:
        return render_template('editpublisher.html', publisher=editedPublisher)


# Delete a publisher
@app.route('/publishers/<int:publisher_id>/delete/', methods=['GET', 'POST'])
def deletePublisher(publisher_id):
    publisherToDelete = session.query(
        Publisher).filter_by(id=publisher_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if publisherToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('That's an illegal move.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(publisherToDelete)
        flash('%s Successfully Deleted' % publisherToDelete.name)
        session.commit()
        return redirect(url_for('showPublishers', publisher_id=publisher_id))
    else:
        return render_template('deletepublisher.html', publisher=publisherToDelete)

# Show a publisher's games


@app.route('/publishers/<int:publisher_id>/')
@app.route('/publishers/<int:publisher_id>/games/', methods=['GET', 'POST'])
def showPublisher(publisher_id):
    publisher = session.query(Publisher).filter_by(id=publisher_id).one()
    creator = getUserInfo(publisher.user_id)

    #Sorting the publisher's games is done by submitting a post request.
    #The variable "order" stores the sorting option chosen from a drop down menu.
    #This variable is then passed into SQLAlchemy's order_by() function, which accepts
    #a column name as a parameter. The options in the drop down menu are all column
    #names in the Game table, except for "min_price" and "max_price." If either
    #of these options is selected, the order variable is set to "price," which
    #is a valid column name. Similar code appears in the showGames() method.
    if request.method == 'POST':
        if "price" in request.form['order']:
            order = "price"
        else:
            order = request.form['order']

        games = session.query(Game).filter_by(publisher_id=publisher_id).order_by(order).all()

        #If sorting by a max value, the list is set the descending order.
        if "max" in request.form['order']:
            games.reverse()

    else:
        games = session.query(Game).filter_by(publisher_id=publisher_id).all()
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicpublisher.html', games=games, publisher=publisher, creator=creator)
    else:
        return render_template('publisher.html', games=games, publisher=publisher, creator=creator)

@app.route('/', methods=['GET', 'POST'])
@app.route('/games/', methods=['GET', 'POST'])
def showGames():
    if request.method == 'POST':
        if "price" in request.form['order']:
            order = "price"
        else:
            order = request.form['order']

        games = session.query(Game).order_by(order).all()

        if "max" in request.form['order']:
            games.reverse()
    else:
        games = session.query(Game).all()

    return render_template('games.html', games=games)

# Create a new game
@app.route('/publishers/<int:publisher_id>/games/new/', methods=['GET', 'POST'])
def newGame(publisher_id):
    if 'username' not in login_session:
        return redirect('/login')
    publisher = session.query(Publisher).filter_by(id=publisher_id).one()
    if login_session['user_id'] != publisher.user_id:
        return "<script>function myFunction() {alert('That's an illegal move.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        newGame = Game(name=request.form['name'], description=request.form['description'], price=float(request.form[
                           'price']), min_players=int(request.form['min_players']), max_players=int(request.form['max_players']),
                           min_length=int(request.form['min_length']), max_length=int(request.form['max_length']), publisher_id=publisher_id, user_id=publisher.user_id)
        session.add(newGame)
        session.commit()
        flash('New game "%s" Successfully Created' % (newGame.name))
        return redirect(url_for('showPublisher', publisher_id=publisher_id))
    else:
        return render_template('newgame.html', publisher_id=publisher_id)

# Edit a game


@app.route('/publishers/<int:publisher_id>/games/<int:game_id>/edit', methods=['GET', 'POST'])
def editGame(publisher_id, game_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedGame = session.query(Game).filter_by(id=game_id).one()
    publisher = session.query(Publisher).filter_by(id=publisher_id).one()
    if login_session['user_id'] != publisher.user_id:
        return "<script>function myFunction() {alert('That's an illegal move.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedGame.name = request.form['name']
        if request.form['description']:
            editedGame.description = request.form['description']
        if request.form['price']:
            editedGame.price = float(request.form['price'])
        if request.form['min_length']:
            editedGame.min_length = int(request.form['min_length'])
        if request.form['max_length']:
            editedGame.max_length = int(request.form['max_length'])
        if request.form['min_players']:
            editedGame.min_players = int(request.form['min_players'])
        if request.form['max_players']:
            editedGame.max_players = int(request.form['max_players'])
        session.add(editedGame)
        session.commit()
        flash('Game Successfully Edited')
        return redirect(url_for('showPublisher', publisher_id=publisher_id))
    else:
        return render_template('editgame.html', publisher_id=publisher_id, game_id=game_id, game=editedGame)


# Delete a game
@app.route('/publishers/<int:publisher_id>/games/<int:game_id>/delete', methods=['GET', 'POST'])
def deleteGame(publisher_id, game_id):
    if 'username' not in login_session:
        return redirect('/login')
    publisher = session.query(Publisher).filter_by(id=publisher_id).one()
    gameToDelete = session.query(Game).filter_by(id=game_id).one()
    if login_session['user_id'] != publisher.user_id:
        return "<script>function myFunction() {alert('That's an illegal move.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(gameToDelete)
        session.commit()
        flash('Game Successfully Deleted')
        return redirect(url_for('showPublisher', publisher_id=publisher_id))
    else:
        return render_template('deletegame.html', game=gameToDelete)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showPublishers'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showPublishers'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
