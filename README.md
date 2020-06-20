# pyrubymarshal
A python module to (partially) read Ruby marshal files + RXDATA files

## Examples

Reading a ruby marshal file:
```python
from pyrubymarshal import Marshal
m = Marshal()
with open("filename here", "rb") as f:
  result = m.unmarshal(f.read())
```

Reading an RXDATA file:
```python
from pyrubymarshal import Marshal
from pyrubymarshal.rgss import RGSS_PARSERS

m = Marshal()
m.register_user_parsers(RGSS_PARSERS)
with open("Map001.rxdata", "rb") as f:
    res = m.unmarshal(f.read())

print(res.type)  # RPG::Map
```

## Types
* RubyObject - a ruby object. You can access its `type` field to get its Ruby class name
* Symbol - a ruby symbol.
* IVar - an instance variable, whatever that is. Its `v` attribute contains the actual value.
* MarshalError - an exception raised when the file can't be decoded.

## TODO
* Add more error checking
* Add more RGSS types
* Add an option to marshal python objects
