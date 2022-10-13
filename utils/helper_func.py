import json
import requests
from datetime import datetime
from .constants import DATETIME_FORMAT, URL, IMAGES_PATH
from typing import List
import concurrent
import os
from tqdm import tqdm

# Convert datetime object to string
def datetime_to_str(d: datetime):
  return datetime.strftime(d, DATETIME_FORMAT)

# Ensure there is a token present
def ensure_token(path = "utils/local_config.json"):
  with open(path) as f:
    data = json.load(f)

  if not data.get("idToken"):
    idToken = input(f"Paste your idToken from the {URL} application tab\n")
    with open(path, "w") as f:
      json.dump({"idToken": idToken}, f)

# Read token from the config file
def read_token(path = "utils/local_config.json"):
  with open(path) as f:
    data = json.load(f)

  return data.get("idToken")

# Get new image labels from the database
def get_new_data(dt: datetime):
  dt_str = datetime_to_str(dt)

  idToken = read_token()

  headers = {
      "Authorization": f"Bearer {idToken}"
  }
  url = f"{URL}/get-new-data"
  r = requests.get(url, params={"after_date": dt_str}, headers=headers)
  r.raise_for_status()

  data = json.loads(r.content)
  return data

# Get presigned urls for images
def get_presigned_url(image_names: List[str]):
  idToken = read_token()

  headers = {
      "Authorization": f"Bearer {idToken}"
  }
  url = f"{URL}/get-images"
  r = requests.post(url, data = json.dumps(image_names), headers=headers)
  r.raise_for_status()
  data = json.loads(r.content)
  return data

# Download one image from a presigned link
def download_image(url: str, save_path: str):
  req = requests.get(url)
  req.raise_for_status()

  with open(save_path, "wb") as f:
    f.write(req.content)


# Get presigned links and download multiple images
def download_many_images(image_names: List[str]):
  BATCH_SIZE = 50

  batches = []

  for i in range(len(image_names)//BATCH_SIZE + 1):
    batches.append(image_names[i*BATCH_SIZE: (i+1)*BATCH_SIZE])

  for batch in batches:
    urls = get_presigned_url(batch)

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
      futures = []

      for image_name, url in urls.items():
        if url:
          save_path = os.path.join(IMAGES_PATH, image_name)
          futures.append( executor.submit(download_image, url, save_path))

      for future in tqdm(concurrent.futures.as_completed(futures)):
        r = future.result()