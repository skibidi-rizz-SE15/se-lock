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
                self.send_log_to_server()
            
    def send_log_to_server(self, log):
        pass
            
    def main_loop(self):
        # Main loop for the MasterPi
        while True:
            self.process_camera()
            ## Check for QR codes and process them
            #qr_code = self._read_qr_code()
            #if qr_code:
            #    self.open(qr_code)
            ## Add any other necessary logic here, such as checking for new slaves or handling other events
            
master = MasterPi()
master.slave_pi_logic.append(SlavePiLogic("1212312121"))  # Example of adding a slave
master._activate_camera()
master.main_loop()  # Start the main loop
