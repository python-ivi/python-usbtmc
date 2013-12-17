"""

Python USBTMC driver

Copyright (c) 2012 Alex Forencich

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

import usb.core
import usb.util
import struct
import time
import os

# constants
USBTMC_bInterfaceClass    = 0xFE
USBTMC_bInterfaceSubClass = 3
USBTMC_bInterfaceProtocol = 0
USB488_bInterfaceProtocol = 1

USBTMC_MSGID_DEV_DEP_MSG_OUT            = 1
USBTMC_MSGID_REQUEST_DEV_DEP_MSG_IN     = 2
USBTMC_MSGID_DEV_DEP_MSG_IN             = 2
USBTMC_MSGID_VENDOR_SPECIFIC_OUT        = 126
USBTMC_MSGID_REQUEST_VENDOR_SPECIFIC_IN = 127
USBTMC_MSGID_VENDOR_SPECIFIC_IN         = 127
USB488_MSGID_TRIGGER                    = 128

USBTMC_STATUS_SUCCESS                  = 0x01
USBTMC_STATUS_PENDING                  = 0x02
USBTMC_STATUS_FAILED                   = 0x80
USBTMC_STATUS_TRANSFER_NOT_IN_PROGRESS = 0x81
USBTMC_STATUS_SPLIT_NOT_IN_PROGRESS    = 0x82
USBTMC_STATUS_SPLIT_IN_PROGRESS        = 0x83
USB488_STATUS_INTERRUPT_IN_BUSY        = 0x20

USBTMC_REQUEST_INITIATE_ABORT_BULK_OUT     = 1
USBTMC_REQUEST_CHECK_ABORT_BULK_OUT_STATUS = 2
USBTMC_REQUEST_INITIATE_ABORT_BULK_IN      = 3
USBTMC_REQUEST_CHECK_ABORT_BULK_IN_STATUS  = 4
USBTMC_REQUEST_INITIATE_CLEAR              = 5
USBTMC_REQUEST_CHECK_CLEAR_STATUS          = 6
USBTMC_REQUEST_GET_CAPABILITIES            = 7
USBTMC_REQUEST_INDICATOR_PULSE             = 64

USB488_READ_STATUS_BYTE = 128
USB488_REN_CONTROL      = 160
USB488_GOTO_LOCAL       = 161
USB488_LOCAL_LOCKOUT    = 162

# Exceptions
class UsbtmcException(Exception): pass

def list_devices():
    "List all connected USBTMC devices"
    
    def is_usbtmc_device(dev):
        for cfg in dev:
            d = usb.util.find_descriptor(cfg, bInterfaceClass = USBTMC_bInterfaceClass,
                                        bInterfaceSubClass = USBTMC_bInterfaceSubClass)
            return d is not None
    
    return usb.core.find(find_all = True, custom_match = is_usbtmc_device)

def find_device(idVendor = None, idProduct = None, iSerial = None):
    "Find USBTMC instrument"
    
    devs = list_devices()
    
    if len(devs) == 0:
        return None
    
    for dev in devs:
        if dev.idVendor != idVendor or dev.idProduct != idProduct:
            continue
        
        if iSerial is None:
            return dev
        else:
            s = ''
            
            # try reading serial number
            try:
                s = usb.util.get_string(dev, 256, 3)
            except:
                pass
            
            if iSerial == s:
                return dev
        
    return None

class Instrument(object):
    "USBTMC instrument interface client"
    def __init__(self, *args, **kwargs):
        "Create new USBTMC instrument object"
        self.idVendor = 0
        self.idProduct = 0
        self.iSerial = None
        self.device = None
        self.iface = None
        self.term_char = None
        
        resource = None
        
        # process arguments
        if len(args) == 1:
            if type(args[0]) == str:
                resource = args[0]
            else:
                self.device = args[0]
        if len(args) >= 2:
            self.idVendor = args[0]
            self.idProduct = args[1]
        if len(args) >= 3:
            self.iSerial = args[2]
        
        for op in kwargs:
            val = kwargs[op]
            if op == 'idVendor':
                self.idVendor = val
            elif op == 'idProduct':
                self.idProduct = val
            elif op == 'iSerial':
                self.iSerial = val
            elif op == 'device':
                self.device = val
            elif op == 'dev':
                self.device = val
            elif op == 'term_char':
                self.term_char = val
            elif op == 'resource':
                resource = val
        
        if resource is not None:
            if resource[:3] == 'USB' and '::' in resource:
                # argument is a VISA resource string
                res = args[0].split('::')
                if len(res) < 4:
                    raise UsbtmcException("Invalid resource string")
                self.idVendor = int(res[1], 0)
                self.idProduct = int(res[2], 0)
                self.iSerial = None
                if len(res) > 4:
                    self.iSerial = res[3]
            else:
                raise UsbtmcException("Invalid resource string")
        
        self.max_recv_size = 1024*1024
        
        self.timeout = 1000
        
        self.bulk_in_ep = None
        self.bulk_out_ep = None
        self.interrupt_in_ep = None
        
        self.last_btag = 0
        
        # find device
        if self.device is None:
            if self.idVendor is None or self.idProduct is None:
                raise UsbtmcException("No device specified")
            else:
                self.device = find_device(self.idVendor, self.idProduct, self.iSerial)
                if self.device is None:
                    raise UsbtmcException("Device not found")
        
        # initialize device
        if os.name == 'posix':
            if self.device.is_kernel_driver_active(0):
                self.device.detach_kernel_driver(0)
        
        self.device.set_configuration()
        self.device.set_interface_altsetting()
        
        # find USBTMC interface
        for cfg in self.device:
            for iface in cfg:
                if (iface.bInterfaceClass == USBTMC_bInterfaceClass and
                   iface.bInterfaceSubClass == USBTMC_bInterfaceSubClass):
                    self.iface = iface
                    break
            else:
                continue
            break
        
        if self.iface is None:
            raise UsbtmcException("Not a USBTMC device")
        
        # find endpoints
        for ep in self.iface:
            ep_at = ep.bmAttributes
            ep_dir = ep.bEndpointAddress & usb.ENDPOINT_DIR_MASK
            ep_type = ep_at & usb.ENDPOINT_TYPE_MASK
            
            if (ep_type == usb.ENDPOINT_TYPE_BULK):
                if (ep_dir == usb.ENDPOINT_IN):
                    self.bulk_in_ep = ep
                elif (ep_dir == usb.ENDPOINT_OUT):
                    self.bulk_out_ep = ep
            elif (ep_type == usb.ENDPOINT_TYPE_INTERRUPT):
                if (ep_dir == usb.ENDPOINT_IN):
                    self.interrupt_in_ep = ep
        
        if self.bulk_in_ep is None or self.bulk_out_ep is None:
            raise UsbtmcException("Invalid endpoint configuration")
        
        self.reset()
        
        time.sleep(0.01) # prevents a very repeatable pipe error
        
        self.get_capabilities()
    
    def reset(self):
        if os.name == 'posix':
            self.device.reset()
    
    def is_usb488(self):
        return self.iface.bInterfaceProtocol == USB488_bInterfaceProtocol
    
    def get_capabilities(self):
        b=self.device.ctrl_transfer(
            usb.util.build_request_type(usb.util.CTRL_IN, usb.util.CTRL_TYPE_CLASS, usb.util.CTRL_RECIPIENT_INTERFACE),
            USBTMC_REQUEST_GET_CAPABILITIES,
            0x0000,
            self.iface.index,
            0x0018,
            timeout=self.timeout)
        if (b[0] == USBTMC_STATUS_SUCCESS):
            # process capabilities
            pass
    
    # message header management
    def pack_bulk_out_header(self, msgid):
        self.last_btag = btag = (self.last_btag % 255) + 1
        return struct.pack('BBBx', msgid, btag, ~btag & 0xFF)
    
    def pack_dev_dep_msg_out_header(self, transfer_size, eom = True):
        hdr = self.pack_bulk_out_header(USBTMC_MSGID_DEV_DEP_MSG_OUT)
        return hdr+struct.pack("<LBxxx", transfer_size, eom)
    
    def pack_dev_dep_msg_in_header(self, transfer_size, term_char = None):
        hdr = self.pack_bulk_out_header(USBTMC_MSGID_DEV_DEP_MSG_IN)
        transfer_attributes = 0
        if term_char is None:
            term_char = 0
        else:
            transfer_attributes = 2
            term_char = str(self.term_char).encode('utf-8')[0]
        return hdr+struct.pack("<LBBxx", transfer_size, transfer_attributes, term_char)
    
    def pack_vendor_specific_out_header(self, transfer_size):
        hdr = self.pack_bulk_out_header(USBTMC_MSGID_VENDOR_SPECIFIC_OUT)
        return hdr+struct.pack("<Lxxxx", transfer_size)
    
    def pack_vendor_specific_in_header(self, transfer_size):
        hdr = self.pack_bulk_out_header(USBTMC_MSGID_VENDOR_SPECIFIC_IN)
        return hdr+struct.pack("<Lxxxx", transfer_size)
    
    def unpack_bulk_in_header(self, data):
        msgid, btag, btaginverse = struct.unpack_from('BBBx', data)
        return (msgid, btag, btaginverse)
    
    def unpack_dev_dep_resp_header(self, data):
        msgid, btag, btaginverse = self.unpack_bulk_in_header(data)
        transfer_size, transfer_attributes = struct.unpack_from('<LBxxx', data, 4)
        data = data[12:transfer_size+12]
        return (msgid, btag, btaginverse, transfer_size, transfer_attributes, data)
    
    def write_raw(self, data):
        "Write binary data to instrument"
        
        eom = False
        
        num = len(data)
        
        offset = 0
        
        while num > 0:
            if num <= self.max_recv_size:
                eom = True
            
            block = data[offset:offset+self.max_recv_size]
            size = len(block)
            
            data = self.pack_dev_dep_msg_out_header(size, eom) + block + b'\0'*((4 - (size % 4)) % 4)
            
            self.bulk_out_ep.write(data)
            
            offset += size
            num -= size

    def read_raw(self, num=-1):
        "Read binary data from instrument"
        
        read_len = self.max_recv_size
        if num > 0 and num < self.max_recv_size:
            read_len = num
        
        eom = False
        
        term_char = None
        
        if self.term_char is not None:
            term_char = str(self.term_char).encode('utf-8')[0]
        
        read_data = b''
        
        while not eom:
            req = self.pack_dev_dep_msg_in_header(read_len, term_char)
            self.bulk_out_ep.write(req)
            
            resp = self.bulk_in_ep.read(read_len+12, timeout = self.timeout)
            
            msgid, btag, btaginverse, transfer_size, transfer_attributes, data = self.unpack_dev_dep_resp_header(resp.tostring())
            
            eom = transfer_attributes & 1
            
            read_data += data
            
            if num > 0:
                num = num - len(data)
                if num <= 0:
                    break
                if num < read_len:
                    read_len = num
            
        return read_data
    
    def ask_raw(self, data, num=-1):
        "Write then read binary data"
        self.write_raw(data)
        return self.read_raw(num)
    
    def write(self, message, encoding = 'utf-8'):
        "Write string to instrument"
        if message.__class__ is tuple or message.__class__ is list:
            # recursive call for a list of commands
            for message_i in message:
                self.write(message_i, encoding)
            return
        
        self.write_raw(str(message).encode(encoding))

    def read(self, num=-1, encoding = 'utf-8'):
        "Read string from instrument"
        return self.read_raw(num).decode(encoding).rstrip('\r\n')

    def ask(self, message, num=-1, encoding = 'utf-8'):
        "Write then read string"
        self.write(message, encoding)
        return self.read(num, encoding)
    
    def read_stb(self):
        "Read status byte"
        raise NotImplementedError()
    
    def trigger(self):
        "Send trigger command"
        self.write("*TRG")
    
    def clear(self):
        "Send clear command"
        self.write("*CLS")
    
    def remote(self):
        "Send remote command"
        raise NotImplementedError()
    
    def local(self):
        "Send local command"
        raise NotImplementedError()
    
    def lock(self):
        "Send lock command"
        raise NotImplementedError()
    
    def unlock(self):
        "Send unlock command"
        raise NotImplementedError()



