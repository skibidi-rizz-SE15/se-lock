from QRManager import QRManager
from SlavePiLogic import SlavePiLogic

class MasterPi(QRManager):
    def __init__(self):
        super().__init__()
        self.slave_pi_logic: list[SlavePiLogic] = []
        
    def open(self, qr_code):
        payload = super().open(qr_code)
        for slave in self.slave_pi_logic:
            if slave.slave_id == payload['locker_id']:
                log = slave.open(payload['actor'])
                # send MQTT message to server
                pass
            
    def main_loop(self):
        # Main loop for the MasterPi
        while True:
            # Check for QR codes and process them
            qr_code = self._read_qr_code()
            if qr_code:
                self.open(qr_code)
            # Add any other necessary logic here, such as checking for new slaves or handling other events