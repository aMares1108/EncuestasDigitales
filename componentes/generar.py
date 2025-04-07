from kivy.uix.screenmanager import Screen
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog, MDDialogIcon, MDDialogSupportingText, MDDialogHeadlineText
from kivy.app import App
from kivy.properties import StringProperty, AliasProperty

import pandas as pd
from datetime import datetime
from pymongo import MongoClient

from os import listdir, path, getenv
from json import load
import csv

class GenerarScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        if app.user_type == 'principal_reducida':
            data = list()
            for file in listdir('respuestas'):
                if file.endswith('.tsv') and file!='temp.tsv':
                    with open('respuestas/'+file, 'r', encoding='utf-8'):
                        data.append({
                            'form_id': path.splitext(file)[0]
                        })
            self.ids.rv.data = data
        elif app.user_type == 'principal':
            with MongoClient(getenv('MONGO_URI')) as mongo:
                db = mongo.get_database()
                self.ids.rv.data = [{'form_id': form} for form in db.list_collection_names() if form not in ('alumnos', 'form', 'test', 'user')]

class GListItem(MDCard):
    form_id = StringProperty()
    user_id = StringProperty()
    date = StringProperty()

    def _get_form_title(self):
        app = App.get_running_app()
        if app.user_type == 'principal_reducida':
            if path.exists('encuestas/'+self.form_id+'.json') and path.exists('respuestas/'+self.form_id+'.tsv'):
                with open('encuestas/'+self.form_id+'.json', 'r', encoding='utf-8') as file:
                    content = load(file)
                with open('respuestas/'+self.form_id+'.tsv', 'r', encoding='utf-8') as file:
                    num_responses = sum(1 for linea in file if linea.strip()) - 1
                return (
                    content['sections'][0]['title'], 
                    num_responses
                )
        elif app.user_type == 'principal':
            if self.form_id:
                with MongoClient(getenv('MONGO_URI')) as mongo:
                    db = mongo.get_database()
                    collection = db[self.form_id]
                    cant = len(next(iter(collection.find_one().get('responses', [dict()]).values())))
                    title = db.form.find_one({'formId': self.form_id})
                    return (title, cant)
        return ('',0)
    info = AliasProperty(_get_form_title, bind=['form_id'])

    def save(self):
        app = App.get_running_app()
        if app.user_type=='principal_reducida':
            responses = self.read_tsv_file()
            # responses = flatten_responses(responses)
            self.insert_data_to_mongo(responses)
        elif app.user_type=='principal':
            try:
                with MongoClient(getenv('MONGO_URI')) as mongo:
                    db = mongo.get_database()
                    doc = db[self.form_id].find_one({})
                    headers_gen = doc.keys()
                    headers_questions = doc['responses'].keys()
                    with open(f"reportes/{self.form_id}.tsv", "w", newline="", encoding="utf-8") as tsv_file:
                        writer = csv.writer(tsv_file, delimiter="\t")  # Especifica el delimitador como tab
                        # Escribe los encabezados (columnas)
                        
                        writer.writerow([*headers_gen, *headers_questions])

                        # Escribe los datos (filas)
                        # for documento in documentos:
                        subdict = doc.pop('responses')
                        common = doc
                        list_of_dicts = [dict(zip(subdict.keys(), values)) for values in zip(*subdict.values())]
                        writer.writerows([[*common.values(), *d.values()] for d in list_of_dicts])
            except Exception as exc:
                MDDialog(
                    MDDialogIcon(
                        icon='database-alert'
                    ),
                    MDDialogHeadlineText(
                        text='Ocurrió un error'
                    ),
                    MDDialogSupportingText(
                        text=str(exc)
                    )
                ).open()
            else:
                MDDialog(
                    MDDialogIcon(
                        icon='database-check'
                    ),
                    MDDialogHeadlineText(
                        text='Reporte guardado localmente'
                    )
                ).open()


    def read_tsv_file(self):
        """
        Reads a TSV file and returns a dictionary where:
        - keys are questions (column headers)
        - values are lists of all responses (lists per question)
        - responses with comma-separated values are split into lists of strings
        """
        file_path = f"respuestas/{self.form_id}.tsv"
        df = pd.read_csv(file_path, sep='\t')

        responses = df.to_dict(orient='list')

        return {
            'form_id': self.form_id,
            'user_id': self.user_id,
            'date': datetime.now(),
            'responses': responses
        }


    def insert_data_to_mongo(self, data):
        try:
            with MongoClient(getenv('MONGO_URI')) as mongo:
                # if formid not in mongo.DBEncuestasDigitales.list_collection_names():
                #     mongo.DBEncuestasDigitales.create_collection(formid)                
                db = mongo.get_database()
                collection = db[self.form_id]
                res = collection.insert_one(data)
        except Exception as exc:
            MDDialog(
                MDDialogIcon(
                    icon='database-alert'
                ),
                MDDialogHeadlineText(
                    text='Ocurrió un error'
                ),
                MDDialogSupportingText(
                    text=str(exc)
                )
            ).open()
        else:
            MDDialog(
                MDDialogIcon(
                    icon='database-check'
                ),
                MDDialogHeadlineText(
                    text='Reporte registrado en la base de datos'
                )
            ).open()




