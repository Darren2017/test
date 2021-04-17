from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from functools import wraps


class Label_Movie(db.Model):
    __tablename__ = 'label_movie'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label_id = db.Column(db.Integer, db.ForeignKey('label.id', ondelete='CASCADE'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id', ondelete='CASCADE'))


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    introduce = db.Column(db.Text, nullable=True)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.Text, nullable=True)
    score = db.Column(db.Float, default=0.0)
    people_num = db.Column(db.Integer, default=0)


class Label(db.Model):
    __tablename__ = 'label'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label_class = db.Column(db.String(50), nullable=False)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = occupation = db.Column(db.String(10))
    age = db.Column(db.Integer, default=0)
    gender = db.Column(db.Integer, default=2)
    occupation = db.Column(db.String(10), default="None")
    password_hash = db.Column(db.String(128))
    role = db.Column(db.Boolean, default=False)
    confirmed = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        raise AttributeError('password is not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=7200):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True

        db.session.add(self)
        return data.get('confirm')

    def check(func):
        @wraps(func)
        def user_check(*args, **kwargs):
            token = request.headers.get('token')
            if not token:
                return jsonify({
                    "msg": "frobidden",
                }), 401
            s = Serializer(current_app.config['SECRET_KEY'])
            try:
                data = s.loads(token)
            except:
                return jsonify({
                    "msg": "token expired"
                }), 401
            uid = data.get('confirm')
            user = User.query.filter_by(id=uid).first()
            if not user:
                return jsonify({
                    "msg": "no such user",
                }), 401
            return func(user, *args, **kwargs)
        return user_check
