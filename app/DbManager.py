import sqlite3
import os
import shutil
import re
from flask import g, current_app

def extract_numbers(filename):
    match = re.match(r'(\d+)_', filename)
    if match:
        return match.group(1)
    return None

class DbManager:
    def __new__(cls, *args, **kwargs):
        raise RuntimeError("Creating instances of this class is not allowed")

    @staticmethod
    def connect_db() -> sqlite3.Connection:
        if 'db' not in g:
            try:  # TODO: check if db exists
                g.db = sqlite3.connect(current_app.config['DATABASE'])
            except sqlite3.OperationalError:
                print(f"Database {current_app.config['DATABASE']} not found.")
        return g.db

    @staticmethod
    def close_db(db: sqlite3.Connection = None):
        if 'db' in g:
            g.db.close()
            g.pop('db')
        if db is not None:
            db.close()

    @staticmethod
    def delete_db():
        try:
            if os.path.isfile(current_app.config['DATABASE']):
                # DbManager.close_db(g.db)
                os.remove(current_app.config['DATABASE'])
        except FileNotFoundError:
            print(f"File {current_app.config['DATABASE']} not found.")
        except PermissionError:
            print(f"Not enough rights to delete {current_app.config['DATABASE']}.")
        except Exception as e:
            print(f"UNEXPECTED ERROR {current_app.config['DATABASE']}: {e}")

    # Request context - for usage in app module

    @staticmethod
    def load_images_to_db():
        query = f"INSERT INTO {current_app.config['DB_TABLE_NAME']} (path, right_answer, typeof_dalton) VALUES (?, ?, ?);"
        existing_paths = set()

        existing_paths_query = f"SELECT path FROM {current_app.config['DB_TABLE_NAME']};"
        existing_paths_result = DbManager.g_exec_query(existing_paths_query)
        for row in existing_paths_result:
            existing_paths.add(row[0])

        for root, dirs, files in os.walk(current_app.config['RESOURCES']):
            for file in files:
                if file.lower().endswith(current_app.config['ALLOWED_EXTENSIONS']):
                    relative_path = os.path.relpath(os.path.join(root, file), current_app.config['RESOURCES'])
                    if relative_path not in existing_paths:
                        values = (relative_path, extract_numbers(file), "")
                        DbManager.g_exec_query(query, values)
                        existing_paths.add(relative_path)

    @staticmethod
    def clear_answers():
        query = f"UPDATE {current_app.config['DB_TABLE_NAME']} SET answer = '';"
        DbManager.g_exec_query(query)

    @staticmethod
    def delete_recolored():
        query = (f"DELETE FROM {current_app.config['DB_TABLE_NAME']} "
                 f"WHERE is_recolored == '1' OR path LIKE 'recolor%';")
        DbManager.g_exec_query(query)
        if os.path.exists(current_app.config['SAVE_DIR']):
            shutil.rmtree(current_app.config['SAVE_DIR'])

    @staticmethod
    def g_create_table():
        db = DbManager.connect_db()
        db.cursor().executescript(current_app.open_resource(current_app.config['DB_TABLE_CREATE'], mode='r').read())
        db.commit()

    @staticmethod
    def g_exec_query(query: str, params: tuple = ()) -> list:
        db = DbManager.connect_db()
        cursor = db.cursor()
        cursor.execute(query, params)
        db.commit()
        records = cursor.fetchall()
        cursor.close()
        return records

    @staticmethod
    def g_get_n_random_pics(n: int) -> list:
        query = (f"SELECT * FROM {current_app.config['DB_TABLE_NAME']} ORDER BY RANDOM() LIMIT ?")
        return DbManager.g_exec_query(query, (n,))

    @staticmethod
    def g_get_recolored() -> (list, int):
        query = (f"SELECT * FROM {current_app.config['DB_TABLE_NAME']} WHERE is_recolored == '1';")
        recolored = DbManager.g_exec_query(query)
        return recolored, len(recolored)

    @staticmethod
    def insert_answer(path: str, answer: str):
        query = (f"UPDATE {current_app.config['DB_TABLE_NAME']} "
                 f"SET answer = ? WHERE path = ?;")
        values = (answer, path)
        DbManager.g_exec_query(query, values)

    @staticmethod
    def g_set_is_recolored(path: str, value: int) -> list:
        query = (f"UPDATE {current_app.config['DB_TABLE_NAME']} SET is_recolored = {value} WHERE path == \'{path}\';")
        return DbManager.g_exec_query(query)

    @staticmethod
    def g_mark_dtypes(blueprint):
        # 0 - Deutan
        # 1 - Protan
        # 2 - Tritan
        query = (f'UPDATE {current_app.config["DB_TABLE_NAME"]} '
                 f'SET typeof_dalton = ? WHERE path LIKE ?;')
        for path, value in blueprint.items():
            values = (value, f'%{path}%')
            DbManager.g_exec_query(query, values)

    @staticmethod
    def g_set_dtype(type: int, path: str):
        query = (f'UPDATE {current_app.config["DB_TABLE_NAME"]} '
                 f'SET typeof_dalton = {type} WHERE path == \'{path}\';')
        DbManager.g_exec_query(query)

    @staticmethod
    def g_get_all_with_ans() -> list:
        query = (f'SELECT * FROM {current_app.config["DB_TABLE_NAME"]} '
                 f'WHERE answer IS NOT NULL;')
        return DbManager.g_exec_query(query)

    @staticmethod
    def g_get_with_wrong_ans(paths: list[str]):
        query = (f'SELECT * FROM {current_app.config["DB_TABLE_NAME"]}'
                 f' WHERE path IN ({",".join(["?"] * len(paths))})'
                 f' AND right_answer != answer;')
        return DbManager.g_exec_query(query, tuple(paths))

    @staticmethod
    def g_get_all_with_right_ans_s2() -> list:
        list_, int_ = DbManager.g_get_recolored()
        values = [path[1] for path in list_]
        query = (f'SELECT * FROM {current_app.config["DB_TABLE_NAME"]}'
                 f' WHERE path IN ({",".join(["?"] * len(values))})'
                 f'AND right_answer == answer AND is_recolored == 1;')
        return DbManager.g_exec_query(query, tuple(values))

