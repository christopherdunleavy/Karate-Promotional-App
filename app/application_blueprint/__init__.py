from flask import Blueprint, request, flash, redirect, url_for, render_template
from database_setup import Base, Promotional, Application, User
from flask_login import login_required
from app import session 
application_blueprint = Blueprint('application_blueprint', __name__, template_folder='templates')

@application_blueprint.route('/<int:promotional_id>/addApplication', methods=['GET', 'POST'])
@login_required
def addApplication(promotional_id):
    promotional = session.query(Promotional).filter_by(id=promotional_id).one()
    if request.method == 'POST' and promotional.isPromotionalPostdated() == False:
        
        #return error if first name or last name is blank
        if not (request.form['firstName'] and request.form['lastName']):
            flash('First and last name are required', category="error")
            return redirect(url_for('showPromotional', promotional_id=promotional_id))
        
        color = rank_to_belt(int(request.form['rank']))
        
        age = 0
        if request.form['age']:
            age = request.form['age']
        newApplication = Application(
            firstName=request.form['firstName'], lastName=request.form['lastName'], age=age, rank=int(request.form['rank']),
                 color=color, beltSize=request.form['beltSize'], promotional_id=promotional_id, payment=request.form['payment'])
        session.add(newApplication)
        applications = session.query(Application).filter_by(promotional_id=promotional_id).order_by(Application.rank, Application.age).all()
        number = 1  
        for application in applications:
            application.number = number
            session.add(application)
            number += 1

        session.commit()
        flash('%s Added' % newApplication.fullName, category="success")
    
    return redirect(url_for('showPromotional', promotional_id=promotional_id))


@application_blueprint.route('/<int:promotional_id>/<int:application_id>/edit', methods=['GET', 'POST'])
@login_required
def editApplication(promotional_id, application_id):
    editedApplication = session.query(Application).filter_by(id=application_id).one()
    promotional = session.query(Promotional).filter_by(id=promotional_id).one()

    if request.method == 'POST' and promotional.isPromotionalNotExpired():
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
        flash('Edited ' + editedApplication.fullName, category="success")
        return redirect(url_for('showPromotional', promotional_id=promotional_id))
        
    #redirect to promotional view if POST request is for expired promotional
    elif request.method == 'POST':
        return redirect(url_for('showPromotional', promotional_id=promotional_id))
    else:
        return render_template('application/editapplication.html', promotional_id=promotional_id, application_id=application_id, application=editedApplication)

@application_blueprint.route('/<int:promotional_id>/<int:application_id>/delete', methods=['GET', 'POST'])
@login_required
def deleteApplication(promotional_id, application_id):
    deletedApplication = session.query(Application).filter_by(id=application_id).one()
    promotional = session.query(Promotional).filter_by(id=promotional_id).one()

    if request.method == 'POST' and promotional.isPromotionalNotExpired():
        session.delete(deletedApplication)
        applications = session.query(Application).filter_by(promotional_id=promotional_id).order_by(Application.number).all()
        number = 1
        for application in applications:
            application.number = number
            session.add(application)
            number += 1
        session.commit()
        flash('Deleted ' + deletedApplication.fullName, category="success")
        return redirect(url_for('showPromotional', promotional_id=promotional_id))
    elif request.method == 'POST':
         return redirect(url_for('showPromotional', promotional_id=promotional_id))
    else:
        return render_template('application/deleteapplication.html', promotional_id=promotional_id, application_id=application_id, application=deletedApplication)

def rank_to_belt(rank):
    colors = ["yellow","blue","blue","green","green","purple","purple","brown","brown","brown","black",
        "black","black","black","black","black","black","black","black","black"]
    return colors[rank]