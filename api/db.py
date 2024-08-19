import pg8000

from dotenv import load_dotenv
import os

load_dotenv()


class User:
    "Class for storing functions related to users"
    def __init__(self, user_id, group_id, name):
        self.user_id = user_id
        self.group_id = group_id
        self.name = name
        self.conn = self.connect_db()
        self.cursor = self.conn.cursor()
    
    def connect_db(self):
        conn = pg8000.connect(
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DATABASE'),
            host=os.getenv('POSTGRES_HOST'),
            port=5432
        )
        return conn

    def fetch_all_user_ids(self):
        self.cursor.execute(
            "SELECT user_id FROM user"
        )
        user_id_list = self.cursor.fetchall()
        return user_id_list
    
    def fetch_user(self):
        self.cursor.execute("SELECT * from user WHERE user_id = {user_id}".format(user_id=self.user_id))
        user_data = self.cursor.fetchall()
        return user_data
    
    def add_user(self):
        user_data = self.fetch_user()
        if len(user_data) == 0:
            self.cursor.execute(
                "INSERT INTO user VALUES ({user_id}, {group_id}, {name})".format(
                    user_id=self.user_id, group_id=self.group_id, name=self.name)
            )
            print(f"Added user_id: {self.user_id}, name: {self.name}")
        else:
            print("User exists, skipping execution.")
            

if __name__ == "__main__":
    try:
        conn = pg8000.connect(
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DATABASE'),
            host=os.getenv('POSTGRES_HOST'),
            port=5432
        )
        cur = conn.cursor()

        with open('db/users.sql') as file:
            sql_script = file.read()
        
        with conn.cursor() as cursor:
            cursor.execute(sql_script)
            conn.commit()

        conn.close()

    except Exception as e:
        print(f"An error occurred: {e}")

