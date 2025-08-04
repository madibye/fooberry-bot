from pymongo import MongoClient
from pymongo.database import Database, Collection
from termcolor import cprint

from config import *

mongo_client = MongoClient(mongo_url, directConnection=True)
database: Database = mongo_client.fooberry_bot  # Database
db_config: Collection = database.config


def create_config_value(config_id, default_value):
    document = {"_id": config_id, "value": default_value}
    cprint(f"Creating new db_config entry under \"{document['_id']}\" with value {document['value']}", "yellow")
    db_config.insert_one(document)
    return document

def get_config_value(config_id, default_value):
    document = db_config.find_one({"_id": str(config_id)})
    if document is None:
        document = create_config_value(config_id, default_value)
    if not document:
        cprint(f"Something went wrong when getting config value `{config_id}`!", "red")
    return document["value"]

def get_config_description(config_id):
    document = db_config.find_one({"_id": str(config_id)})
    if document:
        return document.get("description")
    return None

def set_config_value(config_id, new_value):
    """Do not call this method outside of live_config.set(). Desyncing with db would be sad."""
    document: dict = db_config.find_one({"_id": str(config_id)})
    if document is None:
        return db_config.insert_one({"_id": config_id, "value": new_value})
    document["value"] = new_value
    return db_config.replace_one({"_id": config_id}, document)

def set_config_description(config_id, new_description: str):
    document: dict = db_config.find_one({"_id": str(config_id)})
    if not document:
        return
    document["description"] = new_description
    return db_config.replace_one({"_id": config_id}, document)

def set_user_timezone(user_id: int, timezone_str: str):
    document = db_config.find_one({"_id": "user_timezones"})
    if document is None:
        db_config.insert_one(document := {"_id": "user_timezones", "values": {}})
    document["values"][str(user_id)] = timezone_str
    db_config.replace_one({"_id": "user_timezones"}, document)

def get_user_timezone(user_id: int):
    document = db_config.find_one({"_id": "user_timezones"})
    if document is None:
        db_config.insert_one(document := {"_id": "user_timezones", "values": {}})
    return document["values"].get(str(user_id), "America/New_York")
