import config_path
import loc_check
import asyncio
import svn_util
import time
import subprocess
import os
from ret_code import ReturnCode
from config_path import *
import sys
import json
from excel_diff import compare_excel_rows
cur_excel_file_name = ""
last_excel_file_name = ""
def check_excel(excel_name, is_pub = False):
    checker = loc_check.LocalizeChecker()
    checker.excel_name = excel_name
    coroutine = checker.check_CN(local_path=repository_local_path, is_pub=is_pub)
    asyncio.run(coroutine)
    coroutine2 = checker.warn_CN(local_path=repository_local_path)
    asyncio.run(coroutine2)
def on_error_occur(url, content):
    cur_excel_file_full_name = os.path.join(repository_local_path, cur_excel_file_name)
    last_excel_file_full_name = os.path.join(repository_local_path, last_excel_file_name)
    loc_check.NoticeManager().send_file_notice(
            url=url,
            title="错误通知",
            content=content, 
            is_error=True,
            error_usrs={loc_check.NoticeManager().name_id.get('赵超跃')}# 填写需要通知用户的飞书id
        )
    delete_files([cur_excel_file_full_name, last_excel_file_full_name])
    raise Exception(content)
def run_mono_excel_diff(current_excel_name, last_excel_name, svn_msg):
    sheet = "CN"
    column = "CN"
    command = [
        "dotnet",exe_file,f"-p={last_excel_name}",f"-c={current_excel_name}", f'-sheet={sheet}', f'-column={column}', f'-svn_msg={svn_msg}'
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True, cwd=exe_cwd)
        return ReturnCode(success=True, error_content="")
    except subprocess.CalledProcessError as e:
        return ReturnCode(success=False, error_content=f"Error exporting file: {e.stderr}")
    except FileNotFoundError:
        return ReturnCode(success=False, error_content="Error: The 'svn' command was not found. Please ensure Subversion is installed and in your system's PATH.")
def delete_files(file_names):
    for file_name in file_names:
        if(os.path.isfile(file_name) and os.path.exists(file_name)):
            os.remove(file_name)
def get_resolved_record():
    record_file_path = get_record_file_path()
    if(os.path.exists(record_file_path) and os.path.isfile(record_file_path)):
        with open(record_file_path, 'r') as file:
            json_obj = json.load(file)
            if(json_obj is None):
                return []
            return json_obj
    return []
def is_resolved(revision):
    return revision in  get_resolved_record()
def mark_resolved(revision):
    resolved_record = get_resolved_record()
    if(revision not in resolved_record):
        resolved_record.append(revision)
        with open(get_record_file_path(), 'w') as file:
            json.dump(resolved_record, file)

if __name__ == "__main__":
    input_revision = -1
    only_check_excel_is_pub = False
    if(len(sys.argv) > 1):
        input_revision = int(sys.argv[1])
    if(len(sys.argv) > 2):
        only_check_excel_is_pub = (sys.argv[2]) == 'True' or (sys.argv[2]) == 'true' or (sys.argv[2]) == '1' or (sys.argv[2]) == True
    ret_code = svn_util.checkout_subprocess(repository_local_path)
    if(ret_code.success):
        print("checkout success")
        if(only_check_excel_is_pub):
            check_excel(config_path.path_in_repo, True)
            exit(0)
    else:
        on_error_occur(feishu_self_error_url, ret_code.error_content)
    commits, commit_ret_code = svn_util.get_last_one_day_commits(repository_local_path, path_in_repo, days=200)
    if(commit_ret_code is not None and not commit_ret_code.success):
        on_error_occur(feishu_self_error_url, commit_ret_code.error_content)
    if(commits is None or len(commits) == 0):
        on_error_occur(feishu_self_error_url, "excel svn get last one day commits failed")
    if(len(commits) == 1):
        check_excel(config_path.path_in_repo)
    if(len(commits) > 1):
        for i in range(len(commits) - 1):
            if(input_revision == -1 or int(commits[i]['revision']) == input_revision):
                cur_commit = commits[i]
                last_commit = commits[i + 1]
                try:
                    cur_revision = cur_commit['revision']
                    last_revision = last_commit['revision']
                    if(is_resolved(cur_revision)):
                        continue
                    specific_revision = cur_revision
                    ts =  int(time.time() * 1000)
                except Exception as e:
                    on_error_occur(feishu_self_error_url, f"excel svn two commits parse failed: {e}")
                cur_excel_file_name = f"APS_Dialog_{cur_revision}_{ts}.xlsm"
                last_excel_file_name = f"APS_Dialog_{last_revision}_{ts}.xlsm"
                export_hist_file_rst = svn_util.get_file_at_revision_subprocess(repository_local_path, svn_url, path_in_repo, cur_revision, cur_excel_file_name)
                if(not export_hist_file_rst.success):
                    on_error_occur(feishu_self_error_url, export_hist_file_rst.error_content)
                export_last_file_rst = svn_util.get_file_at_revision_subprocess(repository_local_path, svn_url, path_in_repo, last_revision, last_excel_file_name)
                if(not export_last_file_rst.success):
                    on_error_occur(feishu_self_error_url, export_last_file_rst.error_content)
                try:
                    if(i == 0):
                        check_excel(cur_excel_file_name)
                except Exception as e:
                    on_error_occur(feishu_self_error_url, f"excel check failed: {e}")
                try:
                    cur_excel_file_full_name = os.path.join(repository_local_path, cur_excel_file_name)
                    last_excel_file_full_name = os.path.join(repository_local_path, last_excel_file_name)
                    compare_rst =  compare_excel_rows(cur_excel_file_full_name, last_excel_file_full_name, cur_revision)
                    if(not compare_rst.success):
                        on_error_occur(feishu_self_error_url, compare_rst.error_content)
                    mark_resolved(cur_revision)
                    delete_files([cur_excel_file_full_name, last_excel_file_full_name])
                    
                    if(input_revision != -1):
                        break
                except Exception as e:
                    on_error_occur(feishu_self_error_url, f"excel diff failed: {e}")
   