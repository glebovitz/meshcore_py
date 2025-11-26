import serial
import threading
from .serial_connection import SerialConnection


class PySerialConnection(SerialConnection):
    """
    Concrete SerialConnection using pyserial.
    Equivalent to NodeJSSerialConnection in JS.
    """

    def __init__(self, path: str, baudrate: int = 115200):
        super().__init__()
        self.serial_port_path = path
        self.baudrate = baudrate
        self.serial_port = None
        self._recv_thread = None

    async def connect(self):
        try:
            self.serial_port = serial.Serial(
                port=self.serial_port_path,
                baudrate=self.baudrate,
                timeout=0  # non-blocking
            )
            await self.on_connected()
        except Exception as e:
            print("SerialPort Error:", e)
            return

        # Start background thread to read incoming data
        self._recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        self._recv_thread.start()

    def _recv_loop(self):
        try:
            while self.serial_port and self.serial_port.is_open:
                data = self.serial_port.read(4096)
                if data:
                    # feed into SerialConnection's parser
                    asyncio.run(self.on_data_received(data))
        except Exception as e:
            print("Serial receive error:", e)
        finally:
            asyncio.run(self.on_disconnected())

    async def close(self):
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
        except Exception as e:
            print("Failed to close serial port, ignoring...", e)

    async def write(self, data: bytes):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(data)
