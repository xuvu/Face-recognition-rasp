import os
import threading
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox

import cv2
import pandas as pd
from face_recognition import face_encodings
from joblib import dump, load
from sklearn.metrics import classification_report
from sklearn.model_selection import cross_val_predict
from sklearn.svm import SVC

import connect
import file


def center_window(w, h, window):
    # get screen width and height
    ws = window.winfo_screenwidth()  # width of the screen
    hs = window.winfo_screenheight()  # height of the screen

    # calculate x and y coordinates for the Tk root window
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)

    # set the dimensions of the screen
    # and where it is placed
    window.geometry('%dx%d+%d+%d' % (w, h, x, y))


def camera_capture():
    capture = cv2.VideoCapture(0)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    while True:
        ret, frame = capture.read()
        cv2.imshow('face-acquisition', frame)


def run_window():
    def face_cature():
        # Toplevel object which will
        # be treated as a new window
        face_window = tk.Toplevel(master)
        center_window(300, 200, face_window)

        # sets the title of the
        # Toplevel widget
        face_window.title("face_cature Window")

        face_window.resizable(width=False, height=False)

        # A Label widget to show in toplevel
        tk.Label(face_window, text="Enter your ID").pack()
        entry = tk.Entry(face_window)
        entry.pack()

        tk.Label(face_window, text="Enter amount of picture").pack()
        amount_pic = tk.Entry(face_window)
        amount_pic.pack()

        def capture(label, amount):
            OUTPUT_PATH = 'datasets/faces'
            OUTPUT_PATH_TEST = 'datasets/faces_test'
            SIZE = (256, 256)
            MAX_CAPTURE = int(amount)

            detector = cv2.CascadeClassifier('model-haar/haarcascade_frontalface_default.xml')
            font = cv2.FONT_HERSHEY_SIMPLEX
            color = (0, 255, 0)
            output_path = Path(OUTPUT_PATH)
            if not output_path.exists():
                output_path.mkdir()
            output_face_path = Path(OUTPUT_PATH + '/' + label)
            if not output_face_path.exists():
                output_face_path.mkdir()

            count = 0
            capture = cv2.VideoCapture(0)
            # capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            # capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cv2.namedWindow("face-acquisition", cv2.WINDOW_AUTOSIZE)
            cv2.moveWindow("face-acquisition", 20, 20)
            # cv2.namedWindow("face-acquisition", cv2.WND_PROP_FULLSCREEN)
            # cv2.setWindowProperty("face-acquisition", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            time.sleep(2)
            start_time = time.time()
            while count < MAX_CAPTURE:
                ret, frame = capture.read()
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = detector.detectMultiScale(gray, 1.3, 5)
                if len(faces) > 0:
                    for (x, y, w, h) in faces:
                        face = frame[y:y + h, x:x + w]
                        output_name = OUTPUT_PATH + '/' + label + '/img' + str(count) + '.jpg'
                        output_name_test = OUTPUT_PATH_TEST + '/' + label + '/img' + str(count) + '.jpg'
                        face_cropped = frame[y:y + h, x:x + w]
                        face_resized = cv2.resize(face_cropped, SIZE, interpolation=cv2.INTER_LINEAR)
                        if (time.time() - start_time) >= 0.5:
                            start_time = time.time()
                            cv2.imwrite(output_name, face_resized)
                            file.upload_face_new(
                                link_of_postreciever_server=upload_face_api,
                                id_mem=label, imgBase64=file.img_convert(output_name), count=count)
                            count += 1
                        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                        cv2.putText(frame, 'count = ' + str(count) + ' of ' + str(MAX_CAPTURE), (x, y - 10), font, 0.6,
                                    color, thickness=2)

                cv2.imshow('face-acquisition', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            capture.release()
            cv2.destroyAllWindows()

        def get_text():
            id_code = str(entry.get()).strip()
            if id_code != "":
                arr = server.get_list_for_cature()
                cap = False
                for x in range(len(arr)):
                    if arr[x]["id_code"] == str(id_code):
                        id_code = arr[x]["id_mem"]
                        capture(id_code, amount_pic.get())
                        cap = True
                        break
                if not cap:
                    messagebox.showwarning("Warning", "This person's ID isn't a member or already take picture")

        submit_button = tk.Button(face_window, text="Submit", command=get_text)
        cancel_button = tk.Button(face_window, text="Cancel", command=lambda: face_window.destroy())

        submit_button.pack()
        cancel_button.pack()

        face_window.transient(master)
        face_window.grab_set()
        master.wait_window(face_window)

    def train():
        if not os.path.isdir("model"):
            os.mkdir("model")

        class myThread(threading.Thread):
            def __init__(self):
                threading.Thread.__init__(self)

            def run(self):
                HAAR_MODEL = './model-haar/haarcascade_frontalface_default.xml'

                PROCESSED_IMAGE_PATH = './datasets/processed'
                PROCESSED_CSV_FILE = './datasets/processed.csv'
                DETECTED_FACE_PATH = './datasets/cropped'
                DETECTED_CSV_FILE = './datasets/cropped.csv'

                train_csv_file = PROCESSED_CSV_FILE

                # INPUT/OUTPUT PARAMETERS
                INPUT_IMAGE_PATH = './datasets/faces'
                OUTPUT_CSV_FILE = './datasets/faces.csv'
                pathsavefile = './model/'
                namemodel = 'cs-faces-encoding.lib'
                OUTPUT_MODEL_NAME = './model/cs-faces-encoding.lib'

                # EXPERIMENTAL PARAMETERS
                DETECT_FACE = False
                IMAGE_SIZE = 256
                FACE_SIZE = (256, 256)

                def create_csv(dataset_path, output_csv):
                    root_dir = Path(dataset_path)
                    items = root_dir.iterdir()

                    filenames = []
                    labels = []
                    text_box.insert("1.0", "reading image files ... \n")
                    for item in items:
                        if item.is_dir():
                            for file in item.iterdir():
                                if file.is_file():
                                    text_box.insert("1.0", str(file) + "\n")
                                    filenames.append(file)
                                    labels.append(item.name)

                    raw_data = {'filename': filenames, 'label': labels}
                    df = pd.DataFrame(raw_data, columns=['filename', 'label'])
                    df.to_csv(output_csv)
                    text_box.insert("1.0", str(len(filenames)) + "image file(s) read\n")

                def resize(image, width=None, height=None):
                    (h, w) = image.shape[:2]
                    if width is None:
                        r = height / float(h)
                        dim = (int(w * r), height)
                    else:
                        r = width / float(w)
                        dim = (width, int(h * r))
                    return cv2.resize(image, dim, interpolation=cv2.INTER_LINEAR)

                def process_image(input_csv, output_csv, output_path_name):
                    dataset = pd.read_csv(input_csv, sep=',')
                    ids = dataset.values[:, 0]
                    names = dataset.values[:, 1]
                    labels = dataset.values[:, 2]

                    output_path = Path(output_path_name)
                    if not output_path.exists():
                        output_path.mkdir()

                    filenames = []
                    text_box.insert("1.0", "preprocessing images ... \n")
                    for item in names:
                        input_path = Path(item)
                        if input_path.is_file():
                            output_name = output_path_name + '/image' + str(ids[len(filenames)]) + input_path.suffix
                            text_box.insert("1.0", input_path, '->', output_name + "\n")
                            image = cv2.imread(str(input_path))
                            image = resize(image, width=IMAGE_SIZE, height=IMAGE_SIZE)
                            cv2.imwrite(output_name, image)
                            filenames.append(output_name)

                    prc_data = {'filename': filenames, 'label': labels}
                    df = pd.DataFrame(prc_data, columns=['filename', 'label'])
                    df.to_csv(output_csv)
                    text_box.insert("1.0", str(len(filenames)) + "image file(s) processed\n")

                def detect_face(input_csv, output_csv, output_path_name):
                    dataset = pd.read_csv(input_csv, sep=',')
                    ids = dataset.values[:, 0]
                    names = dataset.values[:, 1]
                    labels = dataset.values[:, 2]

                    output_path = Path(output_path_name)
                    if not output_path.exists():
                        output_path.mkdir()

                    clf = cv2.CascadeClassifier(HAAR_MODEL)
                    face_filenames = []
                    face_labels = []
                    count = 0
                    face_count = 0
                    text_box.insert("1.0", "detecting faces ... \n")

                    for item in names:
                        image = cv2.imread(item)
                        face_label = labels[count]

                        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                        faces = clf.detectMultiScale(gray, 1.3, 5)
                        for (x, y, w, h) in faces:
                            cropped = image[y:y + h, x:x + w]
                            output_file = output_path_name + '/face' + str(len(face_filenames)) + '.jpg'
                            cv2.imwrite(output_file, cropped)

                            face_filenames.append(output_file)
                            face_labels.append(face_label)
                        text_box.insert("1.0", str(len(faces)) + "face(s) detected\n")
                        face_count += len(faces)
                        count += 1
                    crp_data = {'filename': face_filenames, 'label': face_labels}
                    df = pd.DataFrame(crp_data, columns=['filename', 'label'])
                    df.to_csv(output_csv)
                    text_box.insert("1.0", str(face_count) + "face(s) detected\n")

                def train_model(train_csv, temppathsavefile, tempnamemodel):
                    dataset = pd.read_csv(train_csv, sep=',')
                    ids = dataset.values[:, 0]
                    names = dataset.values[:, 1]
                    labels = dataset.values[:, 2]
                    new_labels = []
                    images = []
                    text_box.insert("1.0", "Training recognition model ...\n")
                    i = 0
                    for item in names:
                        image = cv2.imread(str(item))
                        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                        encodings = face_encodings(rgb)
                        for encoding in encodings:
                            text_box.insert("1.0", "encoding image: " + str(item) + "\n")
                            images.append(encoding)
                            new_labels.append(labels[i])
                        i = i + 1

                    clf = SVC(kernel='rbf', probability=True)
                    clf.fit(images, new_labels)

                    # name model and update save file model
                    now = datetime.now()
                    current_time = now.strftime("_%Y_%m_%d_%H_%M_%S")
                    file_extension = os.path.splitext(tempnamemodel)
                    tempnamemodel = file_extension[0] + current_time + file_extension[1]
                    output_model_name = pathsavefile + tempnamemodel
                    text_box.insert("1.0", "Model Name : " + str(output_model_name) + "\n")

                    output_model_name = temppathsavefile + tempnamemodel
                    dump(clf, output_model_name)

                    f = open(temppathsavefile + "namemodel.txt", "w")
                    f.write(tempnamemodel)
                    f.close()
                    text_box.insert("1.0", 'Model created in' + str(output_model_name) + "\n")
                    return tempnamemodel, output_model_name

                def validate_model(validate_csv, model_name):
                    dataset = pd.read_csv(validate_csv, sep=',')
                    ids = dataset.values[:, 0]
                    names = dataset.values[:, 1]
                    labels = dataset.values[:, 2]

                    new_labels = []
                    images = []
                    i = 0
                    text_box.insert("1.0", "Validating recognition model ...\n")
                    for item in names:
                        image = cv2.imread(str(item))
                        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                        encodings = face_encodings(rgb)
                        for encoding in encodings:
                            text_box.insert("1.0", "encoding image: " + str(item) + "\n")
                            images.append(encoding)
                            new_labels.append(labels[i])
                        i = i + 1

                    clf = load(model_name)
                    y_p = cross_val_predict(clf, images, new_labels, cv=5)
                    # text_box.insert("1.0", 'Accuracy Score:' + '{0:.4g}'.format(accuracy_score(new_labels, y_p) * 100), '%' "\n")
                    # text_box.insert("1.0", "Confusion Matrix:\n")
                    # text_box.insert("1.0", str(confusion_matrix(new_labels, y_p)) + "\n")
                    # text_box.insert("1.0", "Classification Report:\n")
                    text_box.insert("1.0", str(classification_report(new_labels, y_p)) + "\n")

                # download face from server
                server.download_face_from_server()

                create_csv(INPUT_IMAGE_PATH, OUTPUT_CSV_FILE)
                process_image(OUTPUT_CSV_FILE, PROCESSED_CSV_FILE, PROCESSED_IMAGE_PATH)

                if DETECT_FACE:
                    detect_face(PROCESSED_CSV_FILE, DETECTED_CSV_FILE, DETECTED_FACE_PATH)
                    train_csv_file = DETECTED_CSV_FILE
                namemodel, OUTPUT_MODEL_NAME = train_model(train_csv_file, pathsavefile, namemodel)
                validate_model(train_csv_file, OUTPUT_MODEL_NAME)

                # upload model
                # server.upload_model(OUTPUT_MODEL_NAME)

                # upload json
                # server.upload_model_to_server(file.export_list())

                # upload json
                # server.upload_model_to_server(pathsavefile+"/list.txt")

                # upload namemodel.txt
                # server.upload_model(pathsavefile + "/namemodel.txt")

                server.upload_model()
                text_box.insert("1.0", namemodel + "\n")

                # remove faces folder
                '''
                dir_path = INPUT_IMAGE_PATH
                try:
                    shutil.rmtree(dir_path)
                except OSError as e:
                    print("Error: %s : %s" % (dir_path, e.strerror))
                '''

        # Toplevel object which will
        # be treated as a new window
        train_window = tk.Toplevel(master)
        center_window(500, 400, train_window)

        # sets the title of the
        # Toplevel widget
        train_window.title("train Window")

        train_window.resizable(width=False, height=False)

        # A Label widget to show in toplevel
        text_box = tk.Text(train_window)
        text_box.pack()

        thread1 = myThread()
        thread1.start()

        train_window.transient(master)
        train_window.grab_set()
        master.wait_window(train_window)

    master = tk.Tk()
    master.title("capture and trainer")

    train_button = tk.Button(
        text="Train model",
        bg="blue",
        fg="yellow",
        command=train
    )

    face_button = tk.Button(
        text="Capture face",
        bg="blue",
        fg="yellow",
        command=face_cature
    )

    master.columnconfigure([0, 1], minsize=150)
    master.rowconfigure(0, minsize=200)

    face_button.grid(row=0, column=0)
    train_button.grid(row=0, column=1)

    center_window(300, 200, master)

    # Fixing the master size
    master.resizable(width=False, height=False)

    master.mainloop()


def get_text():
    global post_receiver
    post_receiver = entry.get()
    global upload_face_api
    upload_face_api = str(post_receiver)+"/view/admin/controller/uploadface.php"
    global server
    server = connect.Server_admin(post_receiver)

    if server.connection_status:
        create_txt_file(post_receiver)
        post_form.destroy()
        run_window()
    else:
        messagebox.showwarning("Warning", "Cannot connect to server = " + post_receiver)


def read_txt_file(name="post.txt"):
    if os.path.exists(name):
        f = open(name, "r")
        return f.read()
    else:
        return ""


def create_txt_file(content):
    f = open("post.txt", "w")
    f.write(content)
    f.close()


post_form = tk.Tk()
post_form.title("Post form")
center_window(600, 200, post_form)

# A Label widget to show in toplevel
tk.Label(post_form, text="Enter your destination").pack()
entry = tk.Entry(post_form, width=100)
entry.insert(0, read_txt_file("post.txt"))
entry.pack()

submit_button = tk.Button(post_form, text="Connect to server", command=get_text)
cancel_button = tk.Button(post_form, text="Cancel", command=lambda: post_form.destroy())

submit_button.pack()
cancel_button.pack()

post_form.mainloop()
