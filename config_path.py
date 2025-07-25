import os
from pathlib import Path
repository_local_path = "D://SVNTest_2"
svn_url = "svn://svn.svnbucket.com/zcyandy/SvnTest"
path_in_repo = "trunk/APS_Dialog.xlsm" #/Volumes/2T/BuildWorkspace/aps_client_table_wx
exe_cwd = "D:/out"
exe_file = os.path.join(exe_cwd, "DialogExcelExtract.exe")
feishu_self_error_url = "https://open.feishu.cn/open-apis/bot/v2/hook/3b03d0a4-e36b-4c2f-b258-5e5da5baa392"
ai_check_url = "https://biai.businsights.net/game/502/cn_text/check";
feishu_public_error_url = feishu_self_error_url# "https://open.feishu.cn/open-apis/bot/v2/hook/e3069555-89da-4679-89ee-3bb5ab7bb1f2"
record_file_path = ".resolved_revision.txt"
def get_record_file_path():
    return os.path.join(Path(__file__).parent.absolute(), record_file_path)
def get_local_excel_special_check_config():
    return os.path.join(Path(__file__).parent.absolute(), "cn_special_config.json")
def get_current_git_repo_path():
    return Path(__file__).parent.absolute()
def get_cn_special_config_path():
    return os.path.join(repository_local_path, "Localization/cn_special_config.json")