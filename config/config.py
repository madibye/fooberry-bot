import os

from dotenv import load_dotenv

load_dotenv()

_true = ["true", "True", "t", "T", "1", "yes", "Yes", "YES"]

mongo_url = os.environ.get("MONGO_URL", "mongodb://mongo:27018")

activity_text = "v1.0.0"
command_prefixes = ['!']

madi_id = 188875600373481472
allowed_servers = [262334639924838412, 1400693204034125864]
dailydive_channel_id = 1400699611974471754

scv_blocked = {}

discord_token = os.environ.get("FOOBERRY_TOKEN")
bot_application_id = 1401926435286941747
discord_cogs = [
    "cogs.dailydive",
]
