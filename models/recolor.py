from models.CVD_Simulation import *
from models.engine import SWIN_Generator

import os
import torch
from torchvision.transforms import v2
from torchvision import transforms
from torchvision.utils import save_image

from PIL import Image


class UnNormalize(object):
    """Denormalize image with specified mean and std"""
    def __init__(self, mean, std):
        self.mean = mean
        self.std = std

    def __call__(self, tensor):
        """
        Args:
            tensor (Tensor): Tensor image of size (C, H, W) to be normalized.
        Returns:
            Tensor: Normalized image.
        """
        for t, m, s in zip(tensor, self.mean, self.std):
            t.mul_(s).add_(m) # The normalize code -> t.sub_(m).div_(s)

        return tensor


def hint():
    print("""python recolor.py <abs_image_path> <cvd_type> <output_path>
abs_image_path - absolute image path (image to recolor).
cvd_type - type of colorblindness:
          0 - Deutan
          1 - Protan
          2 - Tritan
output_path - where to output recolored image (absolute path)
""")


class Recoler:
    @staticmethod
    def recolor_img(img_path: str, output_path: str, cvd_type: int):

        # Open image
        img = Image.open(img_path)

        # transform image
        cuda = torch.cuda.is_available()
        Tensor = torch.cuda.FloatTensor if cuda else torch.FloatTensor # TODO check!!
        transforms_ = v2.Compose([
            transforms.Resize((256, 256), Image.BICUBIC),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
        ])
        img = transforms_(img).type(torch.FloatTensor)
        # Model load
        bas_dir = os.path.dirname(os.path.abspath(__file__))
        model = SWIN_Generator()
        selected_model = ""
        if cvd_type == CVDType.DEUTAN.value:
            selected_model = "DEUTAN"
            model_path = f"{bas_dir}/trained/recolor/DEUTAN/generator_90_epochs.pth"
        elif cvd_type == CVDType.PROTAN.value:
            selected_model = "PROTAN"
            model_path = f"{bas_dir}/trained/recolor/PROTAN/PROTAN. 100% SEVERITY. generator_10.pth"
        elif cvd_type == CVDType.TRITAN.value:
            selected_model = "TRITAN"
            model_path = f"{bas_dir}/trained/recolor/TRITAN/TRITAN. 100% SEVERITY. generator_10.pth"
        if cuda:
            model.load_state_dict(torch.load(model_path))
        else:
            model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        model.eval()
        # Evaluation
        unorm = UnNormalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5))
        with torch.no_grad():
            unsqueeze = img.unsqueeze(0)
            output = model(unsqueeze)
        output = unorm(output)
        # Save the output image to the specified output path
        img_name = os.path.splitext(os.path.basename(img_path))[0]
        output_file = os.path.join(output_path, f"{img_name}_corrected_{selected_model}.png")
        save_image(output, output_file)
        # Получение названия файла
        file_name = os.path.basename(output_file)
        dir_name = os.path.basename(os.path.dirname(output_file))
        relative_path = os.path.join(dir_name, file_name)

        return relative_path
