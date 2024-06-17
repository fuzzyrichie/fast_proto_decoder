# Fast Protobuf Decoder
A fast, lightweight Protobuf message decoder when you don't have the schema. Takes guesses on some fields in order to improve on speed.

## Overview
Ever needed to debug a Protobuf message without the full context of what data is included in it? I did for a security project I was working on. Existing libraries missed a few decodings or were too slow for what I needed. I also realized that I was OK with the tradeoff of some decoding misses for certain types of data in order to improve on overall speed.

## How to Use
Take the hex string of a Protobuf message, call fast_decoder, and you're set:

```python
import json
from protobuf import fast_decoder

a = "0a2f0a084a6f686e20446f6510011a106a6f686e406578616d706c652e636f6d220f0a0b3131312d3232322d33333310010a1e0a084a616e6520446f6510021a106a616e65406578616d706c652e636f6d"
print(json.dumps(fast_decoder(a), indent=2))
```

Yields the following output:
```json
{
  "1": [
    {
      "1": "John Doe",
      "2": 1,
      "3": "john@example.com",
      "4": {
        "1": "111-222-333",
        "2": 1
      }
    },
    {
      "1": "Jane Doe",
      "2": 2,
      "3": "jane@example.com"
    }
  ]
}
```

## Pros
- Faster than previous Protobuf decoders by multiple orders of magnitude.
- Catches many fields that other Protobuf decoders miss or incorrectly parse.
- Directly converts the Protobuf message into JSON.
- Less than 150 lines of code in total :smile:

## Cons
- Does not float up the original field type of the underlying Protobuf message, making it difficult to determine if an incorrect parsing has occurred.
- Does some guessing on what the field could be, which could lead to some incorrect parsing on some messages.
- Does not support groups, which are deprecated in newer versions of the Protobuf specification.

## References
- https://protobuf.dev/programming-guides/encoding/
- https://github.com/pawitp/protobuf-decoder/
- https://github.com/dannyhann/protobuf_decoder/
- https://stackoverflow.com/questions/4324790/removing-control-characters-from-a-string-in-python (for string guessing)
