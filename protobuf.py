import unicodedata
import struct


def _get_field_id(b, sidx):
    eidx = sidx
    val = 0
    offset = 0
    while (b[eidx] & 0x80) == 0x80:
        val = val + ((b[eidx] & 0x7F) << offset)
        offset += 7
        eidx += 1
    val = val + ((b[eidx] & 0x7F) << offset)
    return val >> 3, eidx + 1

def _get_varint(b, sidx):
    eidx = sidx
    val = 0
    offset = 0
    while (b[eidx] & 0x80) == 0x80:
        val = val + ((b[eidx] & 0x7F) << offset)
        offset += 7
        eidx += 1
    val = val + ((b[eidx] & 0x7F) << offset)
    return val, eidx + 1

def get_fixedint(b, sidx, length):
    eidx = sidx + length
    assume_int = False
    dval = 0
    try:
        dval = struct.unpack('d' if length==8 else 'f', b[sidx:eidx])[0]
        if int(dval) == 0 or dval < 0:
            assume_int = True
    except (ValueError, struct.error):
        pass        # Could be from dval being NaN
    return int.from_bytes(b[sidx:eidx], byteorder='little') if assume_int else dval, eidx

def get_string_val(b, sidx, length):
    s = b[sidx:sidx+length].decode()
    s2 = "".join(ch for ch in s if unicodedata.category(ch)[0]!="C" or ch in ['\t','\n','\r'])
    if s != s2:
        raise ValueError("Probably not a string")
    return s

def fast_decoder(msg, depth=1):
    retval = {}

    b = bytes.fromhex(msg)
    if len(b) < 2:
        return retval

    idx = 0
    while idx < len(b):
        field_type = b[idx] & 0x7
        field_id, idx = _get_field_id(b, idx)

        try:
            is_str_hint = (type(retval[field_id]) == str or (type(retval[field_id]) == list and type(retval[field_id][1]) == str)) if retval.get(field_id) else None
            if field_type == 0:
                # int32, int64, uint32, uint64, sint32, sint64, bool, enum
                val, idx = _get_varint(b, idx)
            elif field_type == 1:
                # 1: fixed64, sfixed64, double
                val, idx = get_fixedint(b, idx, 8)
            elif field_type == 5:
                # 5: fixed32, sfixed32, float
                val, idx = get_fixedint(b, idx, 4)
            elif field_type == 2:
                # string, protobuf, etc.
                length, idx = _get_varint(b, idx)
                if length != 0:
                    _inner = None
                    if is_str_hint is not None:
                        if is_str_hint:
                            try:
                                _inner = get_string_val(b, idx, length)
                            except (UnicodeDecodeError, ValueError):
                                pass
                        
                        if not _inner:
                            _inner = fast_decoder(b[idx:idx+length].hex(), depth=depth+1)
                            if _inner in (None, -1):
                                _inner = None
                                if not is_str_hint:
                                    try:
                                        _inner = get_string_val(b, idx, length)
                                    except (UnicodeDecodeError, ValueError):
                                        pass
                                
                                if not _inner:
                                    _inner = b[idx:idx+length].hex()
                    else:
                        # Assume it's a string
                        try:
                            _inner = get_string_val(b, idx, length)
                        except (UnicodeDecodeError, ValueError):
                            _inner = fast_decoder(b[idx:idx+length].hex(), depth=depth+1)
                            if _inner in (None, -1):
                                _inner = b[idx:idx+length].hex()
                    val = _inner
                else:
                    val = ""
                idx += length
            elif field_type > 5 or field_id == 0:
                # Either of these edge cases would make it sound like we failed to parse a protobuf package
                return None
            else:
                return None
            
            if retval.get(field_id):
                if type(retval[field_id]) != list:
                    retval[field_id] = [retval[field_id]]
                retval[field_id].append(val)
            else:
                retval[field_id] = val
            
        except IndexError:
            # We went too far in the buffer, so we'll return None
            return -1
    
    return retval
