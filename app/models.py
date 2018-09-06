# replacing the authentication model to use a simple token-based approach
from datetime import datetime
from flask import current_app
from passlib.apps import custom_app_context as pwd_context
# per http://stackoverflow.com/a/9695045
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import pbkdf2_sha256 as sha256

from . import db

class Permission:
    POST = 0x01 # 0000 0001 (update)
    PUT = 0x02 # 0000 0010 (create)
    DELETE = 0x04 # 0000 0100
    ADMINISTER = 0x80 # 1000 0000 (all?)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            # user can create and update
            'User': (Permission.POST |
                     Permission.PUT, True),
            'Maintainer': (Permission.POST |
                           Permission.PUT |
                           Permission.DELETE, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

        def __repr__(self):
            return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True, unique=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    machines = db.relationship('Machine', backref='author', lazy='dynamic')

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username = username).first()


class RevokedToken(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key = True)
    jti = db.Column(db.String(120))

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti = jti).first()
        return bool(query)


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
    user = db.relationship(User, lazy="joined", innerjoin=True)

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
