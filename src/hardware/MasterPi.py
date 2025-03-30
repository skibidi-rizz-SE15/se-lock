from QRManager import QRManager
from SlavePiLogic import SlavePiLogic

class MasterPi(QRManager):
    def __init__(self):
        super().__init__("key.txt")
        self.slave_pi_logic: list[SlavePiLogic] = []
        
    def open(self, qr_code):    
        payload = super().open(qr_code)
        print(f"decrypted payload: {payload}")
        if payload is None:
            raise("Payload is None")
        for slave in self.slave_pi_logic:
            if slave.slave_id == payload['locker_id']:
                log = slave.open(payload['actor'])
                # send MQTT message to server
                self.send_log_to_server("test")
            
    def send_log_to_server(self, log):
        pass
            
    def main_loop(self):
        # Main loop for the MasterPi
        while True:
            self.process_camera()
            for slave in self.slave_pi_logic:
                log = slave._receive_data()
                if log:
                    slave.send_ack()
        
            
master = MasterPi()
master.slave_pi_logic.append(SlavePiLogic("1212312121"))  # Example of adding a slave
master._activate_camera()
master.main_loop()  # Start the main loop