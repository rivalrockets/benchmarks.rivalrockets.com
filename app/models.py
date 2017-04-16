# replacing the authentication model to use a simple token-based approach
from datetime import datetime
from flask import current_app
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
# per http://stackoverflow.com/a/9695045
from flask_sqlalchemy import SQLAlchemy

from . import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))
    machines = db.relationship('Machine', backref='author', lazy='dynamic')

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user


class Machine(db.Model):
    __tablename__ = 'machines'
    id = db.Column(db.Integer, primary_key=True)
    system_name = db.Column(db.Text)
    system_notes = db.Column(db.Text)
    system_notes_html = db.Column(db.Text)
    owner = db.Column(db.Text)
    active_revision_id = db.Column(db.Integer, db.ForeignKey('machines.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    active_revision = db.relationship('Revision',
                                      cascade='all,delete',
                                      backref='active_revision_of',
                                      uselist=False)
    revisions = db.relationship('Revision', cascade='all,delete',
                                backref='machine', lazy='dynamic')


class Revision(db.Model):
    __tablename__ = 'revisions'
    id = db.Column(db.Integer, primary_key=True)
    cpu_make = db.Column(db.String(64))
    cpu_name = db.Column(db.String(64))
    cpu_socket = db.Column(db.String(64))
    cpu_mhz = db.Column(db.Integer)
    cpu_proc_cores = db.Column(db.Integer)
    chipset = db.Column(db.String(64))
    system_memory_gb = db.Column(db.Integer)
    system_memory_mhz = db.Column(db.Integer)
    gpu_name = db.Column(db.String(64))
    gpu_make = db.Column(db.String(64))
    gpu_memory_mb = db.Column(db.Integer)
    gpu_count = db.Column(db.Integer)
    revision_notes = db.Column(db.Text)
    revision_notes_html = db.Column(db.Text)
    pcpartpicker_url = db.Column(db.String)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    machine_id = db.Column(db.Integer, db.ForeignKey('machines.id'))

    cinebenchr15results = db.relationship('CinebenchR15Result',
                                          cascade='all,delete',
                                          backref='revision', lazy='dynamic')
    futuremark3dmark06results = db.relationship('Futuremark3DMark06Result',
                                                cascade='all,delete',
                                                backref='revision',
                                                lazy='dynamic')
    futuremark3dmarkresults = db.relationship('Futuremark3DMarkResult',
                                              cascade='all,delete',
                                              backref='revision',
                                              lazy='dynamic')


class CinebenchR15Result(db.Model):
    __tablename__ = 'cinebenchr15results'
    id = db.Column(db.Integer, primary_key=True)
    result_date = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    cpu_cb = db.Column(db.Integer, index=True)
    opengl_fps = db.Column(db.Integer, index=True)
    revision_id = db.Column(db.Integer, db.ForeignKey('revisions.id'))


class Futuremark3DMark06Result(db.Model):
    __tablename__ = 'futuremark3dmark06results'
    id = db.Column(db.Integer, primary_key=True)
    result_date = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    sm2_score = db.Column(db.Integer, index=True)
    cpu_score = db.Column(db.Integer, index=True)
    sm3_score = db.Column(db.Integer, index=True)
    proxcyon_fps = db.Column(db.Numeric(5,2))
    fireflyforest_fps = db.Column(db.Numeric(5,2))
    cpu1_fps = db.Column(db.Numeric(5,2))
    cpu2_fps = db.Column(db.Numeric(5,2))
    canyonflight_fps = db.Column(db.Numeric(5,2))
    deepfreeze_fps = db.Column(db.Numeric(5,2))
    overall_score = db.Column(db.Integer, index=True)
    result_url = db.Column(db.String)
    revision_id = db.Column(db.Integer, db.ForeignKey('revisions.id'))


class Futuremark3DMarkResult(db.Model):
    __tablename__ = 'futuremark3dmarkresults'
    id = db.Column(db.Integer, primary_key=True)
    result_date = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    icestorm_score = db.Column(db.Integer, index=True)
    icestorm_result_url = db.Column(db.String)
    cloudgate_score = db.Column(db.Integer, index=True)
    cloudgate_result_url = db.Column(db.String)
    firestrike_score = db.Column(db.Integer, index=True)
    firestrike_result_url = db.Column(db.String)
    skydiver_score = db.Column(db.Integer, index=True)
    skydiver_result_url = db.Column(db.String)
    overall_result_url = db.Column(db.String)
    revision_id = db.Column(db.Integer, db.ForeignKey('revisions.id'))
