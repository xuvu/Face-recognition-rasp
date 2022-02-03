import json
import os
from datetime import datetime

import file
import shutil
import urllib
from urllib.request import urlopen


class Server:
    def __init__(self, postreciever, room_id_code):
        self.postr = str(postreciever) + "/raspberrypi_communication/postReceiver.php"
        self.room_id_code = room_id_code

        # connection status
        self.connection_status = False

        # download zipped file
        self.zip_location_on_server = self.postr.replace("postReceiver.php", "face.zip")

        # check for connection
        self.is_connect()

    def is_connect(self):
        try:
            urlopen(self.postr, timeout=1)
            self.connection_status = True
            return True
        except urllib.error.URLError as Error:
            self.connection_status = False
            print(str(Error) + " Can't connect to server")
            return False

    def check_update_model(self):
        if file.get_latest_model(self.postr) == "0":
            print("no model on server")
            return False
        elif file.get_latest_model(self.postr) != file.get_current_model_name() or not os.path.exists(
                "model/" + file.get_current_model_name()):
            return True
        else:
            return False

    def update_model(self):
        try:
            # remove old model
            if os.path.exists("model/" + str(file.get_current_model_name())):
                os.remove("model/" + str(file.get_current_model_name()))
            elif not os.path.exists("model"):
                os.mkdir("model")

        except OSError as error:
            print(error)

        # locate .txt
        txt_location_on_server = self.postr.replace("postReceiver.php", "model/namemodel.txt")
        # download .txt
        file.download_file(txt_location_on_server, "model/")

        # locate model
        model_location_on_server = self.postr.replace("postReceiver.php", "model/" + file.get_current_model_name())
        # download model
        file.download_file(model_location_on_server, "model/")

    def check_update_permission(self):
        if file.get_latest_permission(self.postr) == "0":
            print("no permission on server")
            return False
        elif file.get_latest_permission(self.postr) != file.get_current_permission_name() or not os.path.exists(
                "permission/" + file.get_current_permission_name()):
            return True
        else:
            return False

    def update_permission(self):
        try:
            # remove old model
            if os.path.exists("permission/" + str(file.get_current_permission_name())):
                os.remove("permission/" + str(file.get_current_permission_name()))
            elif not os.path.exists("permission"):
                os.mkdir("permission")

        except OSError as error:
            print(error)
        # locate .txt
        txt_location_on_server = self.postr.replace("postReceiver.php", "permission/name_permission.txt")
        # download .txt
        file.download_file(txt_location_on_server, "permission/")

        # locate model
        model_location_on_server = self.postr.replace("postReceiver.php",
                                                      "permission/" + file.get_current_permission_name())
        # download model
        file.download_file(model_location_on_server, "permission/")

    def send_log(self):
        req = None
        if self.connection_status:
            with open('log.json', 'r') as data_file:
                data = json.load(data_file)

            if len(data) != 0:
                for i in range(len(data)):
                    req = file.send_log(self.postr,
                                        id_mem=data[0]["id_mem"],
                                        id_code=data[0]["id_code"],
                                        full_name=data[0]["full_name"],
                                        id_room=data[0]["id_room"],
                                        room_name=data[0]["room_name"],
                                        time_stamp=data[0]["time_stamp"])
                    data.pop(0)

            with open('log.json', 'w') as data_file:
                json.dump(data, data_file)
            return req

    def save_log(self, id_code):
        if not os.path.exists("log.json"):
            list_log = file.get_current_permission_list(self.room_id_code, str(id_code))
            list_log[0]["time_stamp"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # Serializing json
            json_object = json.dumps(list_log, indent=6)

            # Writing to sample.json
            with open("log.json", "w") as outfile:
                outfile.write(json_object)
        else:
            list_log = file.get_current_permission_list(self.room_id_code, str(id_code))[0]
            list_log["time_stamp"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.write_json(list_log)

    def write_json(self, new_data, filename='log.json'):
        with open(filename, 'r+') as file:
            # First we load existing data into a dict.
            file_data = json.load(file)
            # Join new_data with file_data inside emp_details
            file_data.append(new_data)
            # Sets file's current position at offset.
            file.seek(0)
            # convert back to json.
            json.dump(file_data, file, indent=5)

    def check_update_room_status(self):
        if file.get_latest_room_status(self.postr) == "0":
            print("no room stat on server")
            return False
        elif file.get_latest_room_status(self.postr) != file.get_current_name_room_status() or not os.path.exists(
                "timeout/" + file.get_current_name_room_status()):
            return True
        else:
            return False

    def update_room_status(self):
        try:
            # remove old model
            if os.path.exists("timeout/" + str(file.get_current_name_room_status())):
                os.remove("timeout/" + str(file.get_current_name_room_status()))
            elif not os.path.exists("timeout"):
                os.mkdir("timeout")

        except OSError as error:
            print(error)
        # locate .txt
        txt_location_on_server = self.postr.replace("postReceiver.php", "timeout/name_roomstatus.txt")
        # download .txt
        file.download_file(txt_location_on_server, "timeout/")

        # locate model
        model_location_on_server = self.postr.replace("postReceiver.php",
                                                      "timeout/" + file.get_current_name_room_status())
        # download model
        file.download_file(model_location_on_server, "timeout/")


class Server_admin:

    def __init__(self, postreciever):
        self.postr = str(postreciever) + "/raspberrypi_communication/postReceiver.php"
        self.connection_status = False
        self.is_connect()
        self.zip_location_on_server = self.postr.replace("postReceiver.php", "face.zip")

    def is_connect(self):
        try:
            urlopen(self.postr, timeout=1)
            self.connection_status = True
            return True
        except urllib.error.URLError as Error:
            self.connection_status = False
            print(str(Error) + " Can't connect to server")
            return False

    def upload_face_to_server(self, name):
        try:
            # get in faces directory
            os.chdir('datasets/faces')

            file.zipdir(name, name)
            file.upload_face(name + ".zip", self.postr)
            os.remove(name + ".zip")

            # remove faces folder
            dir_path = name
            try:
                shutil.rmtree(dir_path)
            except OSError as e:
                print("Error: %s : %s" % (dir_path, e.strerror))

            # get back to root directory
            os.chdir('../../')
        except:
            print("Can't upload face to server")

    def download_face_from_server(self):
        try:
            # signal for server to zip the files
            file.download_prep(self.postr)
            # download zipped file from server
            file.download_file(self.zip_location_on_server, os.getcwd())

            # extract to this machine
            file.extract_file("face.zip", "datasets/faces/")
            file.os.remove("face.zip")
        except:
            print("Can't download face from server")

    def upload_model(self):
        try:
            file.upload_model("model/namemodel.txt", self.postr)
            file.upload_model("model/" + file.get_current_model_name(), self.postr)
        except:
            print("Can't upload model to server")

    def get_list_for_cature(self):
        return file.get_list_capture(self.postr)


#server = Server("http://skbright.totddns.com:28006/nsc_backup", "296fyXYNGtjkH6BlthlKkd8D2h3gT")
#print(server.update_room_status())
