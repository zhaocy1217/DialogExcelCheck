import loc_check
import asyncio
import svn_util
import time
import subprocess
import os
from ret_code import ReturnCode
from config_path import *
import sys
from excel_diff import compare_excel_rows
cur_excel_file_name = ""
last_excel_file_name = ""
def check_excel(excel_name):
    checker = loc_check.LocalizeChecker()
    checker.excel_name = excel_name
    coroutine = checker.check_CN(local_path=repository_local_path, is_pub=False)
    rst = asyncio.run(coroutine)
    return rst
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
if __name__ == "__main__":
    input_revision = -1
    if(len(sys.argv) > 1):
        input_revision = int(sys.argv[1])
    if(len(sys.argv) > 2):
        is_debug = (sys.argv[2]) == 'debug'
        if(is_debug):
            feishu_public_error_url = feishu_self_error_url
    if(svn_util.checkout_subprocess(repository_local_path)):
        print("checkout success")
    else:
        on_error_occur(feishu_self_error_url, "excel svn checkout failed")
        exit()
    commits, commit_ret_code = svn_util.get_last_one_day_commits(repository_local_path, path_in_repo, days=200)
    if(commit_ret_code is not None and not commit_ret_code.success):
        on_error_occur(feishu_self_error_url, commit_ret_code.error_content)
        exit()
    if(commits is not None and len(commits) > 1):
        for i in range(len(commits) - 1):
            if(input_revision == -1 or int(commits[i]['revision']) == input_revision):
                cur_commit = commits[i]
                last_commit = commits[i + 1]
            try:
                cur_revision = cur_commit['revision']
                last_revision = last_commit['revision']
                specific_revision = cur_revision
                ts =  time.time() * 1000
            except Exception as e:
                on_error_occur(feishu_self_error_url, f"excel svn two commits parse failed: {e}")
                exit()
            cur_excel_file_name = f"APS_Dialog_{cur_revision}_{ts}.xlsm"
            last_excel_file_name = f"APS_Dialog_{last_revision}_{ts}.xlsm"
            export_hist_file_rst = svn_util.get_file_at_revision_subprocess(repository_local_path, svn_url, path_in_repo, cur_revision, cur_excel_file_name)
            if(not export_hist_file_rst.success):
                on_error_occur(feishu_self_error_url, export_hist_file_rst.error_content)
                exit()
            export_last_file_rst = svn_util.get_file_at_revision_subprocess(repository_local_path, svn_url, path_in_repo, last_revision, last_excel_file_name)
            if(not export_last_file_rst.success):
                on_error_occur(feishu_self_error_url, export_last_file_rst.error_content)
                exit()
            try:
                check_excel(cur_excel_file_name)
            except Exception as e:
                on_error_occur(feishu_self_error_url, f"excel check failed: {e}")
                exit()
            try:
                cur_excel_file_full_name = os.path.join(repository_local_path, cur_excel_file_name)
                last_excel_file_full_name = os.path.join(repository_local_path, last_excel_file_name)
                compare_rst =  compare_excel_rows(cur_excel_file_full_name, last_excel_file_full_name, cur_revision)
                if(not compare_rst.success):
                    on_error_occur(feishu_self_error_url, compare_rst.error_content)
                    exit()
                delete_files([cur_excel_file_full_name, last_excel_file_full_name])
                if(input_revision != -1):
                    break
            except Exception as e:
                on_error_occur(feishu_self_error_url, f"excel diff failed: {e}")
                exit()
    else:
        on_error_occur(feishu_self_error_url, "excel svn get last two commits failed")
        exit()