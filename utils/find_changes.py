from .decisions import load_json

mappings = load_json("info.json")

FEATURE_TO_MODEL = mappings["FEATURE_TO_MODEL"]
FEATURE_TO_BOUNDING_BOX = mappings["FEATURE_TO_BOUNDING_BOX"]
MODELS_TO_FEATURES = mappings["MODELS_TO_FEATURES"]
BB_TO_FEATURES = mappings["BB_TO_FEATURES"]


def new_feature(path, change, actions):
    # Added label for feature
    # We need to find the parameters:
    #     1) image name
    #     2) bounding box value for the feature
    #     3) value(Yes, No)
    #     Pass all the parameters to a function that will:
    #         a) Crop the original image
    #         b) Rotate and crop other images

    image_name = path[0]
    feature_name = path[-1]
    label = change.t2
    model_name = FEATURE_TO_MODEL[feature_name]
    bounding_box_name = FEATURE_TO_BOUNDING_BOX[feature_name]

    obj_after = change.all_up.t2[image_name]

    bounding_box = obj_after["bounding_boxes"].get(bounding_box_name)

    action = {
        "image_name": image_name,
        "model_name": model_name,
        "bounding_box": bounding_box,
        "label": label
    }

    actions["add"].append(action)

def new_image(path, change, actions):
    # print("New image", path, change)
    obj = change.t2

    image_name = obj["image_name"]
    face_labels = obj["face_labels"]
    bounding_boxes = obj["bounding_boxes"]

    for feature_name, label in face_labels.items():
        model_name = FEATURE_TO_MODEL[feature_name]
        bounding_box_name = FEATURE_TO_BOUNDING_BOX[feature_name]
        bounding_box = bounding_boxes.get(bounding_box_name)

        action = {
            "image_name": image_name,
            "model_name": model_name,
            "bounding_box": bounding_box,
            "label": label
        }

        actions["add"].append(action)

def modified_feature(path, change, actions):
    image_name = path[0]
    feature_name = path[-1]
    model_name = FEATURE_TO_MODEL[feature_name]
    bounding_box_name = FEATURE_TO_BOUNDING_BOX[feature_name]

    label_before = change.t1
    label_after = change.t2

    obj_after = change.all_up.t2[image_name]
    bounding_box = obj_after["bounding_boxes"].get(bounding_box_name)

    if label_before in ("Yes", "No"):
        remove_action = {
            "image_name": image_name,
            "model_name": model_name,
            "bounding_box": bounding_box,
            "label": label_before
        }
        actions["delete"].append(remove_action)

    if label_after in ("Yes", "No"):
        add_action = {
            "image_name": image_name,
            "model_name": model_name,
            "bounding_box": bounding_box,
            "label": label_after
        }
        actions["add"].append(add_action)

def modified_bounding_box(path, change, actions):
    # print("Modified bounding box")
    image_name = path[0]
    bounding_box_name = path[2]

    features = BB_TO_FEATURES[bounding_box_name]

    obj_before = change.all_up.t1[image_name]
    obj_after = change.all_up.t2[image_name]

    bounding_box = obj_after["bounding_boxes"][bounding_box_name]

    for f in features:
        model_name = FEATURE_TO_MODEL.get(f)

        label_before = obj_before["face_labels"].get(f)
        label_after = obj_after["face_labels"].get(f)

        if label_before in ("Yes", "No"):
            remove_action = {
                "image_name": image_name,
                "model_name": model_name,
                "bounding_box": bounding_box,
                "label": label_before
            }
            actions["delete"].append(remove_action)

        if label_after in ("Yes", "No"):
            add_action = {
                "image_name": image_name,
                "model_name": model_name,
                "bounding_box": bounding_box,
                "label": label_after
            }
            actions["add"].append(add_action)

def added_bounding_box(path, change, actions):
    # print("Added bounding box")
    image_name = path[0]
    bounding_box_name = path[2]

    # print("bounding_box_name", bounding_box_name)

    features = BB_TO_FEATURES[bounding_box_name]

    # obj_before = change.all_up.t1[image_name]
    obj_after = change.all_up.t2[image_name]

    bounding_box = obj_after["bounding_boxes"][bounding_box_name]

    for f in features:
        model_name = FEATURE_TO_MODEL.get(f)

        label_after = obj_after["face_labels"].get(f)

        if label_after in ("Yes", "No"):
            action = {
                "image_name": image_name,
                "model_name": model_name,
                "bounding_box": bounding_box,
                "label": label_after
            }
            actions["add"].append(action)



def changes_analyser(diff):
    actions = {"delete": [], "add": []}
    for change_type, list_of_changes in diff.items():
        for change in list_of_changes:
            #dictionary_item_added
            path = change.path(output_format="list")

            if len(path) == 1:
                # New image added to labels
                new_image(path, change, actions)

            elif len(path) >= 3:
                # Existing image but added/removed labels, or modified
                if path[1] == "face_labels":
                    if change_type == "dictionary_item_added":
                        new_feature(path, change, actions)
                    elif change_type == "values_changed":
                        modified_feature(path, change, actions)
                elif path[1] == "bounding_boxes":
                    if change_type == "dictionary_item_added":
                        added_bounding_box(path, change, actions)
                    elif change_type == "values_changed":
                        modified_bounding_box(path, change, actions)
                else:
                    raise Exception("Object change was not caught")
            else:
                raise Exception("Path length not 1 or 3", path)
    return actions