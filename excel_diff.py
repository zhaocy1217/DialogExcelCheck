import pandas as pd
import difflib
import os
from loc_check import NoticeManager
from ret_code import ReturnCode
from config_path import ai_check_url, feishu_self_error_url, feishu_public_error_url
import requests
import json



class ExcelData:
    def __init__(self, id, cn):
        self.id = str(id)  # Ensure ID is treated as string for consistent comparison
        self.cn = str(cn)  # Ensure CN is treated as string for consistent comparison
    def __repr__(self):
        return f"ID: {self.id}, CN: {self.cn}"

    def __eq__(self, other):
        if not isinstance(other, ExcelData):
            return NotImplemented
        return self.id == other.id and self.cn == other.cn

    def __hash__(self):
        return hash((self.id, self.cn))

def read_excel_data(file_path, id_column, cn_column, sign_column):
    try:
        df = pd.read_excel(file_path, sheet_name="CN")
        id_column_index = df.columns.get_loc(id_column)
        cn_column_index = df.columns.get_loc(cn_column)
        data_list = []
        sign_column_index = df.columns.get_loc(sign_column)
        id_sign_dict = {}
        for index, row in df.iterrows():
            id_val = row.iloc[id_column_index]
            cn_val = row.iloc[cn_column_index]
            sign_val = row.iloc[sign_column_index]
            if id_val is not None and cn_val is not None:
                data_list.append(ExcelData(id_val, cn_val))
                id_sign_dict[str(id_val)] = str(sign_val)
            else:
                return None,None, ReturnCode(False, f"row {index} in {file_path} has missing data in '{id_column}' or '{cn_column}'.")
        return data_list, id_sign_dict, None
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None, ReturnCode(False, f"File not found at {file_path}")
    except KeyError as e:
        print(f"Error: Column not found in {file_path}. {e}")
        return None, ReturnCode(False, f"Column not found in {file_path}. {e}")
    except Exception as e:
        print(f"An unexpected error occurred while reading {file_path}: {e}")
        return None, ReturnCode(False, f"An unexpected error occurred while reading {file_path}: {e}")

def compare_excel_rows(current_excel_file, last_excel_file, svn_msg):
    differ = difflib.Differ()
    modified_rows = []
    old_data, old_id_sign_dict, old_data_ret_code = read_excel_data(last_excel_file, "id", "CN", "签名")
    if(old_data_ret_code is not None and not old_data_ret_code.success):
        return old_data_ret_code
    new_data, new_id_sign_dict, new_data_ret_code = read_excel_data(current_excel_file, "id", "CN", "签名")
    if(new_data_ret_code is not None and not new_data_ret_code.success):
        return new_data_ret_code
    sm = difflib.SequenceMatcher(None, [str(d) for d in old_data], [str(d) for d in new_data])
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if(tag != 'equal' and tag != 'delete'):
            modified_rows.extend(new_data[j1:j2])
            print(f"{tag:7s} a[{i1}:{i2}] ({old_data[i1:i2]!r}) --> b[{j1}:{j2}] ({new_data[j1:j2]!r})")
    headers = {'Content-Type': 'application/json'}
    jsonObj = {
        "svn_msg": svn_msg,
        "insert_modified": {}
    }
    for row in modified_rows:
            jsonObj['insert_modified'][row.id] = row.cn
    try:
        response = requests.request(method= 'post', url=ai_check_url, headers=headers, json= jsonObj)
        response_json_obj = json.loads(response.text)
        invalid_rows = response_json_obj["insert_modified"]
        #invalid_rows['TestError'] = 'TestError'
        if(len(invalid_rows) > 0):
            error_usrs = set()
            for id, cn in invalid_rows.items():
                if(id in new_id_sign_dict):
                    sign = new_id_sign_dict[id]
                    if(sign is None or sign == 'nan'or sign not in NoticeManager().name_id):
                        continue
                    error_usrs.add(NoticeManager().name_id.get(sign))
            error_usrs.add(NoticeManager().name_id.get('田明东'))
            NoticeManager().send_file_notice(
                url= feishu_public_error_url,
                title="错误通知",
                content=f'错误文本的SVN提交版本: {svn_msg}\n AI检查返回的错误文本: {invalid_rows}', 
                is_error=True,
                error_usrs= error_usrs# 填写需要通知用户的飞书id
            )
        print("ai check response: ", response.text)
    except Exception as e:
        return ReturnCode(False, f"Error: {e}")
    return ReturnCode(True, "")