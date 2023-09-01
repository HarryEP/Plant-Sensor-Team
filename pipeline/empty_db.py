"""Removes rows older than a day old from the recording table"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
from dotenv import load_dotenv

def remove_old_recordings(conn:connection):
    """Removes entries from the recording table older than a day"""
    with conn.cursor() as cur:
        sql = """
            DELETE FROM recording
            WHERE recorded < NOW() - interval '1 day'
            """
        cur.execute(sql)
    conn.commit()

if __name__ == "__main__":
    load_dotenv()
    db_conn = psycopg2.connect(host=os.environ["DB_HOST"], dbname= os.environ["DB_NAME"],
                             password=os.environ["DB_PASSWORD"], user=os.environ["DB_USERNAME"],
                             cursor_factory=RealDictCursor)
    remove_old_recordings(db_conn)
    db_conn.close()
