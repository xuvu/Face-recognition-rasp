from datetime import datetime
import threading
import time

import cv2
import face_recognition
import numpy as np
from joblib import load

import connect
import file
import tkinter as tk

import components


class test:
    # setup data from current data on this machine
    def setup_data(self):

        # load existed permission
        self.permission_list = file.get_permission_for_this(self.room_id_code)

        # load existed room status
        all_room_status = file.get_this_room_status(self.room_id_code)
        self.room_status["close_time"] = all_room_status["room_dclose"]
        self.room_status["open_time"] = all_room_status["room_open"]
        self.room_status["electric_status"] = all_room_status["room_fstatus"]
        self.room_status["door_status"] = all_room_status["status_door"]

        self.hold_door_status = self.get_current_door_status()  # convert from "1/0" to boolean

        # load existed model
        HAAR_MODEL = './model-haar/haarcascade_frontalface_default.xml'
        SVM_MODEL = "model/" + str(file.get_current_model_name())
        self.detector = cv2.CascadeClassifier(HAAR_MODEL)
        self.classifier = load(SVM_MODEL)

    # update all data
    def update_all(self):
        if self.server.connection_status:
            if self.server.check_update_model():
                self.server.update_model()
                SVM_MODEL = "model/" + str(file.get_current_model_name())
                self.classifier = load(SVM_MODEL)
            if self.server.check_update_permission():
                self.server.update_permission()
                self.permission_list = file.get_permission_for_this(self.room_id_code)
            if self.server.check_update_room_status():
                self.server.update_room_status()

                all_room_status = file.get_this_room_status(self.room_id_code)
                self.room_status["close_time"] = all_room_status["room_dclose"]
                self.room_status["open_time"] = all_room_status["room_open"]
                self.room_status["electric_status"] = all_room_status["room_fstatus"]
                self.room_status["door_status"] = all_room_status["status_door"]

                self.hold_door_status = self.get_current_door_status()  # convert from "1/0" to boolean

    # convert current room's door status
    def get_current_door_status(self):
        if self.room_status["door_status"] == "1":
            return True
        else:
            return False

    def get_pins(self):
        print(self.buzzer_pin)
        print(self.locker_pin)
        print(self.light_pin)
        print(self.open_pin)
        print(self.connection_indicator_pin)

    def setupins(self):
        options = file.read_options()
        active_options = file.convert_active()
        if options["buzzer"] != "":
            self.buzzer_pin.set_pin(int(options["buzzer"]))
            self.buzzer_pin.enable()
            self.buzzer_pin.set_active(active_options[0])
            self.buzzer_pin.off()

        if options["locker"] != "":
            self.locker_pin.set_pin(int(options["locker"]))
            self.locker_pin.enable()
            self.locker_pin.set_active(active_options[1])
            self.locker_pin.off()

        if options["light"] != "":
            self.light_pin.set_pin(int(options["light"]))
            self.light_pin.enable()
            self.light_pin.set_active(active_options[2])
            self.light_pin.off()

        if options["unlock"] != "":
            self.open_pin.set_pin(int(options["unlock"]))
            self.open_pin.set_active(active_options[3])
            self.open_pin.enable()

        if options["con_indicator"] != "":
            self.connection_indicator_pin.set_pin(int(options["con_indicator"]))
            self.connection_indicator_pin.enable()
            self.connection_indicator_pin.set_active(active_options[4])
            self.connection_indicator_pin.off()

    def __init__(self, post, room_id_code):

        self.buzzer_pin = components.control_components.output_pin("disable")
        self.locker_pin = components.control_components.output_pin("disable")
        self.light_pin = components.control_components.output_pin("disable")
        self.open_pin = components.control_components.input_pin("disable")
        self.connection_indicator_pin = components.control_components.output_pin("disable")
        self.ultrasonic = components.control_components.ultrasonic()

        self.server = connect.Server(str(post), str(room_id_code))

        self.post = post
        self.room_id_code = room_id_code

        # detected face from face recognition
        self.detected_face = None

        # variable for room's status
        self.room_status = {"electric_status": " ", "door_status": " ", "open_time": " ", "close_time": ""}

        self.update_all()
        self.setup_data()

        self.room_name = file.get_this_room_status(room_id_code)["room_num"]

        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.WND_PROP_FULLSCREEN, 640)
        self.capture.set(cv2.WND_PROP_FULLSCREEN, 480)

        self.image = 0
        self.rgb = 0
        self.faces = 0
        self.gray = 0
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0

        self.green = (0, 255, 0)
        self.red = (0, 0, 255)
        self.color_face = 0
        self.color_door = self.red
        self.threshold = 0.65
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.text = ""
        self.door_text = "Close"

        # self.video_capture()

        # สถานะเปิดปิดประตู
        # self.statusdoor = True
        # จำนวนครั้งที่ตรวจจับได้ถูกต้องต่อเนื่อง
        self.maxcountdetected = 2

        # นับจำนวนที่ตรวจจับได้ถูกต้อง
        self.countdetected = 0

        # ค่าเฉลี่ยความแม่นยำตรวจจับถูกต้องต่อเนื่อง
        self.avgacc = 0

        # ชื่อผู้ถูกตรวจจับได้
        self.namedetected = ""

        # ระยะเซ็นเซอร์ที่ตรวจจับได้
        self.dis = 75

        # สถานะเซ็นเซอร์ตรวจจับ
        self.statusdetecting = False

        self.kill_thread = False

    def check_time(self, open_time, close_time, current_time):
        if open_time > close_time:
            if open_time <= current_time:
                return True
            else:
                return False
        elif open_time < close_time:
            if open_time <= current_time < close_time:
                return True
            else:
                return False

    def control_electric(self):
        current_time = datetime.now().strftime('%H:%M:%S')
        if self.room_status["electric_status"] == "1":
            # code for always turn on electric

            print("always turn on electric")

            # end of code

        elif self.room_status["electric_status"] == "0":
            # code for always turn off electric:

            print("always turn off electric")

            # end of code

        # control by time
        elif self.room_status["electric_status"] == "2" and self.check_time(self.room_status["open_time"],
                                                                            self.room_status["close_time"],
                                                                            current_time):
            # code for turn on electric is here

            print("Auto mode turn on electric")

            # end of code

        else:
            # code for turn off electric is here

            print("Auto mode turn off electric")

            # end of code

    # function for turn on buzzer for a specific time
    def open_buzzer(self, seconds):
        print("Buzzer on")

        # code for buzzer makes sound is down here **************************

        self.buzzer_pin.on()

        # end of code *******************************************************

        time.sleep(seconds)

        # code for turn off buzzer is down here ****************************

        self.buzzer_pin.off()
        # end of code ******************************************************

        print("Buzzer off")

    # function for open door
    def open_door(self, seconds):

        # open for a specific time
        if seconds > 0:
            self.door_text = "Open"
            self.color_door = self.green
            self.hold_door_status = True  # keep the door open

            # code for opening door is down here ***********************************

            self.locker_pin.on()

            # end of code **********************************************************

            time.sleep(seconds)

            # code for closing door is down here ***********************************

            self.locker_pin.off()

            # end of code **********************************************************

            self.door_text = "Close"
            self.color_door = self.red
            self.hold_door_status = False  # keep the door close

        # always open
        elif seconds == 0:
            self.door_text = "Open"
            self.color_door = self.green
            # self.statusdoor = False

            # code for continuity open door is down here **************************

            self.locker_pin.on()

            # end of code **********************************************************

        # always close
        elif seconds == -1:
            self.door_text = "Close"
            self.color_door = self.red
            # self.statusdoor = True

            # code for continuity close door is down here **************************

            self.locker_pin.off()

            # end of code **********************************************************

    def ultrasonic_run(self):
        if self.ultrasonic.distanceultra() <= self.dis and not self.hold_door_status:
            self.statusdetecting = True
            self.light_pin.on()
        else:
            self.statusdetecting = False
            self.light_pin.off()

    def camera_check(self):
        if not self.capture.isOpened():
            print("Cannot open camera")
            exit()

    # function for capture images from camera
    def video_capture(self):
        ret, frame = self.capture.read()
        self.image = frame.copy()

        self.drawing()

        cv2.imshow('face classifier', self.image)

    # function for drawing text and rectangle on cv screen
    def drawing(self):
        if self.statusdetecting and not self.hold_door_status:
            cv2.putText(self.image, self.text, (self.x, self.y - 10), self.font, 0.6, self.color_face, thickness=2)
            cv2.rectangle(self.image, (self.x, self.y), (self.x + self.w, self.y + self.h), self.color_face, 2)

        cv2.putText(self.image, "Door:" + self.door_text, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, self.color_door,
                    lineType=cv2.LINE_AA)
        self.image = cv2.putText(self.image, self.room_name, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5,
                                 self.green, lineType=cv2.LINE_AA)

    # function for encoding and classification
    def encode_cnn_svm(self):
        if not self.hold_door_status and self.statusdetecting:  # check if door is opened and ultrasonic detected object
            gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            self.rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            self.faces = self.detector.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in self.faces:
                self.x = x
                self.y = y
                self.w = w
                self.h = h
                testset = []
                boxes = [(y, x + w, y + h, x)]
                encodings = face_recognition.face_encodings(self.rgb, boxes)

                if len(encodings) > 0:
                    testset.append(np.ravel(encodings[0]))
                    pred = self.classifier.predict(testset)
                    prob = self.classifier.predict_proba(testset)
                    max_prob = max(prob[0])
                    self.color_face = self.red
                    self.text = "Unknown"
                    if max_prob >= self.threshold:
                        self.color_face = self.green
                        self.text = ''.join(pred[0] + ' (' + '{0:.2g}'.format(max_prob * 100) + '%)')

                        if pred[0] in self.permission_list:
                            self.countdetected = self.countdetected + 1
                            self.avgacc = self.avgacc + (max_prob * 100)  # รวมค่าเฉลี่ยความแม่นยำ

                            if self.maxcountdetected <= self.countdetected:
                                self.detected_face = pred[0]
                                self.avgacc = self.avgacc / self.countdetected  # คำนวณค่าเฉลี่ยการตรวจจับหน้าถูกต้อง
                                self.namedetected = ''.join(pred[0] + ' (' + '{0:.2g}'.format(self.avgacc) + '%)')

                                # code after the permitted face is detected **************************

                                # send log to server
                                self.server.send_log_to_server(pred[0])

                                # call for open door and turn on buzzer
                                t_door = self.thread_door(5)
                                t_buzz = self.thread_buzzer(5)

                                t_door.start()
                                t_buzz.start()

                                t_buzz.join()
                                t_door.join()

                                self.countdetected = 0  # เซตค่าการนับการตรวจจับถูกต้องใหม่
                                self.avgacc = 0  # เซตค่าเฉลี่ยความแม่นยำใหม่

                                # end of code **********************************************************

    # thread for capture image from camera
    class thread_capture(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)

        def run(self):
            while True:
                time.sleep(0.1)
                test.video_capture()
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    test.kill_thread = True
                    components.clear()
                    break
            test.capture.release()
            cv2.destroyAllWindows()

    # thread for encoding and classification
    class thread_encode(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)

        def run(self):
            while True:
                time.sleep(0.1)
                test.encode_cnn_svm()
                if test.kill_thread:  # kill this thread
                    break

    # thread for checking update data from server
    # and logging
    class thread_update(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)

        def run(self):
            while True:
                test.server.is_connect()
                time.sleep(5)
                test.update_all()
                test.server.send_offline_log()
                if test.kill_thread:  # kill this thread
                    break

    # thread for open_door
    class thread_door(threading.Thread):
        def __init__(self, sec):
            threading.Thread.__init__(self)
            self.sec = sec

        def run(self):
            test.open_door(self.sec)
            # code after the door is opened is down here **************************

            # end of code *********************************************************

    # thread for open_buzzer
    class thread_buzzer(threading.Thread):
        def __init__(self, sec):
            threading.Thread.__init__(self)
            self.sec = sec

        def run(self):
            test.open_buzzer(self.sec)
            # code after the buzzer makes sound is down here *************************

            # end of code ************************************************************

    # thread for always open/close door
    class thread_control_components(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)

        def run(self):
            while True:
                time.sleep(1)
                test.control_electric()  # check for electric conditions
                test.ultrasonic_run()  # update distance from ultrasonic

                if test.hold_door_status:  # keep door open
                    test.open_door(0)
                elif not test.hold_door_status:  # keep door close
                    test.open_door(-1)

                if test.server.connection_status:  # LED connection status
                    test.connection_indicator_pin.on()
                else:
                    test.connection_indicator_pin.off()

                if test.open_pin.get_value():  # open from button
                    t_door = test.thread_door(5)
                    t_buzz = test.thread_buzzer(5)

                    t_door.start()
                    t_buzz.start()

                    t_buzz.join()
                    t_door.join()

                if test.kill_thread:  # kill this thread
                    break

    def run(self):

        self.setupins()

        t1 = self.thread_capture()
        t2 = self.thread_encode()
        t3 = self.thread_update()
        t4 = self.thread_control_components()

        t1.start()
        time.sleep(2)
        t2.start()
        t3.start()
        t4.start()


class OptionForm:
    options = file.read_options()
    active_list = {"locker_active": options["locker_active"],
                   "unlock_active": options["unlock_active"],
                   "light_active": options["light_active"],
                   "buzzer_active": options["buzzer_active"],
                   "con_indicator_active": options["con_indicator_active"]}
    submit = False

    def __init__(self):
        self.pin_list = None
        self.options = file.read_options()

    def start(self):

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

        pin_form = tk.Tk()
        pin_form.title("Post form")
        center_window(750, 400, pin_form)
        tk.Label(pin_form, text="Functional pins").grid(row=0, column=1)
        tk.Label(pin_form, text="Locker pin").grid(row=1, column=0)
        tk.Label(pin_form, text="Unlock door pin").grid(row=2, column=0)

        locker = tk.Entry(pin_form, width=10)
        locker.insert(0, self.options["locker"])
        locker.grid(row=1, column=1)

        unlock = tk.Entry(pin_form, width=10)
        unlock.insert(0, self.options["unlock"])
        unlock.grid(row=2, column=1)

        def active_menu_locker(x):
            OptionForm.active_list["locker_active"] = x

        active_locker = tk.StringVar(pin_form)
        active_locker.set(self.options["locker_active"])  # default value

        active_locker_button = tk.OptionMenu(pin_form, active_locker, "Active HIGH", "Active LOW",
                                             command=active_menu_locker)
        active_locker_button.grid(row=1, column=2)

        def active_menu_unlock(x):
            OptionForm.active_list["unlock_active"] = x

        active_unlock = tk.StringVar(pin_form)
        active_unlock.set(self.options["unlock_active"])  # default value

        active_unlock_button = tk.OptionMenu(pin_form, active_unlock, "Active HIGH", "Active LOW",
                                             command=active_menu_unlock)
        active_unlock_button.grid(row=2, column=2)

        tk.Label(pin_form, text="Ultrasonic pin").grid(row=3, column=0)
        tk.Label(pin_form, text="USB camera").grid(row=4, column=0)

        tk.Label(pin_form, text="trigger pin = 18, echo pin = 24").grid(row=3, column=1)
        tk.Label(pin_form, text="USB").grid(row=4, column=1)

        tk.Label(pin_form, text="******************************************").grid(row=5, column=1)

        tk.Label(pin_form, text="Non-Functional pin").grid(row=6, column=1)
        tk.Label(pin_form, text="Connection indicator pin").grid(row=7, column=0)
        tk.Label(pin_form, text="Light pin").grid(row=8, column=0)
        tk.Label(pin_form, text="Buzzer pin").grid(row=9, column=0)

        con_indicator = tk.Entry(pin_form, width=10)
        con_indicator.insert(0, self.options["con_indicator"])
        con_indicator.grid(row=7, column=1)

        light = tk.Entry(pin_form, width=10)
        light.insert(0, self.options["light"])
        light.grid(row=8, column=1)

        buzzer = tk.Entry(pin_form, width=10)
        buzzer.insert(0, self.options["buzzer"])
        buzzer.grid(row=9, column=1)

        variable = tk.StringVar(pin_form)
        variable.set("ON")  # default value

        variable2 = tk.StringVar(pin_form)
        variable2.set("ON")  # default value

        variable3 = tk.StringVar(pin_form)
        variable3.set("ON")  # default value

        def check_menu(x):
            if x == "OFF":
                con_indicator.delete(0, 'end')
                con_indicator.config(state="disabled")
            else:
                con_indicator.config(state="normal")

        def check_menu2(x):
            if x == "OFF":
                light.delete(0, 'end')
                light.config(state="disabled")
            else:
                light.config(state="normal")

        def check_menu3(x):
            if x == "OFF":
                buzzer.delete(0, 'end')
                buzzer.config(state="disabled")
            else:
                buzzer.config(state="normal")

        con_indicator_status = tk.OptionMenu(pin_form, variable, "ON", "OFF", command=check_menu)
        con_indicator_status.grid(row=7, column=2)
        light_status = tk.OptionMenu(pin_form, variable2, "ON", "OFF", command=check_menu2)
        light_status.grid(row=8, column=2)
        buzzer_status = tk.OptionMenu(pin_form, variable3, "ON", "OFF", command=check_menu3)
        buzzer_status.grid(row=9, column=2)

        def active_menu_con(x):
            OptionForm.active_list["con_indicator_active"] = x

        active_con = tk.StringVar(pin_form)
        active_con.set(self.options["con_indicator_active"])  # default value
        active_con_button = tk.OptionMenu(pin_form, active_con, "Active HIGH", "Active LOW", command=active_menu_con)
        active_con_button.grid(row=7, column=3)

        def active_menu_light(x):
            OptionForm.active_list["light_active"] = x

        active_light = tk.StringVar(pin_form)
        active_light.set(self.options["light_active"])  # default value
        active_light_button = tk.OptionMenu(pin_form, active_light, "Active HIGH", "Active LOW",
                                            command=active_menu_light)
        active_light_button.grid(row=8, column=3)

        def active_menu_buzzer(x):
            OptionForm.active_list["buzzer_active"] = x

        active_buzzer = tk.StringVar(pin_form)
        active_buzzer.set(self.options["buzzer_active"])  # default value
        active_buzzer_button = tk.OptionMenu(pin_form, active_buzzer, "Active HIGH", "Active LOW",
                                             command=active_menu_buzzer)
        active_buzzer_button.grid(row=9, column=3)

        def get_value():
            OptionForm.pin_list = {"locker": locker.get(), "con_indicator": con_indicator.get(),
                                   "unlock": unlock.get(), "light": light.get(), "buzzer": buzzer.get()}

            # get options pin from form
            if locker.get() != "" and unlock.get():
                file.save_options(locker.get(), unlock.get(), light.get(), buzzer.get(), con_indicator.get(),
                                  OptionForm.active_list["locker_active"],
                                  OptionForm.active_list["unlock_active"],
                                  OptionForm.active_list["light_active"],
                                  OptionForm.active_list["buzzer_active"],
                                  OptionForm.active_list["con_indicator_active"],
                                  server_ad.get(),
                                  room_identifier.get())
                OptionForm.submit = True
                pin_form.destroy()

        tk.Label(pin_form, text="******************************************").grid(row=10, column=1)
        tk.Label(pin_form, text="Destination").grid(row=11, column=0)

        server_ad = tk.Entry(pin_form)
        server_ad.insert('end', self.options["server_address"])
        server_ad.grid(row=11, column=1, sticky='ew', columnspan=4)

        tk.Label(pin_form, text="Room identifier").grid(row=12, column=0)
        room_identifier = tk.Entry(pin_form)
        room_identifier.insert('end', self.options["room_id_code"])
        room_identifier.grid(row=12, column=1, sticky='ew', columnspan=4)

        btn = tk.Button(pin_form, text="Run raspberry pi", command=get_value).grid(row=13, column=0)

        pin_form.mainloop()


op = OptionForm()
op.start()

if OptionForm.submit:
    options = file.read_options()
    test = test(options["server_address"], options["room_id_code"])
    test.run()
