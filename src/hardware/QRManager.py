import cv2
import time
import json
import datetime
from cryptography.fernet import Fernet
import base64
import hashlib

class QRManager:
    def __init__(self, key_file):
        self.key = self._read_key(key_file)
        self.cipher = Fernet(self.key)
        self.qrDecoder = cv2.QRCodeDetector()
        self.camera = None
        self.qr_log = None
        self.latest_qr = None
        
    def extract_qr(self, qr_code: str):
        """
        Decrypts and decodes a QR code string.

        :param qr_code: The encrypted QR code as a string.
        :return: The decrypted JSON payload as a dictionary, or None if extraction fails.
        """
        try:
            decrypted_bytes = self.cipher.decrypt(qr_code.encode())
            decrypted_str = decrypted_bytes.decode()
            return json.loads(decrypted_str)
        except Exception as e: 
            print("Error extracting QR data:", e)
            return None
        
    def open(self, qr_code: str):
        """
        Validates and processes the QR code to determine if the locker should be unlocked.
        Ensures the QR code contains the required fields and checks if the current time
        falls within the specified valid time range.

        :param qr_code: The encrypted QR code as a string.
        :return: The decrypted JSON payload if the QR code is valid and within the time range, else None.
        """
        print(qr_code)
        payload = self.extract_qr(qr_code)
        if payload is None:
            print("Failed to extract QR data")
            return None
        else:
            if payload.get('locker_id') is None or payload.get('actor') is None or payload.get('request_id') is None:
                raise ValueError("QR code is missing required fields: 'locker_id', 'actor', or 'request_id'")

        try:
            if "start_date" in payload and "end_date" in payload:
                start_time = datetime.datetime.fromisoformat(payload["start_date"])
                end_time = datetime.datetime.fromisoformat(payload["end_date"])
                now = datetime.datetime.now()
                if start_time <= now <= end_time:
                    return payload
                else:
                    raise ValueError("QR code is not valid within the specified time range")
            else:
                raise ValueError("QR code is missing 'start_time' or 'end_time' fields")
        except ValueError as e:
            print("Error processing payload timestamps:", e)
            raise ValueError("Invalid timestamp format in payload")
        
    
    def process_camera(self):
        if self.camera:
            data = self._read_qr_code()
            print(f"data: {data} \n latest_qr: {self.latest_qr}")
            if data:
                if data == self.latest_qr:
                    print("It same qr as previous frame")
                    return
                self.open(data)
            self._display_camera_feed()
            self.latest_qr = data
            
    def _display_camera_feed(self):
        ret, frame = self.camera.read()
        if ret:
            # Overlay the latest log message on the frame
            cv2.putText(frame, self.qr_log, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow("Camera", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.cleanup()
    
    def _read_key(self, key_file):
        """
        Reads a key from a file, ensures it is properly formatted for Fernet encryption.
        """
        with open(key_file, 'rb') as kf:
            key = kf.read().strip()  # Read the key as bytes

        # Hash the key to ensure it's exactly 32 bytes
        hashed_key = hashlib.sha256(key).digest()[:32]  # No need for .encode()

        # Encode to URL-safe base64
        encoded_key = base64.urlsafe_b64encode(hashed_key)
        return encoded_key
    
            
    def _read_qr_code(self):
        if self.camera is None:
            print("Camera is not activated")
            return None
        ret, frame = self.camera.read()
        if not ret:
            print("Failed to grab frame")
            return None
        data, _, _ = self.qrDecoder.detectAndDecode(frame)
        return data
    
    def _activate_camera(self):
        if self.camera is None:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                print("Cannot open camera")
                self.camera = None
            else:
                print("Camera activated")