import sys
import logging
import MySQLdb

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

dbname = 'makdb'
user = 'admin'
password = 'Admin123$'
host = 'mak-db-server.cnslitlzorh7.us-east-1.rds.amazonaws.com'

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class Command(BaseCommand):
    help = 'Creates the initial database'

    def handle(self, *args, **options):
        print('Starting db creation')
        try:
            db = MySQLdb.connect(host=host, user=user,
                                 password=password, db="mysql", connect_timeout=5)
            c = db.cursor()
            print("connected to db server")
            c.execute(f"""CREATE DATABASE {dbname};""")
            print("closed db connection")
        except:
            logger.error(
                "ERROR: Unexpected error: Could not connect to MySql instance.")
            sys.exit()
