# meshcore/connection/base_connection.py

from meshcore.buffer.buffer_writer import BufferWriter
from meshcore.buffer.buffer_reader import BufferReader
from meshcore.constants import Constants
from meshcore.events import EventEmitter


class Connection(EventEmitter):
    """
    Base connection class for MeshCore.
    Subclasses must implement transport-specific methods like close() and send_to_radio_frame().
    """

    async def on_connected(self):
        try:
            await self.device_query(Constants.SupportedCompanionProtocolVersion)
        except Exception:
            pass
        self.emit("connected")

    def on_disconnected(self):
        self.emit("disconnected")

    async def close(self):
        raise NotImplementedError("Subclass must implement close()")

    async def send_to_radio_frame(self, data: bytes):
        raise NotImplementedError("Subclass must implement send_to_radio_frame()")

    # -------------------------
    # Command senders
    # -------------------------

    async def send_command_app_start(self):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.AppStart)
        data.write_uint8(1)  # appVer
        data.write_bytes(b"\x00" * 6)  # reserved
        data.write_string("test")
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_send_txt_msg(self, txt_type, attempt, sender_timestamp, pubkey_prefix, text):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.SendTxtMsg)
        data.write_uint8(txt_type)
        data.write_uint8(attempt)
        data.write_uint32_le(sender_timestamp)
        data.write_bytes(pubkey_prefix[:6])  # only first 6 bytes
        data.write_string(text)
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_send_channel_txt_msg(self, txt_type, channel_idx, sender_timestamp, text):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.SendChannelTxtMsg)
        data.write_uint8(txt_type)
        data.write_uint8(channel_idx)
        data.write_uint32_le(sender_timestamp)
        data.write_string(text)
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_get_contacts(self, since=None):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.GetContacts)
        if since is not None:
            data.write_uint32_le(since)
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_get_device_time(self):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.GetDeviceTime)
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_set_device_time(self, epoch_secs):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.SetDeviceTime)
        data.write_uint32_le(epoch_secs)
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_send_self_advert(self, advert_type):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.SendSelfAdvert)
        data.write_uint8(advert_type)
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_set_advert_name(self, name):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.SetAdvertName)
        data.write_string(name)
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_add_update_contact(self, public_key, type_, flags, out_path_len,
                                              out_path, adv_name, last_advert, adv_lat, adv_lon):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.AddUpdateContact)
        data.write_bytes(public_key)
        data.write_uint8(type_)
        data.write_uint8(flags)
        data.write_uint8(out_path_len)
        data.write_bytes(out_path)  # 64 bytes
        data.write_cstring(adv_name, 32)  # fixed length
        data.write_uint32_le(last_advert)
        data.write_uint32_le(adv_lat)
        data.write_uint32_le(adv_lon)
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_sync_next_message(self):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.SyncNextMessage)
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_set_radio_params(self, freq, bw, sf, cr):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.SetRadioParams)
        data.write_uint32_le(freq)
        data.write_uint32_le(bw)
        data.write_uint8(sf)
        data.write_uint8(cr)
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_set_tx_power(self, tx_power):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.SetTxPower)
        data.write_uint8(tx_power)
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_reset_path(self, pubkey):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.ResetPath)
        data.write_bytes(pubkey)  # 32 bytes
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_set_advert_lat_lon(self, lat, lon):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.SetAdvertLatLon)
        data.write_int32_le(lat)
        data.write_int32_le(lon)
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_remove_contact(self, pubkey):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.RemoveContact)
        data.write_bytes(pubkey)  # 32 bytes
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_share_contact(self, pubkey):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.ShareContact)
        data.write_bytes(pubkey)  # 32 bytes
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_export_contact(self, pubkey=None):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.ExportContact)
        if pubkey:
            data.write_bytes(pubkey)  # 32 bytes
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_import_contact(self, advert_packet_bytes):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.ImportContact)
        data.write_bytes(advert_packet_bytes)
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_reboot(self):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.Reboot)
        data.write_string("reboot")
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_get_battery_voltage(self):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.GetBatteryVoltage)
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_device_query(self, app_target_ver):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.DeviceQuery)
        data.write_uint8(app_target_ver)
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_export_private_key(self):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.ExportPrivateKey)
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_import_private_key(self, private_key):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.ImportPrivateKey)
        data.write_bytes(private_key)
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_send_raw_data(self, path, raw_data):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.SendRawData)
        data.write_uint8(len(path))
        data.write_bytes(path)
        data.write_bytes(raw_data)
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_send_login(self, public_key, password):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.SendLogin)
        data.write_bytes(public_key)  # 32 bytes
        data.write_string(password)   # max 15 chars
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_send_status_req(self, public_key):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.SendStatusReq)
        data.write_bytes(public_key)  # 32 bytes
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_send_telemetry_req(self, public_key):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.SendTelemetryReq)
        data.write_uint8(0)  # reserved
        data.write_uint8(0)  # reserved
        data.write_uint8(0)  # reserved
        data.write_bytes(public_key)  # 32 bytes
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_send_binary_req(self, public_key, request_code_and_params):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.SendBinaryReq)
        data.write_bytes(public_key)  # 32 bytes
        data.write_bytes(request_code_and_params)
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_get_channel(self, channel_idx):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.GetChannel)
        data.write_uint8(channel_idx)
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_set_channel(self, channel_idx, name, secret):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.SetChannel)
        data.write_uint8(channel_idx)
        data.write_cstring(name, 32)
        data.write_bytes(secret)
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_sign_start(self):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.SignStart)
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_sign_data(self, data_to_sign):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.SignData)
        data.write_bytes(data_to_sign)
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_sign_finish(self):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.SignFinish)
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_send_trace_path(self, tag, auth, path):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.SendTracePath)
        data.write_uint32_le(tag)
        data.write_uint32_le(auth)
        data.write_uint8(0)  # flags
        data.write_bytes(path)
        await self.send_to_radio_frame(data.to_bytes())

    async def send_command_set_other_params(self, manual_add_contacts):
        data = BufferWriter()
        data.write_uint8(Constants.CommandCodes.SetOtherParams)
        data.write_uint8(manual_add_contacts)  # 0 or 1
        await self.send_to_radio_frame(data.to_bytes())

    def on_ok_response(self, reader: BufferReader):
        self.emit(Constants.ResponseCodes.Ok, {})

    def on_err_response(self, reader: BufferReader):
        err_code = reader.read_uint8() if reader.remaining() > 0 else None
        self.emit(Constants.ResponseCodes.Err, {"errCode": err_code})

    def on_contacts_start_response(self, reader: BufferReader):
        self.emit(Constants.ResponseCodes.ContactsStart, {
            "count": reader.read_uint32_le(),
        })

    def on_contact_response(self, reader: BufferReader):
        self.emit(Constants.ResponseCodes.Contact, {
            "publicKey": reader.read_bytes(32),
            "type": reader.read_uint8(),
            "flags": reader.read_uint8(),
            "outPathLen": reader.read_int8(),
            "outPath": reader.read_bytes(64),
            "advName": reader.read_cstring(32),
            "lastAdvert": reader.read_uint32_le(),
            "advLat": reader.read_uint32_le(),
            "advLon": reader.read_uint32_le(),
            "lastMod": reader.read_uint32_le(),
        })

    def on_end_of_contacts_response(self, reader: BufferReader):
        self.emit(Constants.ResponseCodes.EndOfContacts, {
            "mostRecentLastmod": reader.read_uint32_le(),
        })

    def on_sent_response(self, reader: BufferReader):
        self.emit(Constants.ResponseCodes.Sent, {
            "result": reader.read_int8(),
            "expectedAckCrc": reader.read_uint32_le(),
            "estTimeout": reader.read_uint32_le(),
        })

    def on_export_contact_response(self, reader: BufferReader):
        self.emit(Constants.ResponseCodes.ExportContact, {
            "advertPacketBytes": reader.read_remaining_bytes(),
        })

    def on_battery_voltage_response(self, reader: BufferReader):
        self.emit(Constants.ResponseCodes.BatteryVoltage, {
            "batteryMilliVolts": reader.read_uint16_le(),
        })

    def on_device_info_response(self, reader: BufferReader):
        self.emit(Constants.ResponseCodes.DeviceInfo, {
            "firmwareVer": reader.read_int8(),
            "reserved": reader.read_bytes(6),
            "firmwareBuildDate": reader.read_cstring(12),
            "manufacturerModel": reader.read_string(),
        })

    def on_private_key_response(self, reader: BufferReader):
        self.emit(Constants.ResponseCodes.PrivateKey, {
            "privateKey": reader.read_bytes(64),
        })

    def on_disabled_response(self, reader: BufferReader):
        self.emit(Constants.ResponseCodes.Disabled, {})

    def on_channel_info_response(self, reader: BufferReader):
        idx = reader.read_uint8()
        name = reader.read_cstring(32)
        remaining = reader.remaining()
        if remaining == 16:
            self.emit(Constants.ResponseCodes.ChannelInfo, {
                "channelIdx": idx,
                "name": name,
                "secret": reader.read_bytes(remaining),
            })
        else:
            print(f"ChannelInfo unexpected key length: {remaining}")

    def on_sign_start_response(self, reader: BufferReader):
        self.emit(Constants.ResponseCodes.SignStart, {
            "reserved": reader.read_uint8(),
            "maxSignDataLen": reader.read_uint32_le(),
        })

    def on_signature_response(self, reader: BufferReader):
        self.emit(Constants.ResponseCodes.Signature, {
            "signature": reader.read_bytes(64),
        })

    def on_self_info_response(self, reader: BufferReader):
        self.emit(Constants.ResponseCodes.SelfInfo, {
            "type": reader.read_uint8(),
            "txPower": reader.read_uint8(),
            "maxTxPower": reader.read_uint8(),
            "publicKey": reader.read_bytes(32),
            "advLat": reader.read_int32_le(),
            "advLon": reader.read_int32_le(),
            "reserved": reader.read_bytes(3),
            "manualAddContacts": reader.read_uint8(),
            "radioFreq": reader.read_uint32_le(),
            "radioBw": reader.read_uint32_le(),
            "radioSf": reader.read_uint8(),
            "radioCr": reader.read_uint8(),
            "name": reader.read_string(),
        })

    def on_curr_time_response(self, reader: BufferReader):
        self.emit(Constants.ResponseCodes.CurrTime, {
            "epochSecs": reader.read_uint32_le(),
        })

    def on_no_more_messages_response(self, reader: BufferReader):
        self.emit(Constants.ResponseCodes.NoMoreMessages, {})

    def on_contact_msg_recv_response(self, reader: BufferReader):
        self.emit(Constants.ResponseCodes.ContactMsgRecv, {
            "pubKeyPrefix": reader.read_bytes(6),
            "pathLen": reader.read_uint8(),
            "txtType": reader.read_uint8(),
            "senderTimestamp": reader.read_uint32_le(),
            "text": reader.read_string(),
        })

    def on_channel_msg_recv_response(self, reader: BufferReader):
        self.emit(Constants.ResponseCodes.ChannelMsgRecv, {
            "channelIdx": reader.read_int8(),
            "pathLen": reader.read_uint8(),
            "txtType": reader.read_uint8(),
            "senderTimestamp": reader.read_uint32_le(),
            "text": reader.read_string(),
        })

    def on_advert_push(self, reader: BufferReader):
        self.emit(Constants.PushCodes.Advert, {
            "publicKey": reader.read_bytes(32),
        })

    def on_path_updated_push(self, reader: BufferReader):
        self.emit(Constants.PushCodes.PathUpdated, {
            "publicKey": reader.read_bytes(32),
        })

    def on_send_confirmed_push(self, reader: BufferReader):
        self.emit(Constants.PushCodes.SendConfirmed, {
            "ackCode": reader.read_uint32_le(),
            "roundTrip": reader.read_uint32_le(),
        })

    def on_msg_waiting_push(self, reader: BufferReader):
        self.emit(Constants.PushCodes.MsgWaiting, {})

    def on_raw_data_push(self, reader: BufferReader):
        self.emit(Constants.PushCodes.RawData, {
            "lastSnr": reader.read_int8() / 4,
            "lastRssi": reader.read_int8(),
            "reserved": reader.read_uint8(),
            "payload": reader.read_remaining_bytes(),
        })

    def on_login_success_push(self, reader: BufferReader):
        self.emit(Constants.PushCodes.LoginSuccess, {
            "reserved": reader.read_uint8(),
            "pubKeyPrefix": reader.read_bytes(6),
        })

    def on_status_response_push(self, reader: BufferReader):
        self.emit(Constants.PushCodes.StatusResponse, {
            "reserved": reader.read_uint8(),
            "pubKeyPrefix": reader.read_bytes(6),
            "statusData": reader.read_remaining_bytes(),
        })

    def on_log_rx_data_push(self, reader: BufferReader):
        self.emit(Constants.PushCodes.LogRxData, {
            "lastSnr": reader.read_int8() / 4,
            "lastRssi": reader.read_int8(),
            "raw": reader.read_remaining_bytes(),
        })

    def on_telemetry_response_push(self, reader: BufferReader):
        self.emit(Constants.PushCodes.TelemetryResponse, {
            "reserved": reader.read_uint8(),
            "pubKeyPrefix": reader.read_bytes(6),
            "lppSensorData": reader.read_remaining_bytes(),
        })

    def on_binary_response_push(self, reader: BufferReader):
        self.emit(Constants.PushCodes.BinaryResponse, {
            "reserved": reader.read_uint8(),
            "tag": reader.read_uint32_le(),
            "responseData": reader.read_remaining_bytes(),
        })

    def on_trace_data_push(self, reader: BufferReader):
        reserved = reader.read_uint8()
        path_len = reader.read_uint8()
        self.emit(Constants.PushCodes.TraceData, {
            "reserved": reserved,
            "pathLen": path_len,
            "flags": reader.read_uint8(),
            "tag": reader.read_uint32_le(),
            "authCode": reader.read_uint32_le(),
            "pathHashes": reader.read_bytes(path_len),
            "pathSnrs": reader.read_bytes(path_len),
            "lastSnr": reader.read_int8() / 4,
        })

    def on_new_advert_push(self, reader: BufferReader):
        self.emit(Constants.PushCodes.NewAdvert, {
            "publicKey": reader.read_bytes(32),
            "type": reader.read_uint8(),
            "flags": reader.read_uint8(),
            "outPathLen": reader.read_int8(),
            "outPath": reader.read_bytes(64),
            "advName": reader.read_cstring(32),
            "lastAdvert": reader.read_uint32_le(),
            "advLat": reader.read_uint32_le(),
            "advLon": reader.read_uint32_le(),
            "lastMod": reader.read_uint32_le(),
        })

    # -------------------------
    # High-level convenience APIs
    # -------------------------

    async def get_contacts(self, since=None, timeout=None):
        """
        Request contacts list from the device.
        Resolves when EndOfContacts is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_end(data):
            self.off(Constants.ResponseCodes.EndOfContacts, on_end)
            fut.set_result(data)

        self.once(Constants.ResponseCodes.EndOfContacts, on_end)
        await self.send_command_get_contacts(since)

        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def get_self_info(self, timeout=None):
        """
        Request self info from the device.
        Resolves when SelfInfo response is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_self_info(data):
            self.off(Constants.ResponseCodes.SelfInfo, on_self_info)
            fut.set_result(data)

        self.once(Constants.ResponseCodes.SelfInfo, on_self_info)
        await self.send_command_app_start()

        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def get_waiting_messages(self, timeout=None):
        """
        Request next waiting message.
        Resolves when NoMoreMessages or a message response is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_no_more(data):
            self.off(Constants.ResponseCodes.NoMoreMessages, on_no_more)
            fut.set_result({"messages": []})

        def on_contact_msg(data):
            self.off(Constants.ResponseCodes.ContactMsgRecv, on_contact_msg)
            fut.set_result({"contactMsg": data})

        def on_channel_msg(data):
            self.off(Constants.ResponseCodes.ChannelMsgRecv, on_channel_msg)
            fut.set_result({"channelMsg": data})

        self.once(Constants.ResponseCodes.NoMoreMessages, on_no_more)
        self.once(Constants.ResponseCodes.ContactMsgRecv, on_contact_msg)
        self.once(Constants.ResponseCodes.ChannelMsgRecv, on_channel_msg)

        await self.send_command_sync_next_message()
        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def get_channel(self, channel_idx, timeout=None):
        """
        Request channel info by index.
        Resolves when ChannelInfo response is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_channel_info(data):
            self.off(Constants.ResponseCodes.ChannelInfo, on_channel_info)
            fut.set_result(data)

        self.once(Constants.ResponseCodes.ChannelInfo, on_channel_info)
        await self.send_command_get_channel(channel_idx)

        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def send_advert(self, advert_type, timeout=None):
        """
        Send an advert and resolve when Ok or Err is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_ok(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_result(True)

        def on_err(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_exception(Exception("Advert failed"))

        self.once(Constants.ResponseCodes.Ok, on_ok)
        self.once(Constants.ResponseCodes.Err, on_err)

        await self.send_command_send_self_advert(advert_type)
        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def set_advert_name(self, name, timeout=None):
        """
        Set advert name and resolve when Ok or Err is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_ok(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_result(True)

        def on_err(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_exception(Exception("SetAdvertName failed"))

        self.once(Constants.ResponseCodes.Ok, on_ok)
        self.once(Constants.ResponseCodes.Err, on_err)

        await self.send_command_set_advert_name(name)
        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def set_advert_lat_lon(self, lat, lon, timeout=None):
        """
        Set advert latitude/longitude and resolve when Ok or Err is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_ok(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_result(True)

        def on_err(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_exception(Exception("SetAdvertLatLon failed"))

        self.once(Constants.ResponseCodes.Ok, on_ok)
        self.once(Constants.ResponseCodes.Err, on_err)

        await self.send_command_set_advert_lat_lon(lat, lon)
        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def set_tx_power(self, tx_power, timeout=None):
        """
        Set transmit power and resolve when Ok or Err is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_ok(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_result(True)

        def on_err(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_exception(Exception("SetTxPower failed"))

        self.once(Constants.ResponseCodes.Ok, on_ok)
        self.once(Constants.ResponseCodes.Err, on_err)

        await self.send_command_set_tx_power(tx_power)
        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def reboot(self, timeout=None):
        """
        Reboot the device and resolve when Ok or Err is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_ok(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_result(True)

        def on_err(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_exception(Exception("Reboot failed"))

        self.once(Constants.ResponseCodes.Ok, on_ok)
        self.once(Constants.ResponseCodes.Err, on_err)

        await self.send_command_reboot()
        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def get_battery_voltage(self, timeout=None):
        """
        Request battery voltage and resolve when BatteryVoltage response is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_voltage(data):
            self.off(Constants.ResponseCodes.BatteryVoltage, on_voltage)
            fut.set_result(data)

        self.once(Constants.ResponseCodes.BatteryVoltage, on_voltage)
        await self.send_command_get_battery_voltage()

        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def device_query(self, app_target_ver, timeout=None):
        """
        Query device for supported protocol version.
        Resolves when DeviceInfo response is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_info(data):
            self.off(Constants.ResponseCodes.DeviceInfo, on_info)
            fut.set_result(data)

        self.once(Constants.ResponseCodes.DeviceInfo, on_info)
        await self.send_command_device_query(app_target_ver)

        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def export_private_key(self, timeout=None):
        """
        Request private key export.
        Resolves when PrivateKey response is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_key(data):
            self.off(Constants.ResponseCodes.PrivateKey, on_key)
            fut.set_result(data)

        self.once(Constants.ResponseCodes.PrivateKey, on_key)
        await self.send_command_export_private_key()

        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def import_private_key(self, private_key, timeout=None):
        """
        Import a private key and resolve when Ok or Err is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_ok(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_result(True)

        def on_err(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_exception(Exception("ImportPrivateKey failed"))

        self.once(Constants.ResponseCodes.Ok, on_ok)
        self.once(Constants.ResponseCodes.Err, on_err)
        await self.send_command_import_private_key(private_key)

        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def get_channel(self, channel_idx, timeout=None):
        """
        Request channel info by index.
        Resolves when ChannelInfo response is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_channel_info(data):
            self.off(Constants.ResponseCodes.ChannelInfo, on_channel_info)
            fut.set_result(data)

        self.once(Constants.ResponseCodes.ChannelInfo, on_channel_info)
        await self.send_command_get_channel(channel_idx)

        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def set_channel(self, channel_idx, name, secret, timeout=None):
        """
        Set channel info and resolve when Ok or Err is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_ok(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_result(True)

        def on_err(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_exception(Exception("SetChannel failed"))

        self.once(Constants.ResponseCodes.Ok, on_ok)
        self.once(Constants.ResponseCodes.Err, on_err)
        await self.send_command_set_channel(channel_idx, name, secret)

        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def sign_start(self, timeout=None):
        """
        Begin signing session. Resolves when SignStart response is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_start(data):
            self.off(Constants.ResponseCodes.SignStart, on_start)
            fut.set_result(data)

        self.once(Constants.ResponseCodes.SignStart, on_start)
        await self.send_command_sign_start()

        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def sign_data(self, data_to_sign, timeout=None):
        """
        Send data to be signed. Resolves when Signature response is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_sig(data):
            self.off(Constants.ResponseCodes.Signature, on_sig)
            fut.set_result(data)

        self.once(Constants.ResponseCodes.Signature, on_sig)
        await self.send_command_sign_data(data_to_sign)

        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def sign_finish(self, timeout=None):
        """
        Finish signing session. Resolves when Ok or Err is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_ok(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_result(True)

        def on_err(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_exception(Exception("SignFinish failed"))

        self.once(Constants.ResponseCodes.Ok, on_ok)
        self.once(Constants.ResponseCodes.Err, on_err)
        await self.send_command_sign_finish()

        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def send_trace_path(self, tag, auth, path, timeout=None):
        """
        Send a trace path. Resolves when Ok or Err is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_ok(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_result(True)

        def on_err(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_exception(Exception("SendTracePath failed"))

        self.once(Constants.ResponseCodes.Ok, on_ok)
        self.once(Constants.ResponseCodes.Err, on_err)
        await self.send_command_send_trace_path(tag, auth, path)

        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def add_update_contact(self, public_key, type_, flags, out_path_len,
                                 out_path, adv_name, last_advert, adv_lat, adv_lon, timeout=None):
        """
        Add or update a contact. Resolves when Ok or Err is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_ok(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_result(True)

        def on_err(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_exception(Exception("AddUpdateContact failed"))

        self.once(Constants.ResponseCodes.Ok, on_ok)
        self.once(Constants.ResponseCodes.Err, on_err)
        await self.send_command_add_update_contact(public_key, type_, flags, out_path_len,
                                                   out_path, adv_name, last_advert, adv_lat, adv_lon)

        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def remove_contact(self, pubkey, timeout=None):
        """
        Remove a contact. Resolves when Ok or Err is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_ok(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_result(True)

        def on_err(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_exception(Exception("RemoveContact failed"))

        self.once(Constants.ResponseCodes.Ok, on_ok)
        self.once(Constants.ResponseCodes.Err, on_err)
        await self.send_command_remove_contact(pubkey)

        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def share_contact(self, pubkey, timeout=None):
        """
        Share a contact. Resolves when Ok or Err is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_ok(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_result(True)

        def on_err(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_exception(Exception("ShareContact failed"))

        self.once(Constants.ResponseCodes.Ok, on_ok)
        self.once(Constants.ResponseCodes.Err, on_err)
        await self.send_command_share_contact(pubkey)

        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def export_contact(self, pubkey=None, timeout=None):
        """
        Export a contact. Resolves when ExportContact response is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_export(data):
            self.off(Constants.ResponseCodes.ExportContact, on_export)
            fut.set_result(data)

        self.once(Constants.ResponseCodes.ExportContact, on_export)
        await self.send_command_export_contact(pubkey)

        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def import_contact(self, advert_packet_bytes, timeout=None):
        """
        Import a contact. Resolves when Ok or Err is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_ok(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_result(True)

        def on_err(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_exception(Exception("ImportContact failed"))

        self.once(Constants.ResponseCodes.Ok, on_ok)
        self.once(Constants.ResponseCodes.Err, on_err)
        await self.send_command_import_contact(advert_packet_bytes)

        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def send_txt_msg(self, txt_type, attempt, sender_timestamp, pubkey_prefix, text, timeout=None):
        """
        Send a text message to a contact. Resolves when Sent response is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_sent(data):
            self.off(Constants.ResponseCodes.Sent, on_sent)
            fut.set_result(data)

        self.once(Constants.ResponseCodes.Sent, on_sent)
        await self.send_command_send_txt_msg(txt_type, attempt, sender_timestamp, pubkey_prefix, text)

        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def send_channel_txt_msg(self, txt_type, channel_idx, sender_timestamp, text, timeout=None):
        """
        Send a text message to a channel. Resolves when Sent response is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_sent(data):
            self.off(Constants.ResponseCodes.Sent, on_sent)
            fut.set_result(data)

        self.once(Constants.ResponseCodes.Sent, on_sent)
        await self.send_command_send_channel_txt_msg(txt_type, channel_idx, sender_timestamp, text)

        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def send_raw_data(self, path, raw_data, timeout=None):
        """
        Send raw data along a path. Resolves when Sent response is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_sent(data):
            self.off(Constants.ResponseCodes.Sent, on_sent)
            fut.set_result(data)

        self.once(Constants.ResponseCodes.Sent, on_sent)
        await self.send_command_send_raw_data(path, raw_data)

        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def sync_next_message(self, timeout=None):
        """
        Request next waiting message. Resolves when NoMoreMessages or a message response is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_no_more(data):
            self.off(Constants.ResponseCodes.NoMoreMessages, on_no_more)
            fut.set_result({"messages": []})

        def on_contact_msg(data):
            self.off(Constants.ResponseCodes.ContactMsgRecv, on_contact_msg)
            fut.set_result({"contactMsg": data})

        def on_channel_msg(data):
            self.off(Constants.ResponseCodes.ChannelMsgRecv, on_channel_msg)
            fut.set_result({"channelMsg": data})

        self.once(Constants.ResponseCodes.NoMoreMessages, on_no_more)
        self.once(Constants.ResponseCodes.ContactMsgRecv, on_contact_msg)
        self.once(Constants.ResponseCodes.ChannelMsgRecv, on_channel_msg)

        await self.send_command_sync_next_message()
        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def send_status_req(self, public_key, timeout=None):
        """
        Send a status request. Resolves when StatusResponse push is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_status(data):
            self.off(Constants.PushCodes.StatusResponse, on_status)
            fut.set_result(data)

        self.once(Constants.PushCodes.StatusResponse, on_status)
        await self.send_command_send_status_req(public_key)

        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def send_telemetry_req(self, public_key, timeout=None):
        """
        Send a telemetry request. Resolves when TelemetryResponse push is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_telemetry(data):
            self.off(Constants.PushCodes.TelemetryResponse, on_telemetry)
            fut.set_result(data)

        self.once(Constants.PushCodes.TelemetryResponse, on_telemetry)
        await self.send_command_send_telemetry_req(public_key)

        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def send_binary_req(self, public_key, request_code_and_params, timeout=None):
        """
        Send a binary request. Resolves when BinaryResponse push is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_binary(data):
            self.off(Constants.PushCodes.BinaryResponse, on_binary)
            fut.set_result(data)

        self.once(Constants.PushCodes.BinaryResponse, on_binary)
        await self.send_command_send_binary_req(public_key, request_code_and_params)

        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    async def set_other_params(self, manual_add_contacts, timeout=None):
        """
        Set other parameters (e.g. manualAddContacts flag).
        Resolves when Ok or Err is received.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_ok(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_result(True)

        def on_err(_):
            self.off(Constants.ResponseCodes.Ok, on_ok)
            self.off(Constants.ResponseCodes.Err, on_err)
            fut.set_exception(Exception("SetOtherParams failed"))

        self.once(Constants.ResponseCodes.Ok, on_ok)
        self.once(Constants.ResponseCodes.Err, on_err)
        await self.send_command_set_other_params(manual_add_contacts)

        return await asyncio.wait_for(fut, timeout) if timeout else await fut

    def on_frame_received(self, frame_bytes: bytes):
        reader = BufferReader(frame_bytes)
        code = reader.read_uint8()

        # Response dispatch table
        response_handlers = {
            Constants.ResponseCodes.Ok: self.on_ok_response,
            Constants.ResponseCodes.Err: self.on_err_response,
            Constants.ResponseCodes.ContactsStart: self.on_contacts_start_response,
            Constants.ResponseCodes.Contact: self.on_contact_response,
            Constants.ResponseCodes.EndOfContacts: self.on_end_of_contacts_response,
            Constants.ResponseCodes.Sent: self.on_sent_response,
            Constants.ResponseCodes.ExportContact: self.on_export_contact_response,
            Constants.ResponseCodes.BatteryVoltage: self.on_battery_voltage_response,
            Constants.ResponseCodes.DeviceInfo: self.on_device_info_response,
            Constants.ResponseCodes.PrivateKey: self.on_private_key_response,
            Constants.ResponseCodes.Disabled: self.on_disabled_response,
            Constants.ResponseCodes.ChannelInfo: self.on_channel_info_response,
            Constants.ResponseCodes.SignStart: self.on_sign_start_response,
            Constants.ResponseCodes.Signature: self.on_signature_response,
            Constants.ResponseCodes.SelfInfo: self.on_self_info_response,
            Constants.ResponseCodes.CurrTime: self.on_curr_time_response,
            Constants.ResponseCodes.NoMoreMessages: self.on_no_more_messages_response,
            Constants.ResponseCodes.ContactMsgRecv: self.on_contact_msg_recv_response,
            Constants.ResponseCodes.ChannelMsgRecv: self.on_channel_msg_recv_response,
        }

        # Push dispatch table
        push_handlers = {
            Constants.PushCodes.Advert: self.on_advert_push,
            Constants.PushCodes.PathUpdated: self.on_path_updated_push,
            Constants.PushCodes.SendConfirmed: self.on_send_confirmed_push,
            Constants.PushCodes.MsgWaiting: self.on_msg_waiting_push,
            Constants.PushCodes.RawData: self.on_raw_data_push,
            Constants.PushCodes.LoginSuccess: self.on_login_success_push,
            Constants.PushCodes.StatusResponse: self.on_status_response_push,
            Constants.PushCodes.LogRxData: self.on_log_rx_data_push,
            Constants.PushCodes.TelemetryResponse: self.on_telemetry_response_push,
            Constants.PushCodes.BinaryResponse: self.on_binary_response_push,
            Constants.PushCodes.TraceData: self.on_trace_data_push,
            Constants.PushCodes.NewAdvert: self.on_new_advert_push,
        }

        # Dispatch
        if code in response_handlers:
            response_handlers[code](reader)
        elif code in push_handlers:
            push_handlers[code](reader)
        else:
            print(f"Unknown frame code: {code}")
