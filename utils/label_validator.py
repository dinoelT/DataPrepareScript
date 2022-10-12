import pydantic
from pydantic import BaseModel
from typing import Dict, List, Optional, Union
from typing_extensions import Literal
import datetime
from enum import Enum
import json

ALLOWED_VALUES = ["Yes", "No", "Undef", "NotLabeled"]

# Allowed face features
ALLOWED_FEATURES = [
    'EyeLeft_NasalRoot_Dark',
    'EyeRight_NasalRoot_Dark',
    'EyeLeft_OuterCorner_Dark',
    'EyeRight_OuterCorner_Dark',
    'MouthUpper_Lip_BrightLine',
    'MouthLower_Lip_BrightLine',
    'EyeLeft_InnerCorner_BrightDot',
    'EyeRight_InnerCorner_BrightDot',
    'EyeLeft_InnerCorner_Bright',
    'EyeRight_InnerCorner_Bright',
    'EyeLeft_Whole_Protruding',
    'EyeRight_Whole_Protruding',
    'ChinWhole_Tip_Red',
    'ChinWhole_Tip_Dimples',
    'MouthLeft_Corner_Cracked',
    'MouthRight_Corner_Cracked',
    'MouthLeft_Corner_Red',
    'MouthRight_Corner_Red',
    'MouthUpper_Pallium_VerticalWrinkles',
    'MouthUpper_Pallium_Red',
    'MouthUpper_Pallium_Dark',
    'EyeLeft_UpperLid_Droopy',
    'EyeRight_UpperLid_Droopy',
    'EyeLeft_Lower_Pale',
    'EyeRight_Lower_Pale',
    'ForeheadCenter_Lower_VerticalWrinkles',
    'EyeLeft_Lower_Tearsack',
    'EyeRight_Lower_Tearsack',
    'EyeLeft_Lower_Dark',
    'EyeRight_Lower_Dark',
    'MouthLower_UnderLip_Swollen',
    'MouthUpper_UnderLip_VerticalWrinkles',
    'TempleLeft_Whole_Dented',
    'TempleRight_Whole_Dented',
    'CheekLeft_Whole_Red',
    'CheekRight_Whole_Red',
    'MouthWhole_Around_BrownYellow',
    'MouthWhole_Lips_Smooth',
    'MouthWhole_Lips_AlteredStructure']


ALLOWED_REGIONS = [
    'ChinWhole_Tip',
    'EyeLeft_InnerCorner',
    'EyeLeft_Lower',
    'EyeLeft_LowerLid',
    'EyeLeft_NasalRoot',
    'EyeLeft_OuterCorner',
    'EyeLeft_UpperLid',
    'EyeLeft_Whole',
    'EyeRight_InnerCorner',
    'EyeRight_Lower',
    'EyeRight_LowerLid',
    'EyeRight_NasalRoot',
    'EyeRight_OuterCorner',
    'EyeRight_UpperLid',
    'EyeRight_Whole',
    'ForeheadCenter_Lower',
    'MouthLeft_Corner',
    'MouthLower_Lip',
    'MouthLower_UnderLip',
    'MouthRight_Corner',
    'MouthUpper_Lip',
    'MouthUpper_Pallium',
    'MouthUpper_UnderLip',
    'Mouth_Whole',
    'TempleLeft_Whole',
    'TempleRight_Whole']

# =========================================================================

class Point(BaseModel):
    x: int
    y: int

class BoundingBox(BaseModel):
    top_left: Point
    bottom_right: Point

    @pydantic.root_validator
    def validate_bounding_box(cls, values):
        top_left = values["top_left"]
        bottom_right = values["bottom_right"]

        left = top_left.x
        top = top_left.y
        right = bottom_right.x
        bottom = bottom_right.y

        # If the values are reversed, the bounding box is not visible
        #TODO: Add a limit value so that we don't have bounding boxes that are too small
        if left > right or top > bottom:
            values["top_left"] = None
            values["bottom_right"] = None
        return values


class ImageLabel(BaseModel):

    image_name: str
    face_labels: Dict[str, str]
    email: str
    bounding_boxes: Dict[str, Union[BoundingBox, Literal["NotValid"]]]


    @pydantic.root_validator
    def validate_image_labels(cls, values):
        # Validate face_labels
        valid_face_labels = {}
        errors = []
        for feature_name, value in values["face_labels"].items():
            isValid = True

            if feature_name not in ALLOWED_FEATURES:
                errors.append(f"Feature name '{feature_name}' is not valid")
                isValid = False

            if value not in ALLOWED_VALUES:
                errors.append(f"Feature value '{value}' is not valid for feature '{feature_name}'")
                isValid = False

            if isValid:
                valid_face_labels[feature_name] = value
        values["face_labels"] = valid_face_labels
        if errors:
          raise Exception(json.dumps(errors))
        return values