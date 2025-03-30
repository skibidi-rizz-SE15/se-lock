import cv2
import serial
import time
import json
import datetime
import requests
from cryptography.fernet import Fernet
import RPi.GPIO as GPIO
import base64
import pigpio

class Pi4LockerSystem:
    TRANSMITTER = 1
    RECEIVER = 0

    def __init__(self, serial_port, baud_rate, api_endpoint, key_file, button_pin, rs485_mode_pin):
        self.serial_port = serial_port
        self.baud_rate = baud_rate  
        self.api_endpoint = api_endpoint
        self.key = self.read_key(key_file)
        self.cipher = Fernet(self.key)
        self.serial_port = serial_port
        self.ser = self.initialize_serial(self.serial_port, baud_rate)
       
        # Setup RS485 mode control pin
        self.pi = pigpio.pi("localhost", 8888)
        if not self.pi.connected:
            raise Exception("Unable to connect to pigpio daemon. Did you run 'sudo pigpiod'?")
        self.rs485_mode_pin = rs485_mode_pin
        self.pi.set_mode(self.rs485_mode_pin, pigpio.OUTPUT)
        self.pi.write(self.rs485_mode_pin, self.RECEIVER)  
       
        self.cap = None  # Camera will be initialized when button is pressed
        self.qrDecoder = cv2.QRCodeDetector()
        self.button_pin = button_pin
        #self.setup_button()
        #self.activate_camera()
       
        # New attribute to store the latest log message
        self.latest_log = "No logs yet"
       
        print("setup complete")

    # ----- Initialization Methods -----
    def read_key(self, key_file):
        print(f"Opening key file: {key_file}")
        with open(key_file, 'rb') as kf:
            key = kf.read().strip()  # Remove any extra spaces or newlines
        print(f"Raw key: {key}")
        missing_padding = len(key) % 4
        if missing_padding:
            key += b'=' * (4 - missing_padding)
        print("Padding applied if needed")
        try:
            key = base64.urlsafe_b64decode(key)
            key = base64.urlsafe_b64encode(key)
        except Exception as e:
            print("Error decoding key:", e)
            raise ValueError("Invalid key format")
        return key

    def initialize_serial(self, port, baud_rate):
        print(f"Initializing serial port: {port} with baud rate {baud_rate}")
        try:
            ser = serial.Serial(port, baudrate=baud_rate, timeout=1)
            print("Opened serial port successfully")
            return ser
        except Exception as e:
            print("Error opening serial port:", e)
            return None

    def setup_button(self):
        GPIO.setup(self.button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.button_pin, GPIO.FALLING, callback=self.activate_camera, bouncetime=300)

    def activate_camera(self, channel=None):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)  # Adjust camera index if necessary
            if not self.cap.isOpened():
                print("Cannot open camera")
                self.cap = None
            else:
                print("Camera activated")

    # ----- Logging Methods -----
    def check_internet(self):
        try:
            requests.get("http://www.google.com", timeout=5)
            return True
        except requests.ConnectionError:
            return False

    def log_to_server(self, data):
        try:
            response = requests.post(self.api_endpoint, json=data)
            response.raise_for_status()
            print("Data logged to server successfully")
            return True
        except requests.RequestException as e:
            print(f"Failed to log data to server: {e}")
            return False
       
    def send_ack(self, receiver, actor="Developper"):
        data = {
            "action": "ACK",
            "assign_to": receiver,
            "actor": actor
        }
        self.transmit_data(json.dumps(data))

    def log_locally(self, data, receiver="No one"):
        with open("local_log.txt", "a") as log_file:
            log_file.write(json.dumps(data) + "\n")
        print("Data logged locally:", data)
        # Update the latest log message to show on the display
        self.latest_log = f"Local log: {data}"

    def process_logs(self):
        pass
        #if self.check_internet():
        #    try:
        #        with open("local_log.txt", "r") as log_file:
        #            logs = log_file.readlines()
        #        with open("local_log.txt", "w") as log_file:
        #            for log in logs:
        #                data = json.loads(log.strip())
        #                if not self.log_to_server(data):
        #                    log_file.write(log)
        #    except FileNotFoundError:
        #        print("Local log file not found")

    def receive_data(self):
        # Read data and remove framing delimiters (assumed to be ";;;")
        if self.ser.in_waiting > 0:
            print(f"Bytes available: {self.ser.in_waiting}")
            raw = self.ser.readline().decode('utf-8', errors='ignore').strip()
            print(f"Raw data received: {raw}")
            if raw.startswith(';;;') and raw.endswith(';;;'):
                data_str = raw[3:-3]
                return data_str
        return None

    def receive_log_from_pi0(self):
        try:
            data_str = self.receive_data()
            if data_str:
                log_data = json.loads(data_str)
                print(f"Decoded log: {log_data}")
                # Update the latest log message
                self.latest_log = f"Pi0 log: {log_data}"
                self.log_locally(log_data, log_data["from_locker_id"])
                self.ser.reset_input_buffer()
                self.send_ack(log_data["from_locker_id"])
        except (json.JSONDecodeError, OSError, serial.SerialException) as e:
            try:
                self.ser.close()
            except Exception:
                pass
            time.sleep(1)
            self.ser = self.initialize_serial(self.serial_port, 9600)
            return None

    # ----- QR Code Methods -----
    def extract_qr_data(self, qr_code):
        try:
            decrypted_bytes = self.cipher.decrypt(qr_code.encode())
            decrypted_str = decrypted_bytes.decode()
            return json.loads(decrypted_str)
        except Exception as e:
            print("Error extracting QR data:", e)
            return None

    def read_qr_code(self):
        if self.cap is None:
            print("Camera is not activated")
            return None
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to grab frame")
            return None
        data, _, _ = self.qrDecoder.detectAndDecode(frame)
        return data

    # ----- Locker Control Methods -----
    def open_locker(self, locker_id, actor="Developper"):
        data = {
            "actor": actor,
            "action": "UNLOCK",
            "assign_to": locker_id,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.transmit_data(json.dumps(data))
        if self.check_internet():
            if not self.log_to_server(data):
                self.log_locally(data)
        else:
            self.log_locally(data)
       
       
    def lock_locker(self, locker_id, actor="Developper"):
        data = {
            "actor": actor,
            "action": "LOCK",
            "assign_to": locker_id,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.transmit_data(json.dumps(data))
        if self.check_internet():
            if not self.log_to_server(data):
                self.log_locally(data)
        else:
            self.log_locally(data)
       

    def assign_item_to_locker(self, locker_id, item_id):
        data = {
            "locker_id": locker_id,
            "item_id": item_id
        }
        return self.log_to_server(data)

    def clear_transaction_in_item(self, item_id):
        data = {
            "item_id": item_id
        }
        return self.log_to_server(data)

    # ----- RS485 Transmit Method -----
    def transmit_data(self, data):
        message = ";;;" + data + ";;;\n"
        # Set RS485 to transmit mode
        print("ALREAD CHANGE TO TRANSMITTER")
        self.pi.write(self.rs485_mode_pin, self.TRANSMITTER)
        self.ser.write(message.encode())
        self.ser.flush()
        time.sleep(0.5)
        # Set RS485 back to receive mode
        self.pi.write(self.rs485_mode_pin, self.RECEIVER)
        print("Switch back to RECEIVER mode")
        time.sleep(0.2)

    # ----- Main Loop and QR Handling -----
    def main_loop(self):
        print("Starting main loop...")
        while True:
            self.receive_log_from_pi0()
            self.process_camera()
            self.process_logs()
           

    def process_camera(self):
        if self.cap:
            data = self.read_qr_code()
            if data:
                self.handle_qr_code(data)
            #self.display_camera_feed()

    def handle_qr_code(self, data):
        print("QR Code detected:", data)
        try:
            decrypted_bytes = self.cipher.decrypt(data.encode())
            decrypted_str = decrypted_bytes.decode()
            payload = json.loads(decrypted_str)
            print("Decrypted JSON:", payload)
            command = self.determine_command(payload)
            self.transmit_data(command)
            self.log_action(payload, command)
        except Exception as e:
            print("Error processing QR code:", e)

    def determine_command(self, payload):
        if "start_time" in payload and "end_time" in payload:
            start_time = datetime.datetime.fromisoformat(payload["start_time"])
            end_time = datetime.datetime.fromisoformat(payload["end_time"])
            now = datetime.datetime.now()
            if start_time <= now <= end_time:
                return "unlock"
            else:
                return "lock"
        else:
            return "unlock"

    def log_action(self, payload, command):
        log_data = {
            "username": payload.get("username"),
            "locker_id": payload.get("locker_id"),
            "action": command,
            "timestamp": datetime.datetime.now().isoformat()
        }
        if self.check_internet():
            if not self.log_to_server(log_data):
                self.log_locally(log_data)
        else:
            self.log_locally(log_data)

    def display_camera_feed(self):
        ret, frame = self.cap.read()
        if ret:
            # Overlay the latest log message on the frame
            cv2.putText(frame, self.latest_log, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow("Camera", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.cleanup()

    def cleanup(self):
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.ser.close()
        GPIO.cleanup()
        exit()