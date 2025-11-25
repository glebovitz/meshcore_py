import socket
import threading

from ..buffer_writer import BufferWriter
from ..buffer_reader import BufferReader
from ..constants import Constants
from .connection import Connection


class TCPConnection(Connection):
    def __init__(self, host: str, port: int):
        super().__init__()
        self.host = host
        self.port = port
        self.read_buffer = bytearray()
        self.socket = None
        self._recv_thread = None

    def connect(self):
        """Connect to TCP server and start receive loop."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.socket.connect((self.host, self.port))
            self.on_connected()
        except Exception as e:
            print("Connection Error", e)
            return

        # Start background thread to receive data
        self._recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        self._recv_thread.start()

    def _recv_loop(self):
        """Background loop to receive data from socket."""
        try:
            while True:
                data = self.socket.recv(4096)
                if not data:
                    break
                self.on_socket_data_received(data)
        except Exception as e:
            print("Receive Error", e)
        finally:
            self.on_disconnected()

    def on_socket_data_received(self, data: bytes):
        """Append received bytes to buffer and process frames."""
        self.read_buffer.extend(data)

        frame_header_length = 3
        while len(self.read_buffer) >= frame_header_length:
            try:
                frame_header = BufferReader(self.read_buffer[:frame_header_length])

                frame_type = frame_header.read_byte()
                if frame_type not in (
                    Constants.SerialFrameTypes.Incoming,
                    Constants.SerialFrameTypes.Outgoing,
                ):
                    # unexpected byte, skip
                    self.read_buffer = self.read_buffer[1:]
                    continue

                frame_length = frame_header.read_uint16_le()
                if not frame_length:
                    self.read_buffer = self.read_buffer[1:]
                    continue

                required_length = frame_header_length + frame_length
                if len(self.read_buffer) < required_length:
                    break

                frame_data = self.read_buffer[frame_header_length:required_length]
                self.read_buffer = self.read_buffer[required_length:]

                self.on_frame_received(frame_data)

            except Exception as e:
                print("Failed to process frame", e)
                break

    def close(self):
        try:
            if self.socket:
                self.socket.close()
        except Exception:
            pass

    def write(self, data: bytes):
        """Send raw bytes to socket."""
        if self.socket:
            self.socket.sendall(data)

    def write_frame(self, frame_type: int, frame_data: bytes):
        """Construct and send a framed packet."""
        frame = BufferWriter()
        frame.write_byte(frame_type)
        frame.write_uint16_le(len(frame_data))
        frame.write_bytes(frame_data)
        self.write(frame.to_bytes())

    def send_to_radio_frame(self, data: bytes):
        """Send 'app to radio' frame (0x3c '<')."""
        self.emit("tx", data)
        self.write_frame(0x3C, data)
