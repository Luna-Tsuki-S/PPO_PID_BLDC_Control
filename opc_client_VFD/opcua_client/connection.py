from opcua import Client, ua
import time
import logging

#self, Now_Temp, Ida_Temp, Now_RPM, RPM_Spd, PID_PER, USS_Run, USS_SPD,url, act


class OPCUAConnection:
    def __init__(self, Now_Temp, Ida_Temp, Now_Hum, Ida_Hum, USS_Run, url, act):
        self._Now_Temp = Now_Temp
        self._Ida_Temp = Ida_Temp
        self._Now_Hum = Now_Hum
        self._Ida_Hum = Ida_Hum
        # self._Now_RPM = Now_RPM
        # self._RPM_Spd = RPM_Spd
        # self._PID_PER = PID_PER
        self._USS_Run = USS_Run
        # self._USS_SPD = USS_SPD
        self.url = url
        self.client = None  # Initialize as None
        self._act = act
    def connect(self):
        try:
            if self.client is None:
                self.client = Client(self.url)
            try:
                # Try to get server time to check connection
                self.client.get_server_time()
                return True
            except:
                # If we can't get server time, try to reconnect
                self.client.connect()
                return True
        except Exception as e:
            print(f"Error connecting to server: {e}")
            logging.error(f"Error connecting to server: {e}", exc_info=True)
            return False

    def disconnect(self):
        try:
            if self.client:
                self.client.disconnect()
                self.client = None
        except Exception as e:
            print(f"Error disconnecting from server: {e}")
            logging.error(f"Error disconnecting from server: {e}", exc_info=True)

    def send_data(self, node, data):
        try:
            if not self.client:
                if not self.connect():
                    return None
            if node != "ns=4;i=5":
                opc_node = self.client.get_node(node)
                value = ua.DataValue(ua.Variant(data, ua.VariantType.Float))
                opc_node.set_value(value)
                return f"Node {node}, Data sent: {value}"
            else:
                opc_node = self.client.get_node(node)
                value = ua.DataValue(ua.Variant(data, ua.VariantType.Boolean))
                opc_node.set_value(value)
                return f"Node {node}, Data sent: {value}"
        except Exception as e:
            print(f"Error sending data to {node}: {e}")
            logging.error(f"Error sending data to {node}: {e}", exc_info=True)
            return None

    def get_data(self, node):
        try:
            if not self.client:
                if not self.connect():
                    return None
            opc_node = self.client.get_node(node)
            return opc_node.get_value()
        except Exception as e:
            print(f"Error getting data from {node}: {e}")
            logging.error(f"Error getting data from {node}: {e}", exc_info=True)
            return None

    @property
    def Now_Temp(self):
        return self._Now_Temp

    @Now_Temp.setter
    def Now_Temp(self, value):
        self._Now_Temp = value

    @property
    def Ida_Temp(self):
        return self._Ida_Temp

    @Ida_Temp.setter
    def Ida_Temp(self, value):
        self._Ida_Temp = value

    @property
    def Now_Hum(self):
        return self._Now_Hum

    @Now_Hum.setter
    def Now_Hum(self, value):
        self._Now_Hum = value

    @property
    def Ida_Hum(self):
        return self._Ida_Hum

    @Ida_Hum.setter
    def Ida_Hum(self, value):
        self._Ida_Hum = value
    
    # @property
    # def Now_RPM(self):
    #     return self._Now_RPM
    
    # @Now_RPM.setter
    # def Now_RPM(self, value):
    #     self._Now_RPM = value

    # @property
    # def RPM_Spd(self):
    #     return self._RPM_Spd
    
    # @RPM_Spd.setter
    # def RPM_Spd(self, value):
    #     self._RPM_Spd = value
    
    # @property
    # def PID_PER(self):
    #     return self._PID_PER
    
    # @PID_PER.setter
    # def PID_PER(self, value):
    #     self._PID_PER = value
    
    @property
    def USS_Run(self):
        return self._USS_Run
    
    @USS_Run.setter
    def USS_Run(self, value):
        self._USS_Run = value
    
    # @property
    # def USS_SPD(self):
    #     return self._USS_SPD
    
    # @USS_SPD.setter
    # def USS_SPD(self, value):
    #     self._USS_SPD = value   
    
    @property
    def act(self):
        return self._act

    @act.setter
    def act(self, value):
        self._act = value

    def connection(self):
        try:
            if not self.connect():
                return 1

            while True:
                Now_RPM = self.get_data("ns=4;i=4")
                USS_SPD = self.get_data("ns=4;i=6")
                RPM_Spd = self.get_data("ns=4;i=8")
                HUM_PID_PER = self.get_data("ns=4;i=11")
                TEM_PID_PER = self.get_data("ns=4;i=12")
                pid_to_rpm = (TEM_PID_PER + HUM_PID_PER) / 2 / 27648 * 1650

                data = pid_to_rpm / self._act

                self.send_data("ns=4;i=2", self._Ida_Temp)
                self.send_data("ns=4;i=3", self._Now_Temp)
                self.send_data("ns=4;i=9", self._Ida_Hum)
                self.send_data("ns=4;i=10", self._Now_Hum)
                self.send_data("ns=4;i=5", self._USS_Run)

                if data > 0.5:
                    per = data / 27648
                    print(f"Data: {data}, Percentage: {per}")
                    self.send_data("ns=4;i=8", self._act)
                else:
                    self.send_data("ns=4;i=8", pid_to_rpm)
                
                    
                print(f"Ida_Temp: {self._Ida_Temp}, Now_Temp: {self._Now_Temp}, Ida_Hum: {self._Ida_Hum}, Now_Hum: {self._Now_Hum}, Now_RPM: {Now_RPM}, RPM_Spd: {RPM_Spd}, TEM_PID_PER: {TEM_PID_PER}, HUM_PID_PER: {HUM_PID_PER},USS_Run: {self._USS_Run}, USS_SPD: {USS_SPD}")
                logging.info(f"[Cycle] Ida_Temp: {self._Ida_Temp}, Now_Temp: {self._Now_Temp}, Now_RPM: {self._Now_RPM}")
                
                if self._Ida_Temp == 0:
                    continue  # Prevent division by zero
                time.sleep(20)

        except Exception as e:
            print(f"Error during connection loop: {e}")
            self.disconnect()
            logging.critical(f"Error during connection loop: {e}", exc_info=True)
            return 1
        
        finally:
            self.disconnect()
