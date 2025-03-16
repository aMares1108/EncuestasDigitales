from kivy.uix.screenmanager import Screen
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog, MDDialogIcon, MDDialogSupportingText, MDDialogHeadlineText
from kivy.properties import StringProperty, AliasProperty

import pandas as pd
from pymongo import MongoClient

from os import listdir, path, getenv
from json import load

class GenerarScreen(Screen):
    def on_enter(self):
        data = list()
        for file in listdir('respuestas'):
            if file.endswith('.tsv') and file!='temp.tsv':
                with open('respuestas/'+file, 'r', encoding='utf-8'):
                    data.append({
                        'form_id': path.splitext(file)[0]
                    })
        self.ids.rv.data = data

class GListItem(MDCard):
    form_id = StringProperty()
    user_id = StringProperty()
    date = StringProperty()

    def _get_form_title(self):
        if path.exists('encuestas/'+self.form_id+'.json') and path.exists('respuestas/'+self.form_id+'.tsv'):
            with open('encuestas/'+self.form_id+'.json', 'r', encoding='utf-8') as file:
                content = load(file)
            with open('respuestas/'+self.form_id+'.tsv', 'r', encoding='utf-8') as file:
                num_responses = sum(1 for linea in file if linea.strip()) - 1
            return (
                content['sections'][0]['title'], 
                num_responses
            )
        else:
            return ('',0)
        
    info = AliasProperty(_get_form_title, bind=['form_id'])

    def save(self):
        responses = self.read_tsv_file()
        # responses = flatten_responses(responses)
        self.insert_data_to_mongo(responses)

    def read_tsv_file(self):
        """
        Reads a TSV file and returns a dictionary where:
        - keys are questions (column headers)
        - values are lists of all responses (lists per question)
        - responses with comma-separated values are split into lists of strings
        """
        file_path = f"respuestas/{self.form_id}.tsv"
        df = pd.read_csv(file_path, sep='\t')

        responses = {'user_id':self.user_id}
        for column in df.columns:
            column_responses = []

            for value in df[column]:
                if isinstance(value, str) and ',' in value:
                    column_responses.append(value.split(','))
                else:
                    column_responses.append(value)

            responses[column] = column_responses

        return responses


    def insert_data_to_mongo(self, data):
        try:
            with MongoClient(getenv('MONGO_URI')) as mongo:
                # if formid not in mongo.DBEncuestasDigitales.list_collection_names():
                #     mongo.DBEncuestasDigitales.create_collection(formid)                
                db = mongo["test"]
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




