from flask import Flask, render_template, request, redirect, url_for, make_response
from ringobot.serviceData.runner import manual_cripto_sell
from ringobot.db.session import Dashboard, Session, LiveDashboard, Coin
from ringobot.db.configurations import Configurations
from ringobot.db.utils import session_scope
from ringobot.config import USERNAME, PASSWORD, SECRET_KEY
from flask import jsonify
import jwt
from functools import wraps
import time


app = Flask(__name__)


def generate_token(username, expiration=60 * 60 * 24 * 365):
    expiration = int(time.time() + expiration)
    token = jwt.encode(
        {'username': username, 'exp': expiration},
        SECRET_KEY, algorithm='HS256'
    )
    return token


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            # Generate JWT token
            token = generate_token(username)
            # Set token in cookies
            response = make_response(redirect(url_for('home')))
            response.set_cookie('jwt_token', token)
            return response
        else:
            error = 'Invalid username or password'
    return render_template('login.html', error=error)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('jwt_token')
        if not token:
            return redirect(url_for('login'))
        try:
            jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
    return decorated_function


@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('login')))
    response.set_cookie('jwt_token', '', expires=0)
    return response



@app.route('/')
@login_required
def home():
    with session_scope() as db_session:
        dashboard = LiveDashboard.get_active_dashboard(db_session)
        return render_template('index.html', dashboard=dashboard)


@app.route('/history')
@login_required
def history():
    with session_scope() as db_session:
        dashboard = Dashboard.get_dashboard(db_session)
        return render_template('history.html', dashboard=dashboard)



@app.route('/get_active_sessions')
@login_required
def get_active_sessions():
    with session_scope() as db_session:
        sessions = Session.get_active_sessions(db_session)
        serialized_sessions = [session.__dict__ for session in sessions]
        return jsonify(serialized_sessions), 200


@app.route('/get_completed_sessions')
@login_required
def get_completed_sessions():
    with session_scope() as db_session:
        sessions = Session.get_completed_sessions(db_session)
        serialized_sessions = [session.__dict__ for session in sessions]
        return jsonify(serialized_sessions), 200


@app.route('/transactions/<int:session_id>/<string:data_interval>')
@login_required
def transactions(session_id, data_interval):
    with session_scope() as db_session:
        session = Session.get_session_details(db_session, session_id, data_interval)
        return render_template('session.html', session=session, coin_id=session.coin_id, title=session.name)



@app.route('/get_sessions_by_coin_id/<int:coin_id>')
@login_required
def get_sessions_by_coin_id(coin_id):
    with session_scope() as db_session:
        sessions = Session.get_session_by_coin_id(db_session, coin_id)
        serialized_sessions = [session.__dict__ for session in sessions]
        return jsonify(serialized_sessions), 200


@app.route('/manual_sell/<int:session_id>')
@login_required
def manual_sell(session_id):
    with session_scope() as db_session:
        manual_cripto_sell(db_session, session_id)
        return redirect(url_for('home'))


@app.route('/config', methods=['GET', 'POST'])
@login_required
def update_config():
    if request.method == 'POST':
        # Retrieve form data
        allow_buy = request.form['allow_buy']
        allow_sell = request.form['allow_sell']
        budget = request.form['budget']
        tolerance = request.form['tolerance']
        hold_time = request.form['hold_time']
        max_trade = request.form['max_trade']
        with session_scope() as db_session:
            Configurations.update_config(db_session, allow_buy, allow_sell, budget, tolerance, hold_time, max_trade)
        return redirect(url_for('update_config'))  # Redirect to the same page to show updated values

    else:
        with session_scope() as db_session:
            config = Configurations.get_config(db_session)
        return render_template('config.html', config=config)



@app.route('/coins')
@login_required
def coins():
        return render_template('coins.html', coins=coins)



@app.route('/get_coins', methods=['GET', 'POST'])
@login_required
def get_coins():
    with session_scope() as db_session:
        coins = Coin.get_coins(db_session)
        serialized_coins = [coin.__dict__ for coin in coins]
        return jsonify(serialized_coins), 200


@app.route('/update_coins/<int:coin_id>/<int:status>')
@login_required
def update_coins(coin_id, status):
    with session_scope() as db_session:
        Coin.update_status(db_session, coin_id, status)
        return redirect(url_for('coins'))





if __name__ == '__main__':
    app.debug = False
    app.run(host='0.0.0.0', port=5156)
