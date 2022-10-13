import os

TRAINING_FOLDER = "/content/drive/Shareddrives/Bionary-HandsOnHealth/Training"

IMAGES_PATH = os.path.join(TRAINING_FOLDER, "Images")
IMAGE_LABELS_PATH = os.path.join(TRAINING_FOLDER, "ImagesLabels.json")
INFO_PATH = os.path.join(TRAINING_FOLDER, "info.json")

PROCESSED_LABELS_PATH = os.path.join(TRAINING_FOLDER,"ProcessedLabels")
CROPPED_ORIG_PATH = os.path.join(TRAINING_FOLDER,"Cropped", "CroppedOriginal")
CROPPED_AUGMENTED_PATH = os.path.join(TRAINING_FOLDER, "Cropped", "CroppedAugmented")
CROPPED_RESIZED_PATH = os.path.join(TRAINING_FOLDER, "Cropped", "Resized")


DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

STAGE = "dev"

urls = {
  "dev": "https://b0l2rcyvuh.execute-api.eu-central-1.amazonaws.com/dev",
  "prod": "https://8m6yqqim6d.execute-api.eu-central-1.amazonaws.com/prod"
}

URL = urls[STAGE]