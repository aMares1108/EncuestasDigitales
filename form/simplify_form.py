from json import loads,dump
from pymongo import MongoClient
from os import getenv

def save_simplify_form(doc: dict | str):
    """Guarda en MongoDB el formulario simplificado

    Args:
        doc (dict | str): Respuesta de la API de Google Forms

    Returns:
        InsertOneResponse: Respuesta obtenida de la API de MongoDB al insertar un registro
    """
    doc = simplify(doc)
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