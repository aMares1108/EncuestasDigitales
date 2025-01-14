from pymongo import MongoClient
from os import getenv
from json import dump
from bcrypt import hashpw, gensalt
from email_validator import validate_email, ValidatedEmail
from email_validator.exceptions_types import EmailNotValidError


def register_user(doc: dict):
    """Guarda en MongoDB el formulario simplificado

    Args:
        doc (dict): Respuesta de la API de Google Forms

    Returns:
        str | None: OID del documento creado
    """
    # with open('user_example.json','w') as f:
    #     dump(doc,f)
    verify_keys = {'name', 'last_name', 'email', 'password', 'type'}
    if doc.keys() != verify_keys:
        raise KeyError(f'Missing or extra keys: {verify_keys^doc.keys()}')
    if type(validate_email(doc['email'])) is not ValidatedEmail:
        raise EmailNotValidError()
    doc['password'] = hashpw(str(doc['password']).encode('utf-8'), gensalt())
    with MongoClient(getenv('MONGO_URI')) as mongo:
        res = mongo.DBEncuestasDigitales.user.insert_one(doc)
    return str(res.inserted_id) if res.acknowledged else None