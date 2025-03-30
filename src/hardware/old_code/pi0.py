from machine import Pin, UART
import utime
import ujson
import json

class LockerTransactionState:
    FREE = 1
    ASSIGN = 2
    PICK_UP = 3
    BORROWED = 4
    RETURNED = 5

class Locker:
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
        self._setup_log_queue()
        self._setup_command_queue()
        self._setup_operation_and_transaction()
        self._setup_sensor_and_physical_output()
        self._setup_communication()
        
    #--------------------------------------------------------------------#
    # setup and end function
        
    def _assign_locker_id(self):
        try:
            with open('locker_id.txt', 'r') as file:
                self.locker_id = file.readline().strip()
        except OSError as e:
            raise Exception(f"Error reading file locker_id.txt: {e}")
        
    def _setup_command_queue(self):
        self.command_queue = []
        
    def _setup_log_queue(self):
        self.log_queue = []
        try:
            with open('log.txt', 'r') as file:
                lines = file.readlines()
                for log in lines:
                    if log == "":
                        continue
                    self.log_queue.append(log.strip())
        except OSError as e:
            raise Exception(f"Error reading file log.txt: {e}")
        
    def _dump_queue_to_log_file(self):
        try:
            with open('log.txt', 'w') as file:
                for log in self.log_queue:
                    if log == "":
                        continue
                    file.write(str(log).strip() + "\n")
        except OSError as e:
            raise Exception(f"Error writing to log.txt: {e}")
        
    def _setup_operation_and_transaction(self):
        self._status = self.CLOSED
        self._state: LockerTransactionState = LockerTransactionState.FREE
        self.transaction_id = None
        
    def _setup_sensor_and_physical_output(self):
        self.feedbackSW = Pin(self.FEEDBACK_SW_PIN, Pin.IN)        
        self.solenoid = Pin(self.SOLENOID_PIN, Pin.OUT)
        self.buzzer = Pin(self.BUZZER_PIN, Pin.OUT)
        self.SW_feedback_prev_state = None
        self.SW_feedback_current_state = self.feedbackSW.value()
        
        
    def _setup_communication(self):
        self.RTen_pin = Pin(self.RTEN_PIN, Pin.OUT)
        self.uart = UART(0, baudrate=9600)
        self._set_rten_mode(self.RECEIVE)
        self.uart.init(9600)
        
    #--------------------------------------------------------------------#
    # common backend function
        
    def _set_rten_mode(self, mode):
        self.RTen_pin.value(mode)
        utime.sleep(0.3)
        
    def _ensure_remove_frame(self, data):
        data = data.strip()  # Remove any newline characters
        if data.startswith(';;;') and data.endswith(';;;'):
            return data[3:-3]
        else:
            print("Framing error, data:", repr(data))
            return None

    def _receive_messege(self):
        if self.uart.any():
            data = self.uart.read().decode().strip()
            unframed_data = self._ensure_remove_frame(data)
            return unframed_data
        return None
    
    def _get_json_command(self):
        unframed_data = self._receive_messege()
        if unframed_data:
            json_data = ujson.loads(unframed_data)
            return json_data
        return None
        
    def _is_my_command(self, command):
        print(command['assign_to'])
        if command['assign_to'] == self.locker_id:
            return True
        else:
            return False
        
    def _set_buzzer_state(self, mode):
        self.buzzer.value(mode)
        
    def _framing_data(self, data):
        return ';;;' + data + ';;;'
        
    def _create_framed_log_str(self, action, actor):
        log_data = {
            "from_locker_id": self.locker_id,
            "action": action,
            "actor": actor,
            "timestamp": utime.time()
            }
        log_str = ujson.dumps(log_data)
        framed_data = self._framing_data(log_str)
        return framed_data
    
    def _record_action(self, action, actor):
        log = self._create_framed_log_str(action, actor)
        self.log_queue.append(log)
        
    def _set_locker_state(self, mode, actor):
        self.solenoid.value(mode)
        self._record_action('UNLOCK' if mode == self.OPEN else 'LOCK', actor)
        
    def _send_log(self):
        if len(self.log_queue) > 0:
            log = self.log_queue[0]
            self._set_rten_mode(self.TRANSMIT)
            self.uart.write(log.encode())
            self.uart.flush()
            utime.sleep(1)
            self._set_rten_mode(self.RECEIVE)
            utime.sleep(0.2)
        
    def _is_acknowledge_in_time(self):
        pass
        #start_time = utime.ticks_ms()
        #while utime.ticks_diff(utime.ticks_ms(), start_time) < self.WAIT_FOR_ACK_TIMEOUT_MS:
        #    command = self._get_my_command()
        #    if command:
        #        if command['action'] == "ACK":
        #            return True
        #return False
    
    def _get_my_command(self):
        command = self._get_json_command()
        if command:
            if self._is_my_command(command):
                print(command)
                self.play_buzzer(500)
                utime.sleep_ms(1000)
                return command
    
    def _update_feedback_state(self):
        if self.SW_feedback_prev_state != self.SW_feedback_current_state:
            if self.SW_feedback_prev_state == self.OPEN and self.SW_feedback_current_state == self.CLOSED:
                self._set_locker_state(self.CLOSED, 'Developper')
                self._record_action('CLOSED', 'Developper')
            else:
                self._record_action('OPEN', 'Developper')
                
    def _update_SW_feedback(self):
        self.SW_feedback_prev_state = self.SW_feedback_current_state
        self.SW_feedback_current_state = self.feedbackSW.value()
        self._update_feedback_state()
        
    def _free_log(self):
        self.log_queue.pop(0)
        self._dump_queue_to_log_file()
        
    def _operate_command(self):
        if self.command_queue:
            command = self.command_queue.pop(0)
            if self._is_my_command(command):
                print("Command for me:", command)
                self.play_buzzer(50)
                if command['action'] == "UNLOCK":
                    print("UNLOCK")
                    self.play_buzzer(500)
                    self.unlock_locker(command['actor'])
                elif command['action'] == "LOCK":
                    print("LOCK")
                    self.play_buzzer(500)
                    self.lock_locker(command['actor'])
            else:
                print("Command not for me:", command)
                
    def _read_command(self):
        messages = []
        while self.uart.any():
            raw_data = self.uart.read().decode().strip()
            print("Raw UART data:", repr(raw_data))
            unframed = self._ensure_remove_frame(raw_data)
            if unframed:
                try:
                    msg = ujson.loads(unframed)
                    messages.append(msg)
                except Exception as e:
                    print("JSON parse error:", e)
        return messages
        
        
    #--------------------------------------------------------------------#
    # frontend function
    
    def process_incoming_command(self):
        #command = self._get_my_command()
        #print(f"This is from process incoming command {command}")
        #if command != None:
        #    self.play_buzzer(5000)
        #    self._operate_command(command)
        if self.uart.any():
            raw_data = self.uart.read().decode().strip()
            print("Raw UART data:", repr(raw_data))
            unframed_data = self._ensure_remove_frame(raw_data)
            if unframed_data:
                command = ujson.loads(unframed_data)
                if command:
                    if self._is_my_command(command):
                        print("Command for me:", command)
                        self.play_buzzer(50)
                        if command['action'] == "UNLOCK":
                            print("UNLOCK")
                            self.play_buzzer(500)
                            self.unlock_locker(command['actor'])
                        elif command['action'] == "LOCK":
                            print("LOCK")
                            self.play_buzzer(500)
                            self.lock_locker(command['actor'])
        
    def broadcast_log(self):
        if self.log_queue:
            log = self.log_queue[0]
            self._set_rten_mode(self.TRANSMIT)
            self.uart.write(log.encode())
            self.uart.flush()
            utime.sleep(1)
            self._set_rten_mode(self.RECEIVE)
            utime.sleep(0.2)
            # Remove the log after broadcasting
            self.log_queue.pop(0)
            self._dump_queue_to_log_file()
            
    def update_sensor_state(self):
        self._update_SW_feedback()
                
    def play_buzzer(self, duration_ms):
        self._set_buzzer_state(self.OPEN)
        utime.sleep_ms(duration_ms)
        self._set_buzzer_state(self.CLOSED)

    def unlock_locker(self, actor='Developer'):
        self._set_locker_state(self.OPEN, actor)
        self.play_buzzer(50)

    def lock_locker(self, actor='Developer'):
        self._set_locker_state(self.CLOSED, actor)
        self.play_buzzer(50)
        
    def collect_command(self):
        msgs = self._read_command()
        for msg in msgs:
            self.command_queue.append(msg)

    def main_loop(self):
        last_dump_time = utime.time()
        try:
            while True:
                self.collect_command()
                self._operate_command()
                self.update_sensor_state()
                self.broadcast_log()
                
                if utime.time() - last_dump_time >= 1800:
                    print(f"Dumb at: {utime.time()}")
                    self._dump_queue_to_log_file()
                    self._setup_log_queue()
                    last_dump_time = utime.time()
                    
        finally:
            self._dump_queue_to_log_file()

a = Locker()
a.main_loop()
