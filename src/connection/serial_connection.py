from ..buffer_writer import BufferWriter
from ..buffer_reader import BufferReader
from ..constants import Constants
from .connection import Connection


class SerialConnection(Connection):
    def __init__(self):
        super().__init__()
        self.read_buffer = bytearray()
        if type(self) is SerialConnection:
            raise RuntimeError("SerialConnection is abstract and cannot be instantiated directly.")

    async def write(self, data: bytes):
        """Abstract method — must be implemented by subclass."""
        raise NotImplementedError("write must be implemented by SerialConnection subclass.")

    async def write_frame(self, frame_type: int, frame_data: bytes):
        """Construct and send a framed packet."""
        frame = BufferWriter()
        frame.write_byte(frame_type)
        frame.write_uint16_le(len(frame_data))
        frame.write_bytes(frame_data)
        await self.write(frame.to_bytes())

    async def send_to_radio_frame(self, data: bytes):
        """Send 'app to radio' frame (0x3c '<')."""
        self.emit("tx", data)
        await self.write_frame(0x3C, data)

    async def on_data_received(self, value: bytes):
        """Append received bytes to buffer and process frames."""
        self.read_buffer.extend(value)

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
