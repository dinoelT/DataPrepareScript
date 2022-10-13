test_changes = [
    {
        "test_name": "Added full image",
        "obj1": {

        },
        "obj2": {
            "img1.jpg": {
                "image_name": "img1.jpg",
                "bounding_boxes": {
                    "EyeRight_Lower": {
                        "top_left": {
                            "x": 1174,
                            "y": 3050
                        },
                        "bottom_right": {
                            "x": 2153,
                            "y": 3629
                        }
                    }
                },
                "face_labels": {
                    "EyeRight_Lower_Tearsack": "Yes"
                }
            }
        },
    },
    {
        "test_name": "Added bounding_box value",
        "obj1": {
            "img1.jpg": {
                "image_name": "img1.jpg",
                "bounding_boxes": {

                },
                "face_labels": {
                    "EyeRight_Lower_Tearsack": "Yes"
                }
            }
        },
        "obj2": {
            "img1.jpg": {
                "image_name": "img1.jpg",
                "bounding_boxes": {
                    "EyeRight_Lower": {
                        "top_left": {
                            "x": 1174,
                            "y": 3050
                        },
                        "bottom_right": {
                            "x": 2153,
                            "y": 3629
                        }
                    }
                },
                "face_labels": {
                    "EyeRight_Lower_Tearsack": "Yes"
                }
            }
        },
    },
    {
        "test_name": "Changed bounding_box value",
        "obj1": {
            "img1.jpg": {
                "image_name": "img1.jpg",
                "bounding_boxes": {
                    "EyeRight_Lower": {
                        "top_left": {
                            "x": 1174,
                            "y": 3038
                        },
                        "bottom_right": {
                            "x": 2153,
                            "y": 3629
                        }
                    }
                },
                "face_labels": {
                    "EyeRight_Lower_Tearsack": "Yes"
                }
            }
        },
        "obj2": {
            "img1.jpg": {
                "image_name": "img1.jpg",
                "bounding_boxes": {
                    "EyeRight_Lower": {
                        "top_left": {
                            "x": 1174,
                            "y": 3050
                        },
                        "bottom_right": {
                            "x": 2153,
                            "y": 3629
                        }
                    }
                },
                "face_labels": {
                    "EyeRight_Lower_Tearsack": "Yes"
                }
            }
        },
    },

    {
        "test_name": "Added new feature",
        "obj1": {
            "img1.jpg": {
                "image_name": "img1.jpg",
                "bounding_boxes": {
                    "EyeRight_Lower": {
                        "top_left": {
                            "x": 1174,
                            "y": 3038
                        },
                        "bottom_right": {
                            "x": 2153,
                            "y": 3629
                        }
                    }
                },
                "face_labels": {
                }
            }
        },
        "obj2": {
            "img1.jpg": {
                "image_name": "img1.jpg",
                "bounding_boxes": {
                    "EyeRight_Lower": {
                        "top_left": {
                            "x": 1174,
                            "y": 3038
                        },
                        "bottom_right": {
                            "x": 2153,
                            "y": 3629
                        }
                    }
                },
                "face_labels": {
                    "EyeRight_Lower_Tearsack": "Yes"
                }
            }
        },
    },
    {
        "test_name": "Changed feature value",
        "obj1": {
            "img1.jpg": {
                "image_name": "img1.jpg",
                "bounding_boxes": {
                    "MouthWhole_Around": {
                        "top_left": {
                            "x": 1174,
                            "y": 3038
                        },
                        "bottom_right": {
                            "x": 2153,
                            "y": 3629
                        }
                    }
                },
                "face_labels": {
                    "MouthWhole_Around_BrownYellow": "Yes"
                }
            }
        },
        "obj2": {
            "img1.jpg": {
                "image_name": "img1.jpg",
                "bounding_boxes": {
                    "MouthWhole_Around": {
                        "top_left": {
                            "x": 1174,
                            "y": 3038
                        },
                        "bottom_right": {
                            "x": 2153,
                            "y": 3629
                        }
                    }
                },
                "face_labels": {
                    "MouthWhole_Around_BrownYellow": "No"
                }
            }
        },
    }
]


if __name__ == "__main__":
    from utils.find_changes import changes_analyser
    from deepdiff import DeepDiff
    from pprint import pprint

    for test in test_changes:
        print()
        print(f"<< {test['test_name']} >>")

        obj1 = test["obj1"]
        obj2 = test["obj2"]

        diff = DeepDiff(obj1, obj2, view="tree")
        actions = changes_analyser(diff)
        pprint(actions)
