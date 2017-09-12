
@app.route('/games/', methods=['GET', 'POST'])
def showGames():
    if request.method == 'POST':
        if "price" in request.form['order']:
            order = "price"
        else:
            order = request.form['order']
        if "max" in request.form['order']:
            games = session.query(Game).order_by(order).all()
            games.reverse()
        else:
            games = session.query(Game).order_by(order).all() 

    else:
        games = session.query(Game).all() 
    if 'username' not in login_session:
        return render_template('publicgames.html', games=games)
    else:
        return render_template('games.html', games=games)