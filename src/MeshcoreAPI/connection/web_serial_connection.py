from .serial_connection import SerialConnection

class WebSerialConnection(SerialConnection):
    """
    Placeholder for Web Serial connection.
    In JS this uses navigator.serial; in Python you'd use pyserial instead.
    """

    def __init__(self, serial_port=None):
        super().__init__()
        self.serial_port = serial_port
        self.reader = None
        self.writable = None

    @staticmethod
    async def open():
        """
        In JS this prompts the user via navigator.serial.
        In Python you'd need to implement device discovery with pyserial.
        """
        raise NotImplementedError("WebSerialConnection.open is browser-only. Use PySerialConnection in Python.")

    async def close(self):
        try:
            if self.reader:
                self.reader.release_lock()
        except Exception:
            pass

        try:
            if self.serial_port:
                self.serial_port.close()
        except Exception:
            pass

    async def write(self, data: bytes):
        """
        In JS this writes via serialPort.writable.
        In Python you'd use pyserial's write().
        """
        if not self.serial_port:
            raise RuntimeError("No serial port available")
        try:
            self.serial_port.write(data)
        except Exception as e:
            print("Failed to write to serial port:", e)

    async def read_loop(self):
        """
        In JS this continuously reads from serialPort.readable.
        In Python you'd use pyserial's read() in a loop.
        """
        raise NotImplementedError("WebSerialConnection.read_loop is browser-only. Use PySerialConnection in Python.")
