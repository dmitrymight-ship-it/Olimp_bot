import sqlite3
from config import *

class DB_Manager():
    def __init__(self, database):
        self.database = database

    def create_questions_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS questions (
                    question_id INTEGER PRIMARY KEY,
                    question_text TEXT,
                    answer TEXT,

                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS answers (
                    question_id INTEGER,
                    FOREIGN KEY (question_id) REFERENCES questions (question_id),
                    FOREIGN KEY (team_id) REFERENCES teams (team_id)

                )
            ''')
            conn.commit()

    def insert_questions(self, data):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()

            cursor.executemany('INSERT OR IGNORE INTO questions (question_text, answer) VALUES (?, ?)', data)
            conn.commit()


    def create_users_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    team_id INTEGER,
                    question_id INTEGER DEFAULT 1,        
                    FOREIGN KEY (team_id) REFERENCES teams (team_id),
                    FOREIGN KEY (question_id) REFERENCES questions (question_id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS teams (
                    team_id INTEGER PRIMARY KEY,
                    name TEXT,
                )
            ''')
            conn.commit()


    def insert_user(self, user_id, team_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()

            cursor.execute('INSERT OR IGNORE INTO users (user_id, team_id) VALUES (?, ?)', (user_id, team_id))
            conn.commit()
        

    def insert_team(self, team_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('INSERT OR IGNORE INTO teams (name) VALUES (?)', (team_name,))
            conn.commit()
            cursor.execute('SELECT team_id FROM teams WHERE name = ?', (team_name, ))
            return cursor.fetchone()[0]

    def get_rating(self):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()

        cursor.execute('SELECT name, score FROM teams ORDER BY score DESC')
        return cursor.fetchall()
        
    def get_question(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()

            cursor.execute('''SELECT questions.question_id, questions.question_text, answer FROM users
    INNER JOIN questions ON users.question_id = questions.question_id
    WHERE user_id = ?''', (user_id,))
            
            return cursor.fetchone()

    def get_answers(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()

            cursor.execute('''SELECT answers.question_id FROM answers
    INNER JOIN users ON users.team_id = answers.team_id
    WHERE user_id = ?''', (user_id,))
            
            return [x[0] for x in cursor.fetchall()]

    def get_teams_name(self):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()

            cursor.execute('''SELECT team_id, name FROM teams''')
            return cursor.fetchall()
            

    def check_answer(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()

            cursor.execute('''SELECT answers.question_id FROM answers
    INNER JOIN users ON users.team_id = answers.team_id
    WHERE user_id = ? AND answers.question_id = users.question_id''', (user_id,))

            return cursor.fetchall()


    def update_question_id(self, user_id, question_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''UPDATE users SET question_id = ?
    WHERE user_id = ?''', (question_id, user_id))


    def add_points(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()

            cursor.execute('''SELECT questions.score, questions.question_id, users.team_id FROM users
    INNER JOIN questions ON users.question_id = questions.question_id
    WHERE user_id = ?''', (user_id,))

            score, question_id, team_id = cursor.fetchone()
            cursor.execute("INSERT OR IGNORE INTO answers values(?,?)", (question_id, team_id))
            cursor.execute(f'''UPDATE teams set score = score+{score}
                            WHERE team_id = ?''', (team_id,))   
            conn.commit()

            return self.check_finish_level(user_id)


    def check_access(self, question_id, user_id):
        level = self.get_level(user_id)
        last_question = QUESTIONS_INFO[level-1]['list'][-1]
        if question_id <= last_question:
            return 1
        else:
            return 0


    def check_finish_level(self, user_id):
        answers = self.get_answers(user_id)
        level = self.get_level(user_id)
        list_ans = []
        for lvl in QUESTIONS_INFO[:level]:
            list_ans += lvl['list']
        if set( list_ans ).issubset(answers):
            return 1
        else:
            return 0


if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    manager.create_questions_tables()
    manager.create_users_table()
    questions = [
        ("Сколько будет 1 + 1 : 3.15 * 45.987 - 345", "−329,4",  ''),
        ("Если у Ани 9 яблок, а у Гриши 5 яблок.Вопрос: когда в следующий раз будет извержение вулкана Кракатау", "4 яблока", ''),
        ("Вычислите корень из 45", "6,708", ''),
        ("У Маши любимый цвет зеленый, у Леры красный.Вопрос: какой будет любимый цвет Ани, после того как она узнала что обогнала Гришу в колличестве яблок", "Красный", ''),
        ("Сколько денег заработала компания apple после выхода нового айфона если диафрагма не открывается", "Незнаю", ''),
        ("Если микроволновая печь разогревает еду 60 сек.Вопрос: Почему не 1,5 минуты", "Потому что заканчивается на у", ''),
        ]
    manager.insert_questions(questions)
 
    for i, key in enumerate(ANSWER_LIST):
        manager.update_questions_key(key, i+1)