from models.recolor import Recoler
import os
from random import randint
from flask import current_app, g
from app.DbManager import DbManager


class ModelsManager:
    def __new__(cls, *args, **kwargs):
        raise RuntimeError("Creating instances of this class is not allowed")

    # 0 - Deutan
    # 1 - Protan
    # 2 - Tritan
    @staticmethod
    def mark_dtypes_in_db():
        blueprint = {
            "RED_GREEN":  1,
            "RED_GRAY": 1,
            "GREEN_BROWN": 0,
            "GREEN_BLUE": 2,
            "BLUE_GRAY": 2,
            "BROWN_GREY_YELLOW": 1,
            "BLUE_PURPLE": 0,
        }
        DbManager.g_mark_dtypes(blueprint)


    # 0 - Deutan
    # 1 - Protan
    # 2 - Tritan
    @staticmethod
    def define_type(answers: list[tuple]) -> int:
        # more false answers - more likely to be this type of colorblindness

        is_Deutan = 0
        is_Protan = 0
        is_Tritan = 0

        tuples = DbManager.g_get_all_with_ans()

        for t in tuples:
            if t[2] == t[3]:
                if t[4] == 0:
                    is_Deutan -= 1
                elif t[4] == 1:
                    is_Protan -= 1
                else: # t[4] == 2:
                    is_Tritan -= 1
            else:
                if t[4] == 0:
                    is_Protan += 1
                    is_Tritan += 1
                elif t[4] == 1:
                    is_Deutan += 1
                    is_Tritan += 1
                else: # t[4] == 2:
                    is_Deutan += 1
                    is_Protan += 1

        if max(is_Deutan, is_Protan, is_Tritan) == is_Deutan:
            ans = 0
        elif max(is_Deutan, is_Protan, is_Tritan) == is_Protan:
            ans = 1
        else:  # max(is_Deutan, is_Protan, is_Tritan) == is_Tritan:
            ans = 2
        return ans
        # return randint(0, 2)  # legacy version


    # 0 - Deutan
    # 1 - Protan
    # 2 - Tritan
    @staticmethod
    def get_correctness_chance(predicted_type: int) -> (int, int):

        tuples = DbManager.g_get_all_with_right_ans_s2()

        corrected = len(tuples)

        if corrected != 0 :
            is_Deutan = 10 / len(tuples) if predicted_type == 0 else 1
            is_Protan = 10 / len(tuples) if predicted_type == 1 else 1
            is_Tritan = 10 / len(tuples) if predicted_type == 2 else 1

            for t in tuples:
                if t[4] == 0:
                    is_Deutan += 1
                elif t[4] == 1:
                    is_Protan += 1
                else:  # t[4] == 2:
                    is_Tritan += 1

            max_ = max(is_Deutan, is_Protan, is_Tritan)
            min_ = min(is_Deutan, is_Protan, is_Tritan)
            percentage = (max_ + min_) / (is_Deutan + is_Protan + is_Tritan) * 100

            if max(is_Deutan, is_Protan, is_Tritan) == is_Deutan:
                dalton = 0
            elif max(is_Deutan, is_Protan, is_Tritan) == is_Protan:
                dalton = 1
            else:  # max(is_Deutan, is_Protan, is_Tritan) == is_Tritan:
                dalton = 2

        else:
            percentage = 0
            dalton = predicted_type

        return dalton, percentage

    @staticmethod
    def recolor_images(answers: list[tuple], blindness_type: int):
        """
        map answers to images paths
        """
        os.makedirs(current_app.config["SAVE_DIR"], exist_ok=True)

        image_paths = [item[1] for item in answers]

        paths = []
        for path in image_paths:
            colored_path = Recoler.recolor_img(
                str(os.path.join(current_app.config["RESOURCES"], path)),
                current_app.config["SAVE_DIR"],
                blindness_type
            )
            print("PATH: ", path)

            paths.append(colored_path)

            DbManager.load_images_to_db()
            DbManager.g_set_is_recolored(path, 2)
            DbManager.g_set_is_recolored(colored_path, 1)
            DbManager.g_set_dtype(blindness_type, colored_path)

        return paths
