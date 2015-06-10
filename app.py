# coding: utf-8

import logging

from authomatic.extras.flask import FlaskAuthomatic
from authomatic.providers import oauth2
from datetime import datetime, timedelta
from flask import Flask, make_response
from flask import session, request
from flask import render_template, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import gen_salt
from flask_oauthlib.provider import OAuth2Provider

logger = logging.getLogger('authomatic.core')
logger.addHandler(logging.StreamHandler())

app = Flask(__name__, template_folder='templates')
app.config.from_pyfile('application.cfg', silent=False)

db = SQLAlchemy(app)
oauth = OAuth2Provider(app)

fa = FlaskAuthomatic(
    config={
        'fb': {
           'class_': oauth2.Facebook,
           'consumer_key': app.config['CONSUMER_KEY'],
           'consumer_secret': app.config['CONSUMER_SECRET'],
           'scope': ['user_about_me', 'email'],
        },
    },
    secret=app.config['SECRET_KEY'],
    debug=True,
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)


class Client(db.Model):
    client_id = db.Column(db.String(40), primary_key=True)
    client_secret = db.Column(db.String(55), nullable=False)

    user_id = db.Column(db.ForeignKey('user.id'))
    user = db.relationship('User')

    _redirect_uris = db.Column(db.Text)
    _default_scopes = db.Column(db.Text)

    @property
    def client_type(self):
        return 'public'

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []

    def validate_redirect_uri(self, redirect_uri):
        # Chop query string and confirm it's in the list
        redirect_uri = redirect_uri.split('?')[0]
        return redirect_uri in self.redirect_uris
        

class Grant(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')
    )
    user = db.relationship('User')

    client_id = db.Column(
        db.String(40), db.ForeignKey('client.client_id'),
        nullable=False,
    )
    client = db.relationship('Client')

    code = db.Column(db.String(255), index=True, nullable=False)

    redirect_uri = db.Column(db.String(255))
    expires = db.Column(db.DateTime)

    _scopes = db.Column(db.Text)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.String(40), db.ForeignKey('client.client_id'),
        nullable=False,
    )
    client = db.relationship('Client')

    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id')
    )
    user = db.relationship('User')

    # currently only bearer is supported
    token_type = db.Column(db.String(40))

    access_token = db.Column(db.String(255), unique=True)
    refresh_token = db.Column(db.String(255), unique=True)
    expires = db.Column(db.DateTime)
    _scopes = db.Column(db.Text)

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []


class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id')
    )
    user = db.relationship('User')
    assessment_type = db.Column(db.String(40))
    taken = db.Column(db.DateTime)


def current_user():
    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)
    return None


@app.route('/terms-of-use', methods=('GET',))
def termsofuse():
    return render_template('termsofuse.html')


@app.route('/', methods=('GET', 'POST'))
def home():
    user = current_user()
    return render_template('home.html', user=user, session=session,
            cookies=request.cookies)


@app.route('/client', methods=['GET', 'POST'])
def client():
    user = current_user()
    if not user:
        return redirect('/')
    if request.method == 'GET':
        return render_template('register_client.html')
    redirect_uri = request.form.get('redirect_uri', None)
    item = Client(
        client_id=gen_salt(40),
        client_secret=gen_salt(50),
        _redirect_uris=redirect_uri,
        _default_scopes='email',
        user_id=user.id,
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(
        client_id=item.client_id,
        client_secret=item.client_secret,
        redirect_uris=item._redirect_uris
    )


@oauth.clientgetter
def load_client(client_id):
    return Client.query.filter_by(client_id=client_id).first()


@oauth.grantgetter
def load_grant(client_id, code):
    return Grant.query.filter_by(client_id=client_id, code=code).first()


@oauth.grantsetter
def save_grant(client_id, code, request, *args, **kwargs):
    # decide the expires time yourself
    expires = datetime.utcnow() + timedelta(seconds=100)
    grant = Grant(
        client_id=client_id,
        code=code['code'],
        redirect_uri=request.redirect_uri,
        _scopes=' '.join(request.scopes),
        user=current_user(),
        expires=expires
    )
    db.session.add(grant)
    db.session.commit()
    return grant


@oauth.tokengetter
def load_token(access_token=None, refresh_token=None):
    if access_token:
        return Token.query.filter_by(access_token=access_token).first()
    elif refresh_token:
        return Token.query.filter_by(refresh_token=refresh_token).first()


@oauth.tokensetter
def save_token(token, request, *args, **kwargs):
    toks = Token.query.filter_by(
        client_id=request.client.client_id,
        user_id=request.user.id
    )
    # make sure that every client has only one token connected to a user
    for t in toks:
        db.session.delete(t)

    expires_in = token.pop('expires_in')
    expires = datetime.utcnow() + timedelta(seconds=expires_in)

    tok = Token(
        access_token=token['access_token'],
        refresh_token=token['refresh_token'],
        token_type=token['token_type'],
        _scopes=token['scope'],
        expires=expires,
        client_id=request.client.client_id,
        user_id=request.user.id,
    )
    db.session.add(tok)
    db.session.commit()
    return tok


@app.route('/oauth/token', methods=['GET', 'POST'])
@oauth.token_handler
def access_token():
    return None


@app.route('/oauth/authorize', methods=['GET', 'POST'])
@oauth.authorize_handler
def authorize(*args, **kwargs):
    user = current_user()
    if not user:
        return redirect('/')
    # Skip confirmation - return true as if user agreed to
    # let portal give API access to intervetion.
    return True

@app.route('/api/me')
@oauth.require_oauth()
def me():
    user = request.oauth.user
    return jsonify(username=user.username)

@app.route('/api/demographics')
@oauth.require_oauth()
def demographics():
    demographics_data = {
        "id": 854387,
        "name": {
            "given": "Patrick",
            "family": "Testa"
        },
        "birthDate": "1970-06-09",
        "communication": "en-US",
        "telecom": [
            {
                "system": "email",
                "value": "helloworld@movember.com"
            },
            {
                "system": "phone",
                "value": "(123) 456-7890"
            },

        ],
        "status": "registered",
    }
    return jsonify(demographics_data)

@app.route('/api/clinical')
@oauth.require_oauth()
def clinical():
    clinical_data = {
        "TNM-Condition-stage": {
            "summary": "T1 N0 M0"
        },
        "Gleason-score": "2"
    }
    return jsonify(clinical_data)

@app.route('/api/assessments')
@oauth.require_oauth()
def assessments():
    addone = Assessment(
        user_id=request.oauth.user.id,
        assessment_type='test type',
        taken=datetime.now())
    db.session.add(addone)
    db.session.commit()
    aments = Assessment.query.filter_by(
        user_id=request.oauth.user.id
    )
    return jsonify(count=aments.count())

@app.route('/api/portal-wrapper-html')
def portal_wrapper_html():
    html =  """
<div class="container">
    <div class="pull-left nav-logos">
        <!-- Probably need to use absolute links for images -->
        <a href="http://truenth-demo.cirg.washington.edu"><img src="img/logo_truenth.png" /></a>
        <a href="http://us.movember.com"><img src="img/logo_movember.png" /></a>
    </div>

    <div class="pull-right nav-links">
        <a href="#" class="btn btn-default">About</a>
        <a href="#" class="btn btn-default">Help</a>
        <a href="#" class="btn btn-default">My Profile</a>
        <a href="index.html" class="btn btn-default">Log Out</a>
        <form class="navbar-form" role="search">
        <div class="form-group">
            <div class="hide-initial" id="search-box">
                <input type="text" class="form-control" placeholder="Search">
            </div>
        </div>
        <button type="submit" class="btn btn-default show-search"><i class="fa fa-search"></i></button>
      </form>
    </div>
</div>
"""
    resp = make_response(html)
    resp.headers.add('Access-Control-Allow-Origin', '*')
    resp.headers.add('Access-Control-Allow-Headers', 'X-Requested-With')
    return resp

@app.route('/login')
@fa.login('fb')
def login():
    user = current_user()
    if user:
        return redirect('/')
    if fa.result:
        if fa.result.error:
            return fa.result.error.message
        elif fa.result.user:
            if not (fa.result.user.name and fa.result.user.id):
                fa.result.user.update()
            # Success - add or pull this user to/from portal store 
            username = fa.result.user.name
            user = User.query.filter_by(username=username).first()
            if not user:
                user = User(username=username)
                db.session.add(user)
                db.session.commit()
            user_id = user.id
            session['id'] = user_id
            session['fa_user_id'] = fa.result.user.id
            return redirect('/')
    else:
        return fa.response


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0')
