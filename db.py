# Mongo Database Connection for our Atlas Mongo DB
from flask_pymongo import pymongo

CONNECTION_STRING = "mongodb+srv://Roisin:DFM5CauDv8K9tXpY@cluster0.b528o.mongodb.net/test?retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('home_safe')
