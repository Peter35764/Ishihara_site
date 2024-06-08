import os
from db.db import get_db
from app.config import Config
from models.legacy.old_predictor import predictor
import json


class ImageProcessor:

    @staticmethod
    def get_images_names():
        """
        1. Get all images names from the folder
        2. Return the names
        """
        try:
            # Получаем список всех файлов в указанной папке
            files = os.listdir(Config.UPLOAD_FOLDER)
            return files
        except FileNotFoundError:
            print("Указанная папка не найдена.")
            return []
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return []

    @staticmethod
    def process_images(app):
        """
        1. Get all images names
        2. Process the images
        3. Save the result in db
        """
        images_names = ImageProcessor.get_images_names()
        db_images_names = ImageProcessor.get_db_images_names(app)
        images_ans = {}
        for name in images_names:
            if name not in db_images_names:
                path_to_image = os.path.join(Config.UPLOAD_FOLDER, name)
                name_values = predictor.predict(path_to_image)
                images_ans[name] = name_values
                # process the image
                # save the result in db
        if images_names:
            ImageProcessor.save_images(images_ans)
        pass

    @staticmethod
    def get_db_images_names(app):
        """
        1. Get all images names from the db
        2. Return the names
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT title FROM pictures")
        titles = cursor.fetchall()
        return [title[0] for title in titles]

    @staticmethod
    def save_images(images_data):
        """
        1. Save the image in db
        """
        db = get_db()
        cursor = db.cursor()
        sql = "INSERT INTO pictures (title, `data`) VALUES (?, ?)"  # `values` в кавычках
        values = [(key, json.dumps(value.tolist())) for key, value in images_data.items()]
        cursor.executemany(sql, values)
        db.commit()