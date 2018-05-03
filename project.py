from datetime import date, datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from PyPDF2 import PdfFileReader, PdfFileWriter
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy import create_engine, asc, and_, or_
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Promotional, Application, Pairing, User
from flask import session as login_session
from flask_bcrypt import Bcrypt
import random
import string
import httplib2
import json
from flask import make_response
import requests
import StringIO
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# CLIENT_ID = json.loads(
#     open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Karate Promotional Organizer"

# Connect to Database and create database session
#engine = create_engine('sqlite:///promotional.db')
engine = create_engine(os.environ['DATABASE_URL'])

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

errors = {"1":"Error: Duplicate"}

login_manager = LoginManager()
login_manager.init_app(app)

bcrypt = Bcrypt(app)

@login_manager.user_loader
def load_user(user_id):
    return session.query(User).filter_by(id=user_id).first()
    #return User.query.get(int(user_id))

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['email'] and request.form['password']:
            email = request.form['email']
            password = request.form['password']
            user = session.query(User).filter_by(email=email).first()

            if bcrypt.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('home'))
            else:
                error = "Wrong email or password"
                return render_template('login.html', error=error)

    else:
        return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    if request.method == 'POST':
        logout_user()
        return redirect(url_for('login'))

    else:
        return render_template('logout.html')

#@app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         if not (request.form['firstName'] and request.form['lastName'] and request.form['lastName'] and request.form['password'] and request.form['confirmPassword']):
#             error = "please fill in all fields"
#             return render_template('register.html', error=error)

#         firstName = request.form['firstName']
#         lastName = request.form['lastName']
#         email = request.form['email']
#         password = request.form['password']
#         confirmPassword = request.form['confirmPassword']

#         if password != confirmPassword:
#             error = "passwords don't match"
#             return render_template('register.html', error=error)

#         else:
#             #hash password
#             password = bcrypt.generate_password_hash(password)
#             user = User(firstName=firstName, lastName=lastName, password=password, email=email)
#             session.add(user)
#             session.commit()
#             login_user(user)
#             return redirect(url_for('home'))
#     else:    
#         return render_template('register.html')

@app.route('/')
@app.route('/home')
@login_required
def home():
    promotionals = session.query(Promotional).order_by(asc(Promotional.date))
    return render_template('home.html', title="Shinkyu Shotokan Promotional Builder - user:" + current_user.email, promotionals=promotionals)

@app.route('/addPromotional', methods=['GET', 'POST'])
@login_required
def addPromotional():
    if request.method == 'POST':
        newPromotional = Promotional(
            date=datetime.strptime(request.form['promotionalDate'], '%Y-%m-%d'), type=request.form['type'])
        session.add(newPromotional)
        flash('Promotional created for %s' % (newPromotional.date.strftime("%B %d, %Y") + " - " + newPromotional.type))
        session.commit()
        return redirect(url_for('home'))

@app.route('/<int:promotional_id>/edit', methods=['GET', 'POST'])
@login_required
def editPromotional(promotional_id):
    promotional = session.query(Promotional).filter_by(id=promotional_id).one()

    if request.method == 'POST':
        print "hey"
        if request.form['date']:
            promotional.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        else:
            promotional.date = None
        if request.form['type']:
            promotional.type = request.form['type']
        
        session.add(promotional)
        session.commit()
        flash('Edited ' + (promotional.date.strftime("%B %d, %Y") + " - " + promotional.type))
        return redirect(url_for('home'))
    else:
        return render_template('editpromotional.html', promotional=promotional)

@app.route('/<int:promotional_id>/delete', methods=['GET', 'POST'])
@login_required
def deletePromotional(promotional_id):
    promotional = session.query(Promotional).filter_by(id=promotional_id).one()
    applications = session.query(Application).filter_by(promotional_id=promotional_id).all()
    pairings = session.query(Pairing).filter_by(promotional_id=promotional_id).all()

    if request.method == 'POST':
        session.delete(promotional)
        for pairing in pairings:
            session.delete(pairing)
        for application in applications:
            session.delete(application)
        session.commit()
        flash('Deleted ' + (promotional.date.strftime("%B %d, %Y") + " - " + promotional.type))
        return redirect(url_for('home'))
    else:
        return render_template('deletepromotional.html', promotional_id=promotional_id)

@app.route('/<int:promotional_id>', methods=['GET', 'POST'])
@login_required
def showPromotional(promotional_id):
    promotional = session.query(Promotional).filter_by(id=promotional_id).one()
    applications = session.query(Application).filter_by(promotional_id=promotional_id).order_by(Application.number).all()
    title = promotional.date.strftime("%B %d, %Y") + " - " + promotional.type
    return render_template('promotional.html', title=title, promotional_id=promotional_id, applications=applications)

@app.route('/<int:promotional_id>/<string:color>', methods=['GET', 'POST'])
@login_required
def showPromotionalColor(promotional_id, color):
    promotional = session.query(Promotional).filter_by(id=promotional_id).one()
    applications = session.query(Application).filter_by(promotional_id=promotional_id, color=color).order_by(Application.number).all()
    # unmatchedApplications = session.query(Application).filter_by(promotional_id=promotional_id, color=color, pairingA=None, pairingB=None).order_by(Application.lastName).all()
    # existingPairings = session.query(Pairing).filter_by(promotional_id=promotional_id, color=color).all()
    title = promotional.date.strftime("%B %d, %Y") + " - " + promotional.type + ": " + color

    error = None
    if request.args.get('error') != None:
    	error = errors[request.args.get('error')]

    return render_template('promotional.html', title=title, promotional_id=promotional_id, applications=applications, color=color, error=error)

@app.route('/<int:promotional_id>/orderBelts', methods=['GET', 'POST'])
@login_required
def orderBelts(promotional_id):
    promotional = session.query(Promotional).filter_by(id=promotional_id).one()
    applications = session.query(Application).filter_by(promotional_id=promotional_id).filter(Application.rank.in_([0, 1, 3, 5, 7, 10])).all()
    title = "Belts for " + promotional.date.strftime("%B %d, %Y") + " - " + promotional.type

    orderedSizes = ['----','0000','000','00','0','1','2','3','4','5','6','7','8']
    orderedColors = ['yellow','blue','green','purple','brown','black']

    sizes = {"yellow":{},
	    "blue":{},
	    "green":{},
	    "purple":{},
	    "brown":{},
	    "black":{}
    }

    for application in applications:
    	if application.beltSize in sizes[application.color].keys():
    		sizes[application.color][application.beltSize] += 1
    	else:
    		sizes[application.color][application.beltSize] = 1
    print sizes
    print applications
    return render_template('orderBelts.html', title=title, promotional_id=promotional_id, sizes=sizes, orderedSizes=orderedSizes, orderedColors=orderedColors)

@app.route('/<int:promotional_id>/<string:color>/certificates', methods=['GET', 'POST'])
@login_required
def generateCertificates(promotional_id, color):
    promotional = session.query(Promotional).filter_by(id=promotional_id).one()
    applications = session.query(Application).filter_by(promotional_id=promotional_id, color=color).order_by(Application.lastName).all()
    title = promotional.date.strftime("%B %d, %Y") + " - " + promotional.type + ": " + color

    output = PdfFileWriter()

    date = promotional.date.strftime("%-m/%-d/%Y")


    for application in applications:
        name = application.firstName + " " + application.lastName
        sensei = "Sue Miller, Sensei"
        if application.age > 10:
            sensei = "Sue Miller, Sensei"
            sensei2 = "Nobu Kaji, Sensei"

        certificate = PdfFileReader(open("promotionalCertificate.pdf", "rb"))
        certificatePage = certificate.getPage(0)

        infoBuffer = StringIO.StringIO()

        def drawCertificate(c):
            c.setFont('Helvetica', 24)
            c.drawCentredString(305,452, name.upper())
            c.setFont('Helvetica', 28)
            c.drawCentredString(305,372, (application.rankInfo + " " + application.color.capitalize() + " Belt"))
            c.setFont('Helvetica', 14)
            c.drawString(180,330, date)
            if sensei2:
                c.drawCentredString(194,286, sensei2)
                c.drawCentredString(194,305, sensei)
            else:
                c.drawCentredString(194,286, sensei)
            c.drawString(383,255, "10th Dan")

        c = canvas.Canvas(infoBuffer)

        drawCertificate(c)
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
@login_required
def generateJudgesPackets(promotional_id, color):
    promotional = session.query(Promotional).filter_by(id=promotional_id).one()
    #yellow = session.query(Application).filter_by(promotional_id=promotional_id, color="yellow").order_by(Application.lastName).all()
    applications = session.query(Application).filter_by(promotional_id=promotional_id, color=color).order_by(Application.number).all()
    title = promotional.date.strftime("%B %d, %Y") + " - " + promotional.type + ": " + color

    output = PdfFileWriter()
    
    counter = 0
    previousRank = applications[0].rank

    def generateCoverPage(rank):
        infoBuffer = StringIO.StringIO()
        c = canvas.Canvas(infoBuffer)
        date = promotional.date.strftime("%B %d, %Y")
        cover = PdfFileReader(open("Judges_packet_template.pdf", "rb"))
        coverPage = cover.getPage(0)

        offset = 38
        coverCounter = 0
        for app in applications:
            if app.rank == rank:
                if coverCounter == 0:
                    c.setFont('Helvetica', 24)
                    #Page title
                    c.drawCentredString(300, 735, date)
                    c.drawCentredString(300, 675, app.rankInfo + " " + color.title() + " Belt")
                    #table header
                    c.setFont('Helvetica-Bold', 18)
                    c.drawString(80, 624, app.rankInfo + " " + color.title() + " Belt")

                c.setFont('Helvetica', 24)
                c.drawString(80, 590 - coverCounter*offset, app.fullName)
                #number listing
                c.drawCentredString(330, 590 - coverCounter*offset, str(app.number))
                coverCounter += 1

                if coverCounter == 15:
                    c.showPage()
                    c.save()
                    infoBuffer.seek(0)
                    info = PdfFileReader(infoBuffer)
                    coverPage.mergePage(info.getPage(0))
                    output.addPage(coverPage)
                    infoBuffer.close()

                    infoBuffer = StringIO.StringIO()
                    c = canvas.Canvas(infoBuffer)
                    cover = PdfFileReader(open("Judges_packet_template.pdf", "rb"))
                    coverPage = cover.getPage(0)
                    coverCounter = 0

        c.showPage()
        c.save()
        infoBuffer.seek(0)
        info = PdfFileReader(infoBuffer)
        coverPage.mergePage(info.getPage(0))
        output.addPage(coverPage)
        infoBuffer.close()

    generateCoverPage(previousRank)

    judgesPacket = PdfFileReader(open("RankingSheet.pdf", "rb"))
    judgesPacketPage = judgesPacket.getPage(0)
    infoBuffer = StringIO.StringIO()
    c = canvas.Canvas(infoBuffer)

    for application in applications:
        name = str(application.number) + ") " + application.fullName

        if counter == 4 or previousRank != application.rank:
            counter = 0
            c.showPage()
            c.save()

            infoBuffer.seek(0)
            info = PdfFileReader(infoBuffer)
            judgesPacketPage.mergePage(info.getPage(0))
            output.addPage(judgesPacketPage)
            infoBuffer.close()

            if previousRank != application.rank:
                generateCoverPage(application.rank)

                #create cover page for next rank

            infoBuffer = StringIO.StringIO()
            c = canvas.Canvas(infoBuffer)
            judgesPacket = PdfFileReader(open("RankingSheet.pdf", "rb"))
            judgesPacketPage = judgesPacket.getPage(0)

        if counter == 0:
            c.setFont('Helvetica', 24)
            c.drawCentredString(300, 700, application.rankInfo + " " + color.title() + " Belt")
            c.setFont('Helvetica', 15)
            c.drawCentredString(450, 566, name)
            counter += 1
        elif counter == 1:
            c.setFont('Helvetica', 14)
            c.drawCentredString(450, 417, name)
            counter += 1
        elif counter == 2:
            c.setFont('Helvetica', 14)
            c.drawCentredString(450, 270, name)
            counter += 1
        elif counter == 3:
            c.setFont('Helvetica', 14)
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

@app.route('/<int:promotional_id>/<string:color>/pairings')
@login_required
def showPairings(promotional_id, color):
    applications = session.query(Application).filter_by(promotional_id=promotional_id, color=color).order_by(Application.number).all()
    
    title="Pairings for " + color

    return render_template('pairings.html', title=title, promotional_id=promotional_id, color=color, applications=applications)

@app.route('/<int:promotional_id>/<string:color>/editPairings', methods=['GET', 'POST'])
@login_required
def editPairings(promotional_id, color):
    applications = session.query(Application).filter_by(promotional_id=promotional_id, color=color).order_by(Application.number).all()
    title="Edit Pairings for " + color

    if request.method == 'POST':
        flagged = []
    	for key in request.form:
            partner = request.form[key]
            if partner != 'sub':
                if request.form[partner] != key:
                    if key not in flagged:
                        print "flagged" + key
                        flagged.append(key)
                    if request.form[key] not in flagged:
                        print "flagged" + request.form[key]
                        flagged.append(request.form[key])
         
        if flagged: 
            #pass the form back so that the dropdowns can be set in html
            form = request.form         
            flash('There are either duplicate entries, or students are not partnered up correctly. Please try again.')
            return render_template('editPairings.html', title=title, promotional_id=promotional_id, color=color, applications=applications, form=form, flagged=flagged, str=str)

        for application in applications:
            print (application in flagged)
            application.sideA_id = None
            application.sideB_id = None 

        for application in applications:
            print "test 431"
            if not application.sideB_id and request.form[str(application.id)] != "sub":
                print "test 433"
                sideB = session.query(Application).filter_by(id=request.form[str(application.id)]).one()
                print 'test 435'
                application.sideA_id = sideB.id
                sideB.sideB_id = application.id
                session.add(sideB)
            session.add(application)
        session.commit()
        return redirect(url_for('showPairings', promotional_id=promotional_id, color=color, applications=applications))

    else:
        form = None
    	return render_template('editPairings.html', title=title, form=form, promotional_id=promotional_id, color=color, applications=applications)

@app.route('/<int:promotional_id>/<string:color>/generatePairings')
@login_required
def generatePairings(promotional_id, color):
    #query for all applicants of the selected color belonging to the selected
    #promotional, ordered by number, which is ordered by rank and age
    applications = session.query(Application).filter_by(promotional_id=promotional_id, color=color).order_by(Application.number).all()
 
    #instatiate a PdfFileWriter for output
    output = PdfFileWriter()
    
    #a counter used to count rows in the table and create a new page once
    #the last row on the page has been reached
    # counter = 0

    #a method used to loop through applications of a given rank and create 
    #a pdf page
    promotional = session.query(Promotional).filter_by(id=promotional_id).one()

    date = promotional.date.strftime("%B %d, %Y")

    def generatePairingsPage():
        infoBuffer = StringIO.StringIO()
        c = canvas.Canvas(infoBuffer)
        cover = PdfFileReader(open("Pairings_packet_template.pdf", "rb"))
        coverPage = cover.getPage(0)
        
        previousRank = applications[0].rank
        offset = 38
        coverCounter = 0
        for app in applications:
            # if app.rank == rank:
                if coverCounter == 15 or app.rank != previousRank:
                    c.showPage()
                    c.save()
                    infoBuffer.seek(0)
                    info = PdfFileReader(infoBuffer)
                    coverPage.mergePage(info.getPage(0))
                    output.addPage(coverPage)
                    infoBuffer.close()

                    infoBuffer = StringIO.StringIO()
                    c = canvas.Canvas(infoBuffer)
                    cover = PdfFileReader(open("Pairings_packet_template.pdf", "rb"))
                    coverPage = cover.getPage(0)
                    coverCounter = 0

                if coverCounter == 0:
                    c.setFont('Helvetica', 24)
                    c.drawCentredString(300, 735, date)
                    #Page title
                    c.drawCentredString(300, 675, app.rankInfo + " " + color.title() + " Belt Pairings")
                    #table header
                    c.setFont('Helvetica-Bold', 18)
                    c.drawString(80, 624, app.rankInfo + " " + color.title() + " Belt")

                c.setFont('Helvetica', 18)
                # put "A) " or "B) " depending on whether the application
                # is on side A or B. Same for the pairing partner.
                if app.sideA_id:
                    c.drawString(80, 590 - coverCounter*offset, "A) " + app.fullName)
                    sideB = session.query(Application).filter_by(promotional_id=promotional_id, id=app.sideA_id).one()
                    c.drawString(340, 590 - coverCounter*offset, "B) " + sideB.fullName)
                elif app.sideB_id:
                    c.drawString(80, 590 - coverCounter*offset, "B) " + app.fullName)
                    sideA = session.query(Application).filter_by(promotional_id=promotional_id, id=app.sideB_id).one()
                    c.drawString(340, 590 - coverCounter*offset, "A) " + sideA.fullName)
                else:
                    c.drawString(80, 590 - coverCounter*offset, "A) " + app.fullName)
                    c.drawString(340, 590 - coverCounter*offset, "SUB")
                
                #number listing
                c.drawCentredString(310, 590 - coverCounter*offset, str(app.number))
                
                coverCounter += 1

                previousRank = app.rank

        c.showPage()
        c.save()
        infoBuffer.seek(0)
        info = PdfFileReader(infoBuffer)
        coverPage.mergePage(info.getPage(0))
        output.addPage(coverPage)
        infoBuffer.close()

    generatePairingsPage()

    outputStream = StringIO.StringIO()
    output.write(outputStream)

    pdfOut = outputStream.getvalue()
    outputStream.close()

    fileName = color + " pairings.pdf"

    response = make_response(pdfOut)
    response.headers['Content-Disposition'] = "attachment; filename=" + fileName
    response.mimetype = 'application/pdf'
    return response

@app.route('/<int:promotional_id>/addApplication', methods=['GET', 'POST'])
@login_required
def addApplication(promotional_id):
    if request.method == 'POST':
        color = rank_to_belt(int(request.form['rank']))
        age = 0
        if request.form['age']:
            age = request.form['age']
        newApplication = Application(
            firstName=request.form['firstName'], lastName=request.form['lastName'], age=age, rank=int(request.form['rank']),
                 color=color, beltSize=request.form['beltSize'], promotional_id=promotional_id, payment=request.form['payment'])
        session.add(newApplication)
        flash('%s Added' % newApplication.fullName)
        # flash('New Promotional %s Successfully Created' % newPromotional.name)
        applications = session.query(Application).filter_by(promotional_id=promotional_id).order_by(Application.rank, Application.age).all()
        number = 1
        for application in applications:
            application.number = number
            session.add(application)
            number += 1

        session.commit()
        return redirect(url_for('showPromotional', promotional_id=promotional_id))

@app.route('/<int:promotional_id>/<int:application_id>/edit', methods=['GET', 'POST'])
@login_required
def editApplication(promotional_id, application_id):
    editedApplication = session.query(Application).filter_by(id=application_id).one()
    promotional = session.query(Promotional).filter_by(id=promotional_id).one()

    if request.method == 'POST':
        if request.form['firstName']:
            editedApplication.firstName = request.form['firstName']
        if request.form['lastName']:
            editedApplication.lastName = request.form['lastName']
        if request.form['age']:
            editedApplication.age = request.form["age"]
        if request.form['rank']:
        	editedApplication.rank = int(request.form['rank'])
        	editedApplication.color = rank_to_belt(int(request.form['rank']))
        if request.form['beltSize']:
        	editedApplication.beltSize = request.form['beltSize']
        if request.form['payment']:
            editedApplication.payment = request.form['payment']

        session.add(editedApplication)
        applications = session.query(Application).filter_by(promotional_id=promotional_id).order_by(Application.rank, Application.age).all()
        number = 1
        for application in applications:
            application.number = number
            session.add(application)
            number += 1
            
        session.commit()
        flash('Edited ' + editedApplication.fullName)
        return redirect(url_for('showPromotional', promotional_id=promotional_id))
    else:
        return render_template('editapplication.html', promotional_id=promotional_id, application_id=application_id, application=editedApplication)

@app.route('/<int:promotional_id>/<int:application_id>/delete', methods=['GET', 'POST'])
@login_required
def deleteApplication(promotional_id, application_id):
    deletedApplication = session.query(Application).filter_by(id=application_id).one()
    promotional = session.query(Promotional).filter_by(id=promotional_id).one()

    if request.method == 'POST':
        session.delete(deletedApplication)
        applications = session.query(Application).filter_by(promotional_id=promotional_id).order_by(Application.number).all()
        number = 1
        for application in applications:
            application.number = number
            session.add(application)
            number += 1
        session.commit()
        flash('Deleted ' + deletedApplication.fullName)
        return redirect(url_for('showPromotional', promotional_id=promotional_id))
    else:
        return render_template('deleteapplication.html', promotional_id=promotional_id, application_id=application_id, application=deletedApplication)

def rank_to_belt(rank):
    colors = ["yellow","blue","blue","green","green","purple","purple","brown","brown","brown","black",
        "black","black","black","black","black","black","black","black","black"]
    return colors[rank]

if __name__ == '__main__':

    app.config['SESSION_TYPE'] = 'filesystem'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
