import sys
import struct

from .rtypes import *

DEBUG = False

##callstackdepth = 0
##def trace(frame, event, arg):
##    global callstackdepth
##
##    sys.settrace(None)   # Disable trace
##    return
##    
##    if event == "return":
##        if "rmarshal" in frame.f_code.co_filename:
##            print("  " * callstackdepth, "==RETURN== ", frame.f_code.co_name, " ", arg, sep="")
##            callstackdepth -= 1
##
##    elif event == "call":
##        if "rmarshal" in frame.f_code.co_filename:
##            print("  " * callstackdepth, "==CALL== ", frame.f_code.co_name, sep="")
##            callstackdepth += 1
##
##    elif event == "exception":
##        if "rmarshal" in frame.f_code.co_filename:
##            print("  " * callstackdepth, "==EXCEPTION==", sep="")
##        
##    return trace

class Marshal():

    def __init__(self):
        self.user_parsers = {}

    def register_user_parsers(self, d):
        self.user_parsers.update(d)

    def unmarshal(self, x):
        return self.parse_marshal_file(x)

    def parse_marshal_file(self, x):
        if x[:2] != b"\x04\x08":
            raise MarshalError("Wrong marshal version, got %d.%d" % (x[0], x[1]))

        return self.parse_obj(x[2:], [], [])[0]

    def parse_obj(self, x, symbols, objcache):
        try:
            if x[0] == b"T"[0]:
                return True, 1
            elif x[0] == b"F"[0]:
                return False, 1
            elif x[0] == b"0"[0]:
                return None, 1
            elif x[0] == b"i"[0]:
                x, y = self.parse_fixnum(x[1:], symbols, objcache)
                return x, y + 1
            elif x[0] == b":"[0]:
                x, y = self.parse_symbol(x[1:], symbols, objcache)
                return x, y + 1
            elif x[0] == b";"[0]:
                x, y = self.parse_symlink(x[1:], symbols, objcache)
                return x, y + 1
            elif x[0] == b"["[0]:
                x, y = self.parse_array(x[1:], symbols, objcache)
                return x, y + 1
            elif x[0] == b"{"[0]:
                x, y = self.parse_hash(x[1:], symbols, objcache)
                return x, y + 1
            elif x[0] == b"I"[0]:
                x, y = self.parse_ivar(x[1:], symbols, objcache)
                return x, y + 1
            elif x[0] == b'"'[0]:
                x, y = self.parse_raw_string(x[1:], symbols, objcache)
                return x, y + 1
            elif x[0] == b'@'[0]:
                x, y = self.parse_objlink(x[1:], symbols, objcache)
                return x, y + 1
            elif x[0] == b"c"[0]:
                x, y = self.parse_class_name(x[1:], symbols, objcache)
                return x, y + 1
            elif x[0] == b"m"[0]:
                x, y = self.parse_module_name(x[1:], symbols, objcache)
                return x, y + 1
            elif x[0] == b"o"[0]:
                x, y = self.parse_object_instance(x[1:], symbols, objcache)
                return x, y + 1
            elif x[0] == b"u"[0]:
                x, y = self.parse_user(x[1:], symbols, objcache)
                return x, y + 1
            else:
                raise MarshalError("Unknown type: 0x%x" % (x[0],))
        except:
            if DEBUG:
                print(x[:100])
            raise

    def parse_user(self, x, symbols, objcache):
        i = 0
        name, di = self.parse_obj(x[i:], symbols, objcache)
        i += di

        if name.value in self.user_parsers:
            objcache.append(None)
            oid = len(objcache) - 1
            
            res, di = self.user_parsers[name.value].load(self, x[i:], symbols, objcache)
            i += di
            
            objcache[oid] = res
            return res, i
        else:
            raise MarshalError("Don't know how to decode class %s" % (name.value))

    def parse_symlink(self, x, symbols, objcache):
        i = 0
        n, di = self.parse_fixnum(x[i:], symbols, objcache)
        i += di

        # print(symbols[n-1], symbols[n])
        return symbols[n], i

    def parse_fixnum(self, x, symbols, objcache):
        # print(x[:100])
        size = x[0]
        if size == 0:
            return 0, 1
        
        elif 0 < size < 5:
            tmp = []
            for i in range(size):
                tmp.append(x[i + 1])
            for i in range(4-size):
                tmp.append(0x00)
            return struct.unpack("i", bytes(tmp))[0], size + 1

        elif 252 < size < 256:
            size = 256 - size
            tmp = []
            for i in range(size):
                tmp.append(x[i + 1])
            for i in range(4-(size)):
                tmp.append(0xff)
            return struct.unpack("i", bytes(tmp))[0], size + 1

        else:
            res = struct.unpack("b", bytes([x[0]]))[0]
            if res < 0:
                res += 5
            elif res > 0:
                res -= 5
            return res, 1

    def parse_symbol(self, x, symbols, objcache):
        # print(x[:100])
        i = 0

        n, di = self.parse_fixnum(x[i:], symbols, objcache)
        i += di

        sym = Symbol(x[i:i+n].decode("latin1"))
        symbols.append(sym)

        return sym, i + n

    def parse_array(self, x, symbols, objcache):
        # print(x[:100])
        i = 0

        objcache.append(None)
        oid = len(objcache) - 1
        
        n, di = self.parse_fixnum(x, symbols, objcache)
        i += di
        
        res = []
        for elemi in range(n):
            elem, di = self.parse_obj(x[i:], symbols, objcache)
            i += di
            
            res.append(elem)

        objcache[oid] = res

        return res, i

    def parse_object_instance(self, x, symbols, objcache):
        objcache.append(None)
        oid = len(objcache) - 1
        # print(x[:100])
        i = 0

        # print("Reading class name")
        class_name, di = self.parse_obj(x[i:], symbols, objcache)
        i += di
        # print(x[i:i+100])

        # print("Reading size")
        n, di = self.parse_fixnum(x[i:], symbols, objcache)
        i += di

        res = RubyObject({})
        res.type = class_name.value
        for elemi in range(n):
            # print(class_name, "key")
            key, di = self.parse_obj(x[i:], symbols, objcache)
            i += di

            # print(class_name, "value")
            value, di = self.parse_obj(x[i:], symbols, objcache)
            i += di

            # print(class_name, "%r %r" % (key, value))
            res.update({key: value})
            # print(res)

        objcache[oid] = res
        return res, i

    def parse_raw_string(self, x, symbols, objcache):
        i = 0
        
        objcache.append(None)
        oid = len(objcache) - 1

        n, di = self.parse_fixnum(x[i:], symbols, objcache)
        i += di

        res = x[i:i+n]

        objcache[oid] = res
        
        return res, i + n

    def parse_hash(self, x, symbols, objcache):
        i = 0

        objcache.append(None)
        oid = len(objcache) - 1
        
        # print("Reading size")
        n, di = self.parse_fixnum(x[i:], symbols, objcache)
        i += di

        res = {}
        for elemi in range(n):
            # print("key")
            key, di = self.parse_obj(x[i:], symbols, objcache)
            i += di

            # print("value")
            value, di = self.parse_obj(x[i:], symbols, objcache)
            i += di

            res.update({key: value})
            
        # objcache.append(res)
        objcache[oid] = res
        return res, i

    def parse_objlink(self, x, symbols, objcache):
        i = 0
        n, di = self.parse_fixnum(x[i:], symbols, objcache)
        i += di

        return objcache[n + 1], i

    def parse_ivar(self, x, symbols, objcache):
        i = 0

        objcache.append(None)
        oid = len(objcache) - 1

        value, di = self.parse_obj(x[i:], symbols, objcache)
        i += di

        i += 1   # There's always this ACK byte after that I have no idea what it is for
        
        name, di = self.parse_obj(x[i:], symbols, objcache)
        if type(name) == Symbol:
            if name.value in ("E", "encoding"):
                i += di
                encoding, di = self.parse_obj(x[i:], symbols, objcache)
                i += di
            else:
                encoding = None
        else:
            encoding = None

        res = IVar(value, encoding)
        # objcache.append(res)
        objcache[oid] = res
        
        return res, i
