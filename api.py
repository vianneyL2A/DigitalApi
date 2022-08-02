from cmath import log
from datetime import date, datetime
from email.policy import default
from enum import unique
import json
from lib2to3.pgen2.token import OP
import os
from socket import socket
import string
from tkinter.messagebox import NO
from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import true, values
from flask_cors import CORS
from flask_socketio import SocketIO
from sqlalchemy import desc
from sqlalchemy.sql import func
load_dotenv()


app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

motdepasse = os.getenv(quote_plus('password'))

#connexion db
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:{}@localhost:5432/digitalcompte".format(motdepasse)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#instance
db = SQLAlchemy(app)

#Création des classes

class Pdv(db.Model):
    __tablename__ = 'pdvs'
    idPdv = db.Column(db.Integer, primary_key=True)
    nomPDV = db.Column(db.String(20), unique=True)
    gerant = db.Column(db.String(50), nullable=False)
    adresse = db.Column(db.String(100), nullable=False)
    caisse = db.Column(db.Integer, default=0)
    proprietaire_nump = db.Column(db.String(8), db.ForeignKey('proprietaires.nump'), nullable=False)
    gerants = db.relationship('Gerant', backref='pdvs', cascade="all,delete", lazy=True)

    def __init__(self, nomPDV, gerant, adresse, proprietaire_nump):
        self.nomPDV = nomPDV
        self.gerant = gerant
        self.adresse = adresse
        self.proprietaire_nump = proprietaire_nump
    
    def insert(self):
        db.session.add(self)
        db.session.commit()
        
    def update(self):
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    def format(self):
        return {
            'id' : self.idPdv,
            'nomPDV' : self.nomPDV,
            'gerant' : self.gerant,
            'adresse' : self.adresse,
            'caisse' : self.caisse,
            'numeroP' : self.proprietaire_nump
        }
        

class Proprietaire(db.Model):
    __tablename__ = 'proprietaires'
    nump = db.Column(db.String(8), primary_key=True)
    password_p = db.Column(db.String(20), nullable =False)
    pdv = db.relationship('Pdv', backref='propietaires', lazy=True)
    gerant = db.relationship('Gerant', backref='propietaires', lazy=True)

    def __init__(self, nump, password_p):
        self.numero_p = nump,
        self.password_p = password_p
        
    def insert(self):
        db.session.add(self)
        db.session.commit()
        
    def update(self):
        db.session.commit()
    
    def delete(self) :
        db.session.delete(self)
        db.session.commit()
        
    def format(self) :
        return {
            'numero' : self.nump,
            'pass'  : self.password_p
        }

class Gerant(db.Model):
    __tablename__ = 'gerants'
    idG = db.Column(db.String(20), primary_key=True)
    nom_g = db.Column(db.String(50), nullable=False)
    prenom_g = db.Column(db.String(50), nullable=False)
    password_g = db.Column(db.String(20), nullable = False)
    actif = db.Column(db.Boolean, default=False)
    pdv_idPdv = db.Column(db.Integer, db.ForeignKey('pdvs.idPdv'), nullable=False)
    proprietaire_nump = db.Column(db.String(8), db.ForeignKey('proprietaires.nump'), nullable=False)
    operation = db.relationship('Operation', cascade="all,delete", backref='gerants')

    def __init__(self, idG, nom_g, prenom_g, password_g, actif, pdv_idPdv, proprietaire_nump):
        self.idG = idG
        self.nom_g = nom_g
        self.prenom_g = prenom_g
        self.password_g = password_g
        self.actif = actif
        self.pdv_idPdv = pdv_idPdv
        self.proprietaire_nump = proprietaire_nump
    
    def insert(self):
        db.session.add(self)
        db.session.commit()
        
    def update(self):
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    def format(self):
        return {
            'id_g' : self.idG,
            'nom_g' : self.nom_g,
            'prenom_g' : self.prenom_g,
            'password_g' : self.password_g,
            'acces' : self.actif,
            'idPdv' : self.pdv_idPdv,
            'nump' : self.proprietaire_nump
        }

class Service(db.Model):
    __tablename__ = 'services'
    idS = db.Column(db.Integer, primary_key=True)
    libelle_s = db.Column(db.String(30), nullable=False, unique=True)
    img_s = db.Column(db.String(30), nullable=False)
    servicePdv = db.relationship('ServicePdv', backref='services')

    def __init__(self, libelle_s, img_s):
        self.libelle_s = libelle_s
        self.img_s= img_s
    
    def insert(self):
        db.session.add(self)
        db.session.commit()
        
    def update(self):
        db.session.commit()
        
    def format(self):
        return {
            'id_s' : self.idS,
            'libelle_s' : self.libelle_s,
            'img_s': self.img_s
        }

class ServicePdv(db.Model):
    __tablename__ = 'servicePdvs'
    idSpdv = db.Column(db.Integer, primary_key=True)
    idPdv = db.Column(db.Integer, db.ForeignKey('pdvs.idPdv'), nullable=False)
    uv = db.Column(db.Integer, default = 0)
    service_idS = db.Column(db.Integer, db.ForeignKey('services.idS'), nullable=False)
    operation = db.relationship('Operation', cascade="all,delete" ,backref='servicePdvs')

    def __init__(self, idPdv, service_idS):
        self.idPdv = idPdv
        self.service_idS = service_idS
        
    
    def insert(self):
        db.session.add(self)
        db.session.commit()
        
    def update(self):
        db.session.commit()
        
    def format(self):
        return {
            'idSpdv' : self.idSpdv,
            'idPdv' : self.idPdv,
            'uv' : self.uv,
            'id_s' : self.service_idS
        }

class TypeOp(db.Model):
    __tablename__='typeops'
    libelle = db.Column(db.String(20), primary_key=True)
    payer = db.Column(db.Boolean, default=False)
    typeOp = db.relationship('Operation', backref='typeops')

    def __init__(self, libelle):
        self.libelle = libelle

    def insert(self):
        db.session.add(self)
        db.session.commit()
        
    def update(self):
        db.session.commit()
        
    def format(self):
        return {
            'libelle': self.libelle
        }


class Operation(db.Model):
    __tablename__ = 'operations'
    id_op = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(8), nullable = False)
    montant = db.Column(db.Integer, nullable = False)
    commission = db.Column(db.Integer, nullable = False)
    Solde_uv = db.Column(db.Integer, nullable = False)
    Solde_caisse = db.Column(db.Integer, nullable=False)
    date_operation = db.Column(db.String(12), nullable=False)
    typeOp_libelle = db.Column(db.String(20), db.ForeignKey('typeops.libelle'), nullable=False)
    idSpdv = db.Column(db.Integer, db.ForeignKey('servicePdvs.idSpdv'), nullable=False)
    gerant_idG = db.Column(db.String(20), db.ForeignKey('gerants.idG'), nullable=False)

    def __init__(self, numero, montant, commission, Solde_uv, Solde_caisse, date_operation, typeOp_libelle, idSpdv, gerant_idG):
        self.numero = numero
        self.montant = montant
        self.commission = commission
        self.Solde_uv = Solde_uv
        self.Solde_caisse= Solde_caisse
        self.date_operation = date_operation
        self.typeOp_libelle = typeOp_libelle
        self.idSpdv = idSpdv
        self.gerant_idG = gerant_idG
    
    def insert(self):
        db.session.add(self)
        db.session.commit()
        
    def update(self):
        db.session.commit()
        
    def format(self):
        return {
            'id_op' : self.id_op,
            'numero' : self.numero,
            'montant' : self.montant,
            'com': self.commission,
            'uv': self.Solde_uv,
            'caisse': self.Solde_caisse,
            'date_operation': self.date_operation,
            'type_op': self.typeOp_libelle,
            'id_servicePdv' : self.idSpdv,
            'id_g' : self.gerant_idG
        }

db.create_all()

def depot_uv(montant, commission, Spdv):
        solde_uv = (Spdv.uv-montant)+commission
        Spdv.uv = solde_uv
        Spdv.update()
        return solde_uv

def depot_caisse(montant, pdv):
        solde_caisse = pdv.caisse+montant
        pdv.caisse = solde_caisse
        pdv.update()
        return solde_caisse

def retrait_uv(montant, commission, Spdv):
    solde_uv = (Spdv.uv+montant)+commission
    Spdv.uv = solde_uv
    Spdv.update()
    return solde_uv

def retrait_caisse(montant, pdv):
        solde_caisse = pdv.caisse-montant
        pdv.caisse = solde_caisse
        pdv.update()
        return solde_caisse

@app.route('/operations', methods=['POST'])
def addOperation():
    body= request.get_json()
    idSpdv = body.get('idSpdv')
    numero = body.get('numero')
    montant = body.get('montant')
    commission = body.get('commission')
    libelle = body.get('type_op')
    Date = body.get("date_operation")
    idG = body.get('id_g')
    Spdv = ServicePdv.query.get(idSpdv)
    pdv = Pdv.query.get(Spdv.idPdv)
    if Spdv.uv == 0 or pdv.caisse == 0:
        return jsonify({
            'success': False,
            'erreur': 'solde caisse ou sole uv non attribué'
        })
    elif libelle == 'D':
        if Spdv.uv>montant :
            uv=depot_uv(montant, commission, Spdv)
            caisse=depot_caisse(montant, pdv)

            operation= Operation(numero=numero, montant=montant, commission=commission,
            Solde_uv=uv, Solde_caisse=caisse, date_operation=Date, typeOp_libelle=libelle,
            idSpdv=idSpdv, gerant_idG=idG)
            operation.insert()
            return jsonify({
                'operation': operation.format()
            })
        else:
            return jsonify({
            'success': False,
            'erreur': "solde UV insuffisant pour l'opperation"
        })
    elif libelle == 'R':
        if pdv.caisse>montant:
            uv=retrait_uv(montant, commission, Spdv)
            caisse=retrait_caisse(montant, pdv)

            operation= Operation(numero=numero, montant=montant, commission=commission,
            Solde_uv=uv, Solde_caisse=caisse, date_operation=Date, typeOp_libelle=libelle,
            idSpdv=idSpdv, gerant_idG=idG)
            operation.insert()
            return jsonify({
                'operation': operation.format()
            })
        else : 
            return jsonify({
            'success': False,
            'erreur': "solde caisse insuffisant pour l'opperation"
        })


@app.route('/operations/<string:id>', methods=['GET'])
def getalloperation(id):
    operation =  Operation.query.filter_by(gerant_idG=id).order_by(Operation.date_operation.desc())
    op = [i.format() for i in operation]
    return jsonify({
        'operation' : op
    })

@app.route('/service/<int:id>/operations', methods=['GET'])
def getaloperation(id):
    servicePdv =  ServicePdv.query.get(id)
    service =  Service.query.filter_by(idS=servicePdv.service_idS).first()
    operation =  Operation.query.filter_by(idSpdv=servicePdv.idSpdv).order_by(Operation.date_operation.desc())

    op = [i.format() for i in operation]
    return jsonify({
        'operation' : op,
        'service' : service.format()
    })

@app.route('/com/<string:idG>', methods=['Get'])
def commission(idG):
    operation = Operation.query.with_entities(func.sum(Operation.commission).label("total_com")).filter_by(gerant_idG=idG)
    for op in operation : 
     return jsonify({
         'total' :  op.total_com
    })


@app.route('/gerant/<string:idG>/operations', methods=['GET'])
def getOperation(idG):
    operation =  Operation.query.filter_by(gerant_idG=idG, date_operation=datetime.now().strftime('%d-%m-%Y'))
    op = [i.format() for i in operation]
    return jsonify({
        'operation' : op
    }) 



@app.route('/', methods=['POST'])
def connexion():
    body = request.get_json()
    num = body.get('numero_p')
    passw = body.get('password_p')
    test = Proprietaire.query.get(num)
    if test is None:
        return jsonify({
            'success': False
    })
    elif test.password_p == passw:
        return jsonify({
            'success': True
    })
    else:
        return jsonify({
            'success': False
    })

@app.route('/g', methods=['POST'])
def connexiong():
    body = request.get_json()
    id = body.get('id_g')
    passw = body.get('pass_g')
    test = Gerant.query.get(id)
    if test is None:
        abort(404)
    elif test.password_g == passw:
        if test.actif :
            return jsonify({
            'success': True,
            'gerant' : test.format()
            })
        else:
             return jsonify({
            'success': "Compte non activé"
            })
    else:
        return jsonify({
            'success': False
    })



@app.route('/services', methods = ['POST'])
def add_services():
        body = request.get_json()
        Libelle = body.get('libelle_s')
        Img = body.get('img_s')
        serv = Service(libelle_s=Libelle, img_s=Img)
        serv.insert()
        return jsonify({
            'service' : serv.format(),
            'Total'     : Service.query.count()
        })

@app.route('/services', methods=['GET'])
def getAllServices():
    service =  Service.query.all()
    serv = [i.format() for i in service]
    return jsonify({
        'service' : serv
    }) 

@app.route('/services/<int:id>', methods=['GET'])
def getServices(id):
    service =  Service.query.get(id)
    return jsonify({
        'service' : service.format()
    }) 


@app.route('/caisse', methods=['PATCH'])
def caissePdvs():
    body=request.get_json()
    idPdv = body.get('idPdv')
    caisse = body.get('caisse')
    p =  Pdv.query.get(idPdv)
    p.caisse = p.caisse+caisse
    p.update()
    return jsonify({
        'pdv' : p.format()
    })

@app.route('/proprietaires', methods=['GET'])
def getAllProprietaires():
    proprietaire =  Proprietaire.query.all()
    prop = [i.format() for i in proprietaire]
    return jsonify({
        'proprietaire' : prop
    })

@app.route('/gerants', methods=['GET'])
def getAllGerants():
    g =  Gerant.query.all()
    gerant = [i.format() for i in g]
    return jsonify({
        'gerant' : gerant
    })

@app.route('/gerants', methods=['POST'])
def postGerants():
    body=request.get_json()
    pdv_id= body.get('idPdv')
    gerant = body.get('gerant')
    nump = body.get('nump')
    if gerant == 'proprietaire':
        idG= body.get('id_g')
        nomG= body.get('nom_g')
        prenomG= body.get('prenom_g')
        passwordG= body.get('pass_g')
        actif = False
        g = Gerant(idG=idG, nom_g=nomG, prenom_g=prenomG, password_g=passwordG, actif=actif, pdv_idPdv=pdv_id,
        proprietaire_nump=nump)
        g.insert()
        pdv = Pdv.query.get(pdv_id)
        pdv.gerant = 'gerant'
        pdv.update()
        return jsonify({
            'success': True,
            'gerant' : g.format()
        })
    

@app.route('/gerants/<int:id>', methods=['GET'])
def getGerants(id):
    g =  Gerant.query.filter_by(pdv_idPdv=id).first()
    return jsonify({
        'gerant' : g.format()
    })

@app.route('/activeG', methods=['PATCH'])
def patchAcces():
    body=request.get_json()
    idG = body.get('id_g')
    g =  Gerant.query.get(idG)
    if g.actif :
        g.actif=False
        g.update()
        return jsonify({
        'gerant' : g.format()
    })
    else:
        g.actif=True
        g.update()
        return jsonify({
        'gerant' : g.format()
    })

@app.route('/gerant/<string:id>', methods=['PATCH'])
def patchGerant(id):
    gerant = Gerant.query.get(id)
    body=request.get_json()
    gerant.nom_g = body.get('nom_g')
    gerant.prenom_g =  body.get('prenom_g')
    gerant.password_g = body.get('pass_g')
    gerant.update()
    return jsonify({
        'gerant' : gerant.format()
    })

@app.route('/gerant/<string:id>', methods=['DELETE'])
def drop_book(id):
    l = Gerant.query.get(id)
    if l is None:
        return jsonify({
            'success' : False
        })
    else:
        l.delete()
        pdv = Pdv.query.get(l.pdv_idPdv)
        pdv.gerant = 'proprietaire'
        pdv.update()
        gerant = Gerant.query.all()
        formated_G = [i.format() for i in gerant]
        return jsonify({
            'deleted_id'   : l.idG,
            'Total'  : Gerant.query.count(),
            'Livres' : formated_G
        }) 

@app.route('/gerantsP/<string:nump>', methods=['GET'])
def getGerantsPerProprio(nump):
    g =  Gerant.query.filter_by(proprietaire_nump=nump)
    if g.count()== 0:
     return jsonify({
        'gerant' : 'vide'
    })
    else:
        gerant = [i.format() for i in g]
        return jsonify({
        'gerant' : gerant
        })

@app.route('/solde', methods=['PATCH'])
def patchSolde():
    body=request.get_json()
    id = body.get('idSpdv')
    solde = body.get('uv')
    spdv = ServicePdv.query.get(id)
    spdv.uv = spdv.uv+solde
    spdv.update()
    return jsonify({
        'servicePdv' : spdv.format()
    })


@app.route('/servicePdvs/<int:id>', methods=['GET'])
def getServicePdvs(id):
    service =  ServicePdv.query.filter_by(idPdv= id)
    serv = [i.format() for i in service]
    return jsonify({
        'servicePdv' : serv
    }) 

@app.route('/servicePdvs', methods = ['POST'])
def add_servicePdv():
        body = request.get_json()
        idPdv =  body.get('idPdv')
        title = body.get('titre')
        serv = Service.query.filter_by(libelle_s=title).first()
        service_idS= serv.idS
        service = ServicePdv(idPdv=idPdv, service_idS=service_idS)
        service.insert()
        return jsonify({
            'service' : service.format(),
            'Total'     : ServicePdv.query.count()
        })

@app.route('/servicePdvs', methods=['GET'])
def getAllServicePdv():
    service =  ServicePdv.query.all()
    serv = [i.format() for i in service]
    return jsonify({
        'servicePdv' : serv
    }) 

@app.route('/pdvs', methods=['GET'])
def getAllPdvs():
    p =  Pdv.query.all()
    pdv = [i.format() for i in p]
    return jsonify({
        'pdv' : pdv
    })

@app.route('/pdvs/<string:nump>', methods=['GET'])
def getPdvs(nump):
    point = Pdv.query.filter_by(proprietaire_nump=nump)
    pdv = [i.format() for i in point]
    return jsonify({
        'pdv' : pdv
    })

@app.route('/pdv/<int:id>', methods=['GET'])
def getPdv(id):
    point = Pdv.query.get(id)
    return jsonify({
        'pdv' : point.format()
    })


@app.route('/pdvs', methods=['POST'])
def add_pdv():
    body=request.get_json()
    nom = body.get('nomPDV', None)
    gerant = body.get('gerant', None)
    adresse = body.get('adresse', None)
    numProprio = body.get('num_p', None)
    n = Pdv.query.filter_by(nomPDV=nom)
    if n is None:
        p = Pdv(nomPDV=nom, gerant=gerant, adresse=adresse, proprietaire_nump=numProprio)
        p.insert()
        if gerant == 'gerant':
            idG= body.get('id_g')
            nomG= body.get('nom_g')
            prenomG= body.get('prenom_g')
            passwordG= body.get('pass_g')
            actif = False
            pdv_id=p.idPdv
            nump = numProprio
            id = Gerant.query.get(idG)
            if id is None:
                g = Gerant(idG=idG, nom_g=nomG, prenom_g=prenomG, password_g=passwordG, actif=actif, pdv_idPdv=pdv_id,
                proprietaire_nump=nump)
                g.insert()
                return jsonify({ 
                'pdv'        : p.format(),
                'gerant' : g.format(),
                'erreur' : False           
                })
            else:
                return jsonify({
                'erreur' : True,
                'type': 'Nom du gerant existant'
                    })
        else:
            return jsonify({
            'pdv'        : p.format(),
            'erreur' : False   
            })
    else :
         return jsonify({
            'erreur' : True,
            'type': 'Nom du PDV existant'
            })



@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success' : False,
        'Ressource'  : 'Bad Request',
    }), 400
    
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success' : False,
        'Ressource' : 'Not Found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success' : False,
        'Ressource' : 'Internal error'
    }), 500