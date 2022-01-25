import json
import sys
import os.path
from datetime import datetime
from os.path import basename
import requests
import os
import zipfile


def get_current_name_room_status():
    try:
        f = open("timeout/name_roomstatus.txt", "r")
        return f.readline().strip()
        f.close()
    except:
        NameError


def get_this_room_status(room_id_code):
    try:
        # Opening JSON file
        f = open("timeout/" + get_current_name_room_status(), )
        data = json.load(f)
        for i in data:
            if i["room_id_code"] == str(room_id_code):
                return i
        f.close()
    except:
        print("There's no time_out list in this machine")

def get_current_room_status_list(room_id_code, key):
    try:
        # Opening JSON file
        f = open("timeout/" + get_current_name_room_status(), )
        data = json.load(f)
        list = []
        for i in data:
            if i["room_id_code"] == str(room_id_code):
                list.append(i[key])
        f.close()
        # return list
        return list
    except:
        print("There's no time_out list in this machine")


def get_all_current_room_status_list():
    try:
        # Opening JSON file
        f = open("timeout/" + get_current_name_room_status(), )
        data = json.load(f)
        f.close()
        # return list
        return data
    except:
        print("There's no time_out list in this machine")


# check lastest permission on server
def get_latest_room_status(link_of_postreciever_server):
    req = requests.post(link_of_postreciever_server, data={'key': 'check_latest_time'})
    # .strip() = Trimming Whitespaces
    return req.text.strip()


def send_log(link_of_postreciever_server, id_mem, id_code, full_name, id_room, room_name):
    req = requests.post(link_of_postreciever_server,
                        data={'key': 'log',
                              'id_mem': id_mem,
                              'id_code': id_code,
                              'full_name': full_name,
                              'id_room': id_room,
                              'room_name': room_name})
    # .strip() = Trimming Whitespaces
    return req.text.strip()


def get_current_permission_name():
    try:
        f = open("permission/name_permission.txt", "r")
        return f.readline().strip()
        f.close()
    except:
        NameError


def get_current_permission_list(room_id_code, id_code):
    try:
        # Opening JSON file
        f = open("permission/" + get_current_permission_name(), )
        data = json.load(f)
        list = []
        for i in data:
            if i["room_id_code"] == str(room_id_code) and id_code == i["id_code"]:
                list.append(i)
        f.close()
        # return list
        return list
    except:
        print("There's no permission list in this machine")


def get_permission_for_this(room_id_code):
    try:
        # Opening JSON file
        f = open("permission/" + get_current_permission_name(), )
        data = json.load(f)
        list = []
        for i in data:
            if i["room_id_code"] == str(room_id_code):
                list.append(i["id_code"])
        f.close()
        # return list
        return list
    except:
        print("There's no permission list in this machine")


def get_all_current_permission_list():
    try:
        # Opening JSON file
        f = open("permission/" + get_current_permission_name(), )
        data = json.load(f)
        list = []
        for i in data:
            list.append(i)
        f.close()
        # return list
        return list
    except:
        print("There's no permission list in this machine")


# check lastest permission on server
def get_latest_permission(link_of_postreciever_server):
    req = requests.post(link_of_postreciever_server, data={'key': 'check_latest_permission'})
    # .strip() = Trimming Whitespaces
    return req.text.strip()


def get_current_model_name():
    try:
        f = open("model/namemodel.txt", "r")
        return f.readline().strip()
        f.close()
    except:
        NameError


# check lastest model
def get_latest_model(link_of_postreciever_server):
    req = requests.post(link_of_postreciever_server, data={'key': 'check_latest_model'})
    # .strip() = Trimming Whitespaces
    return req.text.strip()


# signal to server to compile files
def download_prep(link_of_postreciever_server):
    req = requests.post(link_of_postreciever_server, data={'key': 'zip_files'})
    print(req.text)


def download_file(link_of_file_on_server, destination_for_downloaded_file):
    filename = link_of_file_on_server.rsplit('/', 1)[1]
    completeName = os.path.join(destination_for_downloaded_file, filename)
    with open(completeName, "wb") as f:
        print("\n Downloading %s" % filename)
        response = requests.get(link_of_file_on_server, stream=True)
        total_length = response.headers.get('content-length')

        if total_length is None:  # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int((dl / total_length) * 100)
                sys.stdout.write("\r[%s%s]" % (done, "%"))
                sys.stdout.flush()


def extract_file(zipped_file, destination_for_unzip):
    with zipfile.ZipFile(zipped_file, 'r') as zip_ref:
        zip_ref.extractall(destination_for_unzip)
    zip_ref.close()


def upload_face(files_to_upload, link_of_postreciever_server):
    test_file = {'file': open(files_to_upload, "rb")}
    print("Uploading....")
    test_response = requests.post(link_of_postreciever_server, files=test_file)
    print("Uploaded")
    print(test_response.text)


def upload_model(model_to_upload, link_of_postreciever_server):
    test_file = {'file_model': open(model_to_upload, "rb")}
    print("Uploading....")
    test_response = requests.post(link_of_postreciever_server, files=test_file)
    print("Uploaded")
    print(test_response.text)


def upload_permission(model_to_upload, link_of_postreciever_server):
    test_file = {'file_permission': open(model_to_upload, "rb")}
    print("Uploading....")
    test_response = requests.post(link_of_postreciever_server, files=test_file)
    print("Uploaded")
    print(test_response.text)


def zipdir(dirName, archived_name):
    # ziph is zipfile handle
    ziph = zipfile.ZipFile(archived_name + '.zip', 'w', zipfile.ZIP_DEFLATED)
    # Iterate over all the files in directory
    for folderName, subfolders, filenames in os.walk(dirName):
        for filename in filenames:
            # create complete filepath of file in directory
            filePath = os.path.join(folderName, filename)
            # Add file to zip
            ziph.write(filePath, os.path.join(dirName, basename(filePath)))
    ziph.close()


def export_list():
    now = datetime.now()
    current_time = now.strftime("_%Y_%m_%d_%H_%M_%S")
    arr = os.listdir("datasets/faces/")
    js = 'model/data' + current_time + '.json'
    f = open("model/list.txt", "w")
    f.write('data' + current_time + '.json')
    f.close()
    count = 0
    list = []
    for x in arr:
        text = {"id": count,
                "name": x,
                }
        count += 1
        list.append(text)

    with open(js, 'w') as f:
        json.dump(list, f)

    return js


def get_list_capture(link_of_postreciever_server):
    req = requests.post(link_of_postreciever_server, data={'key': 'list_capture'})
    # .strip() = Trimming Whitespaces
    return json.loads(req.text.strip())


def upload_face_new(link_of_postreciever_server, id_mem, imgBase64, count):
    req = requests.post(link_of_postreciever_server, data={'key': 'uploadface',
                                                           'id_mem': id_mem,
                                                           'imgBase64': imgBase64,
                                                           'count': count})
    print(req.text)


def img_convert(my_image):
    import base64
    with open(my_image, "rb") as img_file:
        my_string = base64.b64encode(img_file.read())
        my_string = my_string.decode('utf-8')
    return my_string


def room_identifier():
    try:
        f = open("room_identifier/name_room_id.txt", "r")
        text = f.readline().strip()
        f.close()
        js = open("room_identifier/"+text)
        data = json.load(js)
        return data
    except:
        NameError


def save_options(locker, unlock, light, buzzer, con_indicator, locker_active, unlock_active, light_active,
                 buzzer_active, con_indicator_active,server_address,room_id_code):
    # Data to be written
    dictionary = {
        "locker": locker,
        "unlock": unlock,
        "light": light,
        "buzzer": buzzer,
        "con_indicator": con_indicator,
        "locker_active": locker_active,
        "unlock_active": unlock_active,
        "light_active": light_active,
        "buzzer_active": buzzer_active,
        "con_indicator_active": con_indicator_active,
        "server_address": server_address,
        "room_id_code": room_id_code
    }

    # Serializing json
    json_object = json.dumps(dictionary, indent=5)

    # Writing to sample.json
    with open("option.json", "w") as outfile:
        outfile.write(json_object)


def read_options():
    with open('option.json', 'r') as openfile:
        # Reading from json file
        json_object = json.load(openfile)
    return json_object


def convert_active():
    options = read_options()
    converted_option = []
    if options["buzzer_active"] == "Active HIGH":
        converted_option.append(True)
    elif options["buzzer_active"] == "Active LOW":
        converted_option.append(False)
    if options["locker_active"] == "Active HIGH":
        converted_option.append(True)
    elif options["locker_active"] == "Active LOW":
        converted_option.append(False)
    if options["light_active"] == "Active HIGH":
        converted_option.append(True)
    elif options["light_active"] == "Active LOW":
        converted_option.append(False)
    if options["unlock_active"] == "Active HIGH":
        converted_option.append(True)
    elif options["unlock_active"] == "Active LOW":
        converted_option.append(False)
    if options["con_indicator_active"] == "Active HIGH":
        converted_option.append(True)
    elif options["con_indicator_active"] == "Active LOW":
        converted_option.append(False)
    return converted_option


# arr = get_list_capture("http://skbright.totddns.com:28006/nsc_backup/raspberrypi_communication/postReceiver.php")
# for x in range(len(arr)):
#    if arr[x]["id_code"] == "1339900662224":
#        print("1339900662224")

# download_file("http://skbright.totddns.com:28006/nsc_backup/raspberrypi_communication/postReceiver.php",os.getcwd())
# print(get_all_current_permission_list())
# print(get_current_permission_list(1,"id_mem"))
# download_prep("http://gonewhich.thddns.net:7071/Upload_Download/postReceiver.php")
# print(send_log("http://localhost/nsc_backup/raspberrypi_communication/postReceiver.php",id_room=1,id_mem=1,full_name="123 123",room_name="living"))
# print(send_log("http://skbright.totddns.com:28006/nsc_backup/raspberrypi_communication/postReceiver.php",id_room=2,id_mem=2,full_name="korawit  kaema",room_name="123"))
# timer()
# r = "88dcUMx6yioCcm70il5w4dANcchov"
# time_out = get_current_room_status_list(room_id_code=r, key="room_dclose")[0]
# current_time = datetime.now().strftime('%H:%M:%S')
# print(current_time)
# print(time_out)
# print(current_time <= time_out)
