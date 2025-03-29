from machine import Pin, UART
import utime
import ujson
import json

class SlavePiPhysical:
    # Hardware PIN
    RTEN_PIN = 11
    FEEDBACK_SW_PIN = 19
    SOLENOID_PIN = 20
    BUZZER_PIN = 21
    
    # RTen mode
    TRANSMIT = 1
    RECEIVE = 0
    
    # Operate State
    CLOSED = 0
    OPEN = 1
    
    # Time variable
    WAIT_FOR_ACK_TIMEOUT_MS = 700
    
    def __init__(self):
        self._assign_locker_id()
        self.setup_sensor_and_physical_output()
        self._setup_communication()
        
    def _assign_locker_id(self):
        try:
            with open('locker_id.txt', 'r') as file:
                self.locker_id = file.readline().strip()
        except OSError as e:
            raise Exception(f"Error reading file locker_id.txt: {e}")
    
    def unlock(self, actor):
        """
        Unlocks the locker:
         - Sets the solenoid to OPEN state.
         - Plays the buzzer for user feedback.
        """
        print(f"Unlock command received from {actor}.")
        self.solenoid.value(self.OPEN)
        self._transmit_data(self._create_framed_log_str('UNLOCK', actor))
        self.play_buzzer(100)  # Activate buzzer for 100ms
        print("Locker unlocked.")
        
    def lock(self, actor):
        print(f"Lock command received from {actor}.")
        self.solenoid.value(self.CLOSED)
        self._transmit_data(self._create_framed_log_str('LOCK', actor))
        self.play_buzzer(100)  # Activate buzzer for 100ms
        print("Locker locked.")
    
    def setup_sensor_and_physical_output(self):
        self.feedbackSW = Pin(self.FEEDBACK_SW_PIN, Pin.IN)        
        self.solenoid = Pin(self.SOLENOID_PIN, Pin.OUT)
        self.buzzer = Pin(self.BUZZER_PIN, Pin.OUT)
        self.SW_feedback_prev_state = None
        self.SW_feedback_current_state = self.feedbackSW.value()
    
    def _setup_communication(self):
        self.RTen_pin = Pin(self.RTEN_PIN, Pin.OUT)
        self.uart = UART(0, baudrate=9600)
        self.RTen_pin.value(self.RECEIVE)
        self.uart.init(9600)
        
    def _transmit_data(self, data):
        """
        Transmits data over UART. The data is expected to be framed by ";;;" at the beginning and end.
        """
        framed_data = ';;;' + data + ';;;'
        self.RTen_pin.value(self.TRANSMIT)
        self.uart.write(framed_data.encode())
        self.uart.flush()
        utime.sleep(1)
        self.RTen_pin.value(self.RECEIVE)
        utime.sleep(0.2)
    
    def _receive_data(self):
        """
        Receives data from UART. If data is available, it is expected to be framed
        by ";;;" at the beginning and end. The method decodes the JSON payload and,
        if the 'assign_to' field matches the local locker ID, processes the command.
        """
        if self.uart.any():
            try:
                data = self.uart.read().decode().strip()
            except Exception as e:
                print("UART read error:", e)
                return
            if data.startswith(';;;') and data.endswith(';;;'):
                # Remove the framing delimiters.
                data = data[3:-3]
                try:
                    json_data = ujson.loads(data)
                    if json_data.get('assign_to') == self.locker_id:
                        self._operate_command(json_data)
                    else:
                        print("Received command not intended for this locker.")
                except Exception as e:
                    print("Error processing received data:", e)

    
    def _operate_command(self, command):
        """
        Checks the action field in the received command.
        Currently, only the 'UNLOCK' action is supported.
        """
        action = command.get('action')
        actor = command.get('actor', 'Unknown')
        if action == "UNLOCK":
            self.unlock(actor)
        else:
            print(f"Unsupported command action received: {action}")
            
    def play_buzzer(self, duration_ms):
        """
        Activates the buzzer for the specified duration (in milliseconds).
        """
        self.buzzer.value(1)  # Turn on the buzzer
        utime.sleep_ms(duration_ms)
        self.buzzer.value(0)  # Turn off the buzzer
        
    def _update_SW_feedback(self):
        self.SW_feedback_prev_state = self.SW_feedback_current_state
        self.SW_feedback_current_state = self.feedbackSW.value()
        if self.SW_feedback_prev_state != self.SW_feedback_current_state:
            if self.SW_feedback_prev_state == self.OPEN and self.SW_feedback_current_state == self.CLOSED:
                self._set_locker_state(self.CLOSED, 'Developper')
                self._record_action('CLOSED', 'Developper')
            else:
                self._record_action('OPEN', 'Developper')
                
    def main_loop(self):
        """
        Main loop for the SlavePi. Continuously checks for incoming commands and updates the feedback switch state.
        """
        while True:
            self._receive_data()
            self._update_SW_feedback()
            utime.sleep(0.1)