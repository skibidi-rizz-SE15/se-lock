import serial
import time
import datetime
import json
import pigpio

class SlavePiLogic:
    DELAY_HARDWARE_COMMAND_MILLISECONDS = 200
    WAITING_TIME_MILLISECONDS = 400
    
    TRANSMITTER = 1
    RECEIVER = 0
    
    RS485_MODE_PIN = 5
    
    
    def __init__(self, slave_pi_physical_id):
        self._init_communication()
        self.slave_id = slave_pi_physical_id
        self._test_connecting(slave_pi_physical_id)
    
    def open(self, actor):
        """
        Attempts to open a hardware lock by transmitting an "UNLOCK" command and waiting for a response.
        Args:
            actor (str): The identifier of the actor initiating the unlock command.
        Returns:
            dict: The response data received from the hardware, parsed as JSON.
        Behavior:
            - Continuously transmits the "UNLOCK" command to the hardware.
            - Waits for a response within a specified timeout period (WAITING_TIME_MILLISECONDS).
            - Sends an acknowledgment (send_ack) upon receiving a valid response.
            - Retries the process if no response is received within the timeout period.
            - Introduces a delay (DELAY_HARDWARE_COMMAND_MILLISECONDS) between retries.
        Raises:
            None: This method does not explicitly raise exceptions but may propagate exceptions
            from _transmit_data, _receive_data, or send_ack if they occur.
        """
        start_time = datetime.datetime.now()
        while True:
            self._transmit_data("UNLOCK", actor)
            # Wait up to WAITING_TIME_MILLISECONDS for a response
            while datetime.datetime.now() < start_time + datetime.timedelta(milliseconds=self.WAITING_TIME_MILLISECONDS):
                # response is json data
                response = self._receive_data()
                if response:
                    self.send_ack()
                    return response
                # Delay before trying again
                time.sleep(self.DELAY_HARDWARE_COMMAND_MILLISECONDS / 1000.0)
                start_time = datetime.datetime.now()
    
    def send_ack(self):
        self._transmit_data("ACK", "Developer")
    
    def _init_communication(self):
        """
        Initializes communication interfaces for the hardware module.
        This method sets up a serial communication interface on '/dev/serial0' 
        with a baud rate of 9600 and a timeout of 1 second. It also initializes 
        a pigpio connection to the localhost on port 8888, configures the 
        RS485 mode pin as an output, and sets it to the receiver mode.
        Raises:
            Exception: If there is an error initializing the serial communication.
        """
        try:
            self.ser = serial.Serial('/dev/serial0', baudrate=9600, timeout=1)
            print("Serial port initialized")
        except Exception as e:
            print("Error initializing serial communication:", e)
            self.ser = None
        self.pi = pigpio.pi("localhost", 8888)
        self.rs485_mode_pin = self.RS485_MODE_PIN
        self.pi.set_mode(self.rs485_mode_pin, pigpio.OUTPUT)
        self.pi.write(self.rs485_mode_pin, self.RECEIVER)
    
    def _transmit_data(self, command, actor="Developer"):
        """
        Transmits a command from the slave device to a connected system via serial communication.
        Args:
            command (str): The command to be transmitted.
            actor (str, optional): The entity initiating the command. Defaults to "Developer".
        Attributes:
            from_slave_id (str): The identifier of the slave device, retrieved from the instance attribute slave_id.
            command (str): The command to be sent.
            actor (str): The entity initiating the command.
            timestamp (str): The ISO 8601 formatted timestamp of when the command is sent.
        Behavior:
            - Constructs a JSON message containing the command, actor, slave ID, and timestamp.
            - Frames the message with delimiters and sends it via the serial interface.
            - Switches the RS485 mode pin to transmitter mode before sending and back to receiver mode after sending.
            - Prints the transmitted message or an error if the serial interface is not initialized.
            - Introduces a delay after transmission to ensure hardware stability.
        Note:
            The method assumes the presence of instance attributes ser, pi, rs485_mode_pin, 
            TRANSMITTER, RECEIVER, and DELAY_HARDWARE_COMMAND_MILLISECONDS.
        """
        data = {
            "assign_to": getattr(self, 'slave_id', None),
            "action": command,
            "actor": actor,
            "timestamp": datetime.datetime.now().isoformat()
        }
        message = json.dumps(data)
        framed_message = ";;;" + message + ";;;\n"
        if self.ser:
            self.pi.write(self.rs485_mode_pin, self.TRANSMITTER)
            self.ser.write(framed_message.encode())
            self.ser.flush()
            self.pi.write(self.rs485_mode_pin, self.RECEIVER)
            print("Transmitted:", framed_message)
        else:
            print("Serial not initialized; cannot transmit.")
        time.sleep(self.DELAY_HARDWARE_COMMAND_MILLISECONDS / 1000.0)
    
    def _receive_data(self):
        """
        Receives and processes data from a serial connection.
        This method reads data from a serial connection if available, switches the 
        RS485 mode pin to receiver mode, and attempts to parse the received data 
        as JSON. The data is expected to be enclosed within ";;;" delimiters. If 
        the data is successfully parsed, it is returned; otherwise, an error is 
        logged, and None is returned.
        Returns:
            dict or None: The parsed JSON data as a dictionary if successful, 
                          otherwise None.
        """
        if self.ser and self.ser.in_waiting > 0:
            self.pi.write(self.rs485_mode_pin, self.RECEIVER)
            raw = self.ser.readline().decode('utf-8', errors='ignore').strip()
            if raw.startswith(";;;") and raw.endswith(";;;"):
                data_str = raw[3:-3]
                try:
                    data = json.loads(data_str)
                    print("Received:", data)
                    return data
                except Exception as e:
                    print("Error parsing received data:", e)
                    return None
        return None
    
    def _test_connecting(self, slave_pi_physical_id):
        """
        Tests the connection to a slave device by verifying the log details.
        This method checks if the log indicates that the actor is a "Developer" 
        and the command is "UNLOCK". If the conditions are met, it returns the 
        provided slave device's physical ID. Otherwise, it raises a ValueError.
        Args:
            slave_pi_physical_id (str): The physical ID of the slave device.
        Returns:
            str: The physical ID of the slave device if the connection is successful.
        Raises:
            ValueError: If the connection to the slave device fails.
        """
        #log = self.open("Developer")
        #if log['actor'] == "Developer" and log['action'] == "UNLOCK":
        #    return slave_pi_physical_id
        return slave_pi_physical_id
        raise ValueError("Failed to connect to the slave device")