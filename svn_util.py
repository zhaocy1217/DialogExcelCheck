import subprocess
from client import Client
import os
from ret_code import ReturnCode
import time
from client import username_password
def checkout_subprocess(repo_path_local):
    command = [
        "svn","checkout","."
    ]
    command.extend(username_password)
    try:
        subprocess.run(command, cwd=repo_path_local, check=True, capture_output=True, text=True)
        return ReturnCode(success=True, error_content="")
    except subprocess.CalledProcessError as e:
        return ReturnCode(success=False, error_content=f"Error exporting file: {e.stderr}")
    except FileNotFoundError:
        return ReturnCode(success=False, error_content="Error: The 'svn' command was not found. Please ensure Subversion is installed and in your system's PATH.")

def get_file_at_revision_subprocess(repo_path_local,repo_url, file_path, revision, output_file):
    full_file_path = f"{repo_url}/{file_path}"
    command = [
        "svn","export","--force", "--revision",str(revision),full_file_path,
        output_file
    ]
    command.extend(username_password)
    try:
        subprocess.run(command, cwd=repo_path_local, check=True, capture_output=True, text=True)
        return ReturnCode(success=True, error_content="")
    except subprocess.CalledProcessError as e:
        return ReturnCode(success=False, error_content=f"Error exporting file: {e.stderr}")
    except FileNotFoundError:
        return ReturnCode(success=False, error_content="Error: The 'svn' command was not found. Please ensure Subversion is installed and in your system's PATH.")
#get_file_at_revision_subprocess(repository_local_path, svn_url, path_in_repo, specific_revision, local_filename)
def get_last_two_commits(repository_local_path, file_path):
    try:
        client = Client(cwd = repository_local_path)
        log_entries = client.log(
            file_path, 2
        )
        if log_entries:
            commits = []
            for log_entry in log_entries:
                commits.append({
                    'revision': log_entry['revision'],
                    'author': log_entry['author'],
                    'date': log_entry['date'],  # This is a timestamp
                    'message': log_entry['msg'],
                })
            return commits, None
        else:
            return None, ReturnCode(success=False, error_content=f"No commit history found for: {file_path}")
    except Exception as e:
        return None, ReturnCode(success=False, error_content=f"Error accessing SVN: {e}")

def get_last_one_day_commits(repository_local_path, file_path, days = 1):
    try:
        client = Client(cwd = repository_local_path)
        log_entries = client.log(
            file_path, 100
        )
        if log_entries:
            commits = []
            date_one_day_ago =  time.time() - 24 * 60 * 60*days
            for log_entry in log_entries:
                d = time.mktime(time.strptime(log_entry['date'], "%Y-%m-%dT%H:%M:%S.%fZ"))
                if(d < date_one_day_ago):
                    break
                commits.append({
                    'revision': log_entry['revision'],
                    'author': log_entry['author'],
                    'date': log_entry['date'],  # This is a timestamp
                    'message': log_entry['msg'],
                })
            return commits, None
        else:
            return None, ReturnCode(success=False, error_content=f"No commit history found for: {file_path}")
    except Exception as e:
        return None, ReturnCode(success=False, error_content=f"Error accessing SVN: {e}")

