import imgaug as ia
import imgaug.augmenters as iaa
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage
from .constants import (
  PROCESSED_LABELS_PATH,
  CROPPED_ORIG_PATH,
  CROPPED_AUGMENTED_PATH,
  CROPPED_RESIZED_PATH,
  IMAGES_PATH
)

from typing import List, Tuple, Dict
from PIL import Image
import numpy as np
import concurrent
import random
from tqdm import tqdm
import os, json
import matplotlib.pyplot as plt

# Given an object in the following format:
# {
#   "image_name": "in_001382_male_21_InGlasses0.jpg",
#   "bounding_box": {
#     "top_left": {
#       "x": 1482,
#       "y": 3654
#     },
#     "bottom_right": {
#       "x": 1864,
#       "y": 3748
#     }
#   }
# }
# This function will crop the original image and the rotated images

def crop_bounding_boxes(image_label, folder_orig, folder_aug, nr_rotations = 2):
    image_name = image_label["image_name"]
    side = image_label.get("side", "")
    without_ext = image_name.split(".")[0]

    path = os.path.join(IMAGES_PATH, image_name)

    bounding_box = image_label["bounding_box"]

    top_left = bounding_box["top_left"]
    bottom_right = bounding_box["bottom_right"]

    x1, y1 = top_left["x"], top_left["y"]
    x2, y2 = bottom_right["x"], bottom_right["y"]

    try:
      img = np.array(Image.open(path).convert("RGB"))
    except Exception as e:
      return image_name

    orig_cropped = img[y1: y2, x1: x2, :]

    cropped_pil = Image.fromarray(orig_cropped)
    cropped_image_name = f"{without_ext}_{side}_orig.png"

    img_path = os.path.join(folder_orig, cropped_image_name)
    cropped_pil.save(img_path)

    bbs = BoundingBoxesOnImage([BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2)], shape=img.shape)

    angles = [random.randint(-20, 20) for _ in range(nr_rotations)]

    for angle in angles:
      rotation = iaa.Rotate(rotate = angle)
      image_aug, bbs_aug = rotation(image=img, bounding_boxes=bbs)

      x1 = int(bbs_aug[0].x1)
      x2 = int(bbs_aug[0].x2)
      y1 = int(bbs_aug[0].y1)
      y2 = int(bbs_aug[0].y2)

      cropped = image_aug[y1: y2, x1: x2, :]

      cropped_pil = Image.fromarray(cropped)
      cropped_image_name = f"{without_ext}_{side}_rot_{angle}.png"
      img_path = os.path.join(folder_aug, cropped_image_name)
      cropped_pil.save(img_path)


# This function takes the model_name as a parameter(it's also the folder name)
# And crops the images for the Yes and No folders
def crop_images(model_name: str, max_workers = 100):

  missing_images = []

  labels_path = os.path.join(PROCESSED_LABELS_PATH, model_name)
  for value in ("Yes", "No"):
    json_path = os.path.join(labels_path, f"{value}.json")

    with open(json_path) as f:
      objects = json.load(f)

    folder_orig = os.path.join(CROPPED_ORIG_PATH, model_name, value)
    folder_aug = os.path.join(CROPPED_AUGMENTED_PATH, model_name,  value)

    os.makedirs(folder_orig, exist_ok = True)
    os.makedirs(folder_aug, exist_ok = True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
      futures = []

      for obj in objects.values():
        futures.append( executor.submit(crop_bounding_boxes, obj, folder_orig, folder_aug))

      for future in tqdm(concurrent.futures.as_completed(futures)):
          r = future.result(timeout=5)
          if r:
            missing_images.append(r)

  return missing_images



def get_image_size(image_path):
  img = Image.open(image_path)
  width, height = img.size
  return (width, height)

# Counts the amount of
def count_widths_heights(model_name: str, max_workers = 100)->List[Tuple[int, int]]:
  model_path = os.path.join(CROPPED_ORIG_PATH, model_name)

  if not os.path.exists(model_path):
    raise ValueError(f"Path '{model_path}' does not exist")

  cropped_images_paths = []

  for l in ("Yes", "No"):
    labels_path = os.path.join(model_path, l)
    image_paths = [os.path.join(labels_path, img) for img in os.listdir(labels_path) if ".png" in img]
    cropped_images_paths.extend(image_paths)

  widths = []
  heights = []
  with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = []

    for image_path in cropped_images_paths:
      futures.append( executor.submit(get_image_size, image_path))

    for future in tqdm(concurrent.futures.as_completed(futures)):
        w, h = future.result()
        widths.append(w)
        heights.append(h)
  return {
    "widths": widths,
    "heights": heights
  }


# model_name = "Eye_OuterCorner_Dark"

# res = count_widths_heights(model_name)

# widths = res["widths"]
# heights = res["heights"]



def draw_histogram(widths: List[int], heights: List[int]):
  fig, ax = plt.subplots()

  h = ax.hist2d(widths, heights, bins=20)

  ax.set_title('Distribution of cropped image sizes')
  ax.set_xlabel('width')
  ax.set_ylabel('height')
  plt.colorbar(h[3])
  plt.show()


# Resize one image. Reads from src_img_path, saves to save_path.
def resize_image(src_img_path, save_path, size_w_h = Tuple[int, int]):
  Image.open(src_img_path).resize(size_w_h).save(save_path)

# Counts the amount of
def resize_images_for_model(model_name: str, size_w_h = Tuple[int, int], max_workers = 100):
  width, height = size_w_h

  source_model_path = os.path.join(CROPPED_ORIG_PATH, model_name)
  dest_model_path = os.path.join(CROPPED_RESIZED_PATH, model_name, f"w_{width}_h_{height}")

  if not os.path.exists(source_model_path):
    raise ValueError(f"Path '{source_model_path}' does not exist")

  source_to_dest = {}

  for label in ("Yes", "No"):

    source_folder = os.path.join(source_model_path, label)
    dest_folder = os.path.join(dest_model_path, label)
    os.makedirs(dest_folder, exist_ok=True)

    for img in os.listdir(source_folder):
      if ".png" in img:
        img_src = os.path.join(source_folder, img)
        img_dst = os.path.join(dest_folder, img)
        source_to_dest[img_src] = img_dst

  with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = []

    for src, dest in source_to_dest.items():
      futures.append( executor.submit(resize_image, src, dest, size_w_h))

    for future in tqdm(concurrent.futures.as_completed(futures)):
        r = future.result()


# Read one image as numpy array
def read_numpy(src_img_path: str, size_w_h = Tuple[int, int]):
  return np.array(Image.open(src_img_path))

# Read all cropped and resized images in a numpy array based on Label
def read_images_as_ndarray(model_name: str, size_w_h = Tuple[int, int], max_workers = 100)-> Dict[str, np.ndarray]:
  width, height = size_w_h
  source_model_path = os.path.join(CROPPED_RESIZED_PATH, model_name, f"w_{width}_h_{height}")

  if not os.path.exists(source_model_path):
    raise ValueError(f"Path '{source_model_path}' does not exist")

  data = {}
  for label in ("Yes", "No"):

    source_folder = os.path.join(source_model_path, label)
    images_to_read = [os.path.join(source_folder, img) for img in os.listdir(source_folder) if ".png" in img]

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
      futures = []

      for img_path in images_to_read:
        futures.append( executor.submit(read_numpy, img_path))
      data[label] = [future.result() for future in tqdm(concurrent.futures.as_completed(futures))]

  for k in data:
    data[k] = np.array(data[k])
  return data

