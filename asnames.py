import logging
import psycopg2
import requests


DEFAULT_URL = 'https://ftp.ripe.net/ripe/asnames/asn.txt'
DEFAULT_DB = 'ihr'

class ASNames(object):
    def __init__(self, url_names=DEFAULT_URL, db=DEFAULT_DB):
        """Initialize variables"""
         
        self.url_names = url_names
        self.ripe = {}
        self.db = db

    def get_names(self):
        """Retrieve AS names file from RIPE and load it"""

        req = requests.get(self.url_names)

        if not req.ok:
            logging.warn('Cannot fetch file from RIPE website!')
            return False

        for line in req.text.splitlines():
            asn, _, name = line.partition(' ')
            self.ripe[int(asn)] = name

        return True
    
    def update_names(self):
        '''
        Get the list of ASNs from the database and update name if needed
        '''

        assert len(self.ripe)

        # Connect to the database
        conn_string = "host='127.0.0.1' dbname='%s'" % self.db

        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as cursor:

                # Get the list of monitored ASNs
                cursor.execute("SELECT number, name FROM ihr_asn")
                old_names = cursor.fetchall()

                for asn, old_name in old_names: 
                    
                    new_name = self.ripe.get(asn)
                    
                    if new_name and new_name != old_name:
                        cursor.execute(
                                "UPDATE ihr_asn SET name = %s where number = %s", 
                                (new_name, asn))


    def main(self):
        if self.get_names():
            self.update_names()


if __name__ == "__main__":

    FORMAT = '%(asctime)s %(processName)s %(message)s'
    logging.basicConfig(format=FORMAT, filename='ihr-as-names.log', 
            level=logging.WARN, datefmt='%Y-%m-%d %H:%M:%S')

    an = ASNames()
    an.main()

