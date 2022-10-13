import os, json
# from typing_extensions import Literal
from typing import Literal
from typing import List, Dict
from collections import Counter

def save_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent =4)

def load_json(path, default = None):
    if not os.path.exists(path):
        if default == None:
            raise ValueError(f"The '{path}' path does not exist")
        return default

    with open(path) as f:
        data = json.load(f)
    return data

def decide_by_frequency(face_labels: List[Dict]):
    all_features = {k for o in face_labels for k in list(o.keys())}

    decided = {}
    for feature in all_features:
        labels = [o.get(feature) for o in face_labels]
        most_common = Counter(filter(lambda x: x in ("Yes", "No", "Undef"), labels)).most_common()

        # most_common = [('Yes', 2), ('No', 1)]
        if len(most_common) == 0:
            continue
        elif len(most_common) == 1:
            decided[feature] = most_common[0][0]
        else:
            # Check if the experts are disagreeing
            if most_common[0][1] > most_common[1][1]:
                decided[feature] = most_common[0][0]
    return decided


def decide_on_labels(original_labels):
    grouped_labels = {}

    #group by image_name
    for obj in original_labels:
        image_name = obj["image_name"]
        grouped_labels[image_name] = grouped_labels.get(image_name, []) + [obj]

    decided_labels = {}
    for image_name, multilabels in grouped_labels.items():
        decided_labels[image_name] = {
            "image_name": image_name,
            "bounding_boxes": multilabels[0]["bounding_boxes"],
            "face_labels": decide_by_frequency([el["face_labels"] for el in multilabels])
        }

    return decided_labels