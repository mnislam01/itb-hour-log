import random
import time
from datetime import datetime
import requests
import csv


# Runtime Database
obj_store = {}


# Constant Class
class API:
    login = 1
    hour_log = 2
    endpoint_map = {
        login: "https://it-button.com/api/user-login/",
        hour_log: "https://it-button.com/api/projects/{project_id}/hour/"
    }

    @staticmethod
    def get_endpoint(api, project_id):
        return API.endpoint_map[api].format(project_id=project_id)


# Aborting function
def abort(message):
    print(f"{datetime.now()}\n\t Aborting - {message}")
    exit(0)


# Logging function
def log(message):
    print(f"{datetime.now()}\n\t{message}")


# Request making function
def make_request(payload, headers, api, project_id):
    endpoint = API.get_endpoint(api=api, project_id=project_id)
    if api != API.login:
        log(f"Payload: {payload})")
    log(f"API: {endpoint}")
    res = requests.post(url=endpoint, data=payload, headers=headers)
    if res.status_code not in [200, 201]:
        return abort(f"Response: {res.json()}")
    return res.json()


# Function to return random hour log
def get_work_duration():
    return random.randint(5, 8)


# Login Function
def log_in():
    log("Reading file: '.secrets'")
    with open(".secrets", "r") as secret_file:
        data = secret_file.readline()
        log("Reading file done")
        if not data:
            return abort("Secret file empty !!!!!\nLogin Failed !!!! \nAborting...")
        email, passwd = data.split(",")
        if not (email and passwd):
            return abort("No email or password !!! Aborting...")
        log(f"Email: {email}, Password: {str(passwd).translate('*'*256)}")
        log("Sending login request")
        payload = {
            "email": email,
            "password": passwd
        }
        data = make_request(payload=payload, headers={}, api=API.login, project_id=None)
        log("Login complete")
        obj_store.update({"token": f"JWT {data['access']}"})
        log("Saved token to Object Store")


# Hour Log function
def log_hours():
    with open("logfile.csv", "r") as log_file:
        log("Reading 'logfile.csv'")
        csv_log_file = csv.DictReader(log_file, delimiter=',')
        log("Read complete")
        log("Getting token from object store")
        token = obj_store.get("token", None)
        if not token:
            return abort("No token\n Aborting....")
        log(f"Got token: {token}")
        headers = {
            "Authorization": token
        }
        log("Getting data ready")
        for work_log in csv_log_file:
            payload = {
                "assignee_id": int(work_log["Assignee"]),
                "description": work_log["Description"],
                "issue_id": int(work_log["Issue"]),
                "project_id": int(work_log["Project"]),
                "worked_date": work_log["Date"],
                "duration": str(get_work_duration())
            }
            log(f"Logging for date: {payload['worked_date']}")
            data = make_request(payload=payload, headers=headers, api=API.hour_log, project_id=int(work_log["Project"]))
            if not data:
                abort("Log could not saved")
            elif not data.get("isSaved", False):
                abort("Log could not saved")
            elif data and data.get("isSaved", True):
                log(f"Log Saved. ID: {data['id']}")
            else:
                abort("Unknown error")
            time.sleep(5)


if __name__ == '__main__':
    print("--------------------")
    log("Begin HourLog")
    log_in()
    log_hours()
