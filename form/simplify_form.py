from json import loads,dump
from pymongo import MongoClient
from os import getenv
from form.get_form import call_forms_api

def save_simplify_form(form_id: str, passwd: str):
    """Guarda en MongoDB el formulario simplificado

    Args:
        form_id (str): Token de Google Forms

    Returns:
        InsertOneResponse: Respuesta obtenida de la API de MongoDB al insertar un registro
    """
    doc = call_forms_api(form_id)
    doc = simplify(doc)
    doc['password'] = passwd
    with MongoClient(getenv('MONGO_URI')) as mongo:
        res = mongo.test.form.insert_one(doc)
    return res

def simplify(api_res: dict|str):
    """Simplifica el JSON de un Google Form

    Args:
        api_res (dict | str): Respuesta obtenida de la API de Google Forms

    Returns:
        dict: Diccionario simplificado
    """
    if type(api_res) is str:
        api_res = loads(api_res)
    if any(key not in api_res for key in ['formId', 'items','info']):
        raise KeyError('La entrada no contiene todos los elementos necesarios')
    
    api_res['sections'] = [{
        'title': api_res['info']['title'],
        'description': api_res['info']['description'],
        'questions': []
    }]

    for key in ['info', 'settings', 'revisionId', 'responderUri']:
        api_res.pop(key,None)
    
    for item in api_res['items']:
        if 'questionItem' in item:
            qtype = list(item['questionItem']['question'].keys())[1]
            api_res['sections'][-1]['questions'].append({
                'question': item.get('title'),
                'type': qtype
            })
            if qtype == 'choiceQuestion':
                api_res['sections'][-1]['questions'][-1]['choiceType'] = item['questionItem']['question'][qtype]['type']
                api_res['sections'][-1]['questions'][-1]['options'] = item['questionItem']['question'][qtype]['options']
        elif 'pageBreakItem' in item:
            api_res['sections'].append({
                'title': item['title'],
                'description': item['description'],
                'questions': []
            })
    api_res.pop('items')
    return api_res