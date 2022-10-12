from utils7.constants import IMAGES_PATH
from utils7.helper_func import ensure_token, get_new_data, get_tinydb
from tinydb import where
# ensure_token()

# from datetime import datetime

# dt = datetime(year = 2022, month = 9, day = 25)
# data = get_new_data(dt)



# print(len(data))
db = get_tinydb()


res = db.search(where("bounding_boxes")["MouthWhole"]["top_left"]["x"] == 1174)
print(res)