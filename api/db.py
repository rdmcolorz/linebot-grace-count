import pg8000.dbapi
import os

# from dotenv import load_dotenv
# load_dotenv()


class User:
    "Class for storing functions related to users"
    def __init__(self, user_id, group_id, name):
        self.user_id = user_id
        self.group_id = group_id
        self.name = name
        self.conn = self.connect_db()
        self.cursor = self.conn.cursor()
    
    def connect_db(self):
        conn = pg8000.dbapi.connect(
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DATABASE'),
            host=os.getenv('POSTGRES_HOST'),
            port=5432
        )
        return conn

    def fetch_all_user_ids(self):
        self.cursor.execute(
            "SELECT user_id FROM users"
        )
        result = self.cursor.fetchall()
        user_id_list = [row[0] for row in result]
        return user_id_list
    
    def fetch_user(self):
        self.cursor.execute("SELECT * FROM users WHERE user_id = %s", [self.user_id])
        user_data = self.cursor.fetchall()
        return user_data
    
    def add_user(self):
        user_data = self.fetch_user()
        if len(user_data) == 0:
            self.cursor.execute(
                "INSERT INTO users (user_id, group_id, name) VALUES (%s, %s, %s)",
                [self.user_id, self.group_id, self.name]
            )
            self.conn.commit()
            print(f"Added user_id: {self.user_id}, name: {self.name}")
        else:
            print("User exists, skipping adding user.")
            

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

