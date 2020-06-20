class IVar():

    def __init__(self, v, encoding=None):
        self.v = v.decode(encoding.decode("latin1"))
        # self.encoding = encoding

    def __repr__(self):
        return "IVar(%r)" % (self.v)

class RubyObject(dict):
    def __getattr__(self, x):
        for i in self.keys():
            if i.value[1:] == x:
                return self[i]
        
        raise AttributeError("%r object has not attribute %r" % (self.type, x))

    def __setattr__(self, x, y):
        for i in self.keys():
            if i.value[1:] == x:
                self[i] = y
        
        object.__setattr__(self, x, y)

    def __dir__(self):
        return [i.value[1:] for i in self.keys()]

    def __repr__(self):
        return self.type + "({" + ", ".join([repr(k) + " => " + repr(v) for k, v in self.items()]) + "})"

    def pprint(self):
        print(self.prepr())

    def prepr(self, indent=0):
        res = ""
        res += self.type + "({\n"
        for i in self.keys():
            res += (indent + 2) * " " + repr(i) + " => "
            obj = getattr(self, i.value[1:])
            if type(obj) == type(self):
                res += obj.prepr(indent=indent + 2)

            elif type(obj) in (list, tuple):
                res += self._prepr_iterable(obj, indent + 2)

            elif type(obj) == dict:
                res += self._prepr_dict(obj, indent + 2)

            else:
                res += repr(obj)
            
            res += ",\n"
        res += (indent) * " " + "})"
        
        return res

    def _prepr_iterable(self, obj, indent):
        res = "[\n"
        for i in obj:
            res += (indent + 2) * " "
            
            if type(i) == type(self):
                res += i.prepr(indent=indent + 2)

            elif type(i) in (list, tuple):
                res += self._prepr_iterable(i, indent + 2)

            elif type(i) == dict:
                res += self._prepr_dict(i, indent + 2)

            else:
                res += repr(i)
            
            res += ",\n"
        res += (indent) * " " + "]"

        return res

    def _prepr_dict(self, x, indent):
        res = "{\n"
        for i in x.keys():
            res += (indent + 2) * " " + repr(i) + ": "
            obj = x[i]
            if type(obj) == type(self):
                res += obj.prepr(indent=indent + 2)

            elif type(obj) in (list, tuple):
                res += self._prepr_iterable(obj, indent)

            elif type(obj) == dict:
                res += self._prepr_dict(obj, indent)

            else:
                res += repr(obj)
            
            res += ",\n"
        res += (indent) * " " + "}"
        
        return res

class Symbol():
    
    def __init__(self, v):
        self.value = v

    def __repr__(self):
        return ":" + str(self.value)

    def __hash__(self):
        return hash(self.value)

class MarshalError(Exception):
    pass
