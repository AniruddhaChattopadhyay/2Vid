import json
from newsX_backend.enums.model_enums import ItemConfigEnum
from newsX_backend.utils.db_utils import update_item_config

def save_item_config(id,data):
    item_config_dict = {ItemConfigEnum.id.value : id}
    if data is not None:
        if 'email' in data.keys():
            item_config_dict[ItemConfigEnum.email_list.value] =  json.dumps([data['email']])
        
        if 'isBgm' in data.keys():
            if data['isBgm'] == "TRUE":
                item_config_dict[ItemConfigEnum.is_bgm_enabled.value] =  True
            else:
                item_config_dict[ItemConfigEnum.is_bgm_enabled.value] =  False
    update_item_config(item_config_dict)