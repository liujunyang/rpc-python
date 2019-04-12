def zigzag_encode(num):
        retval =  num * 2 if num >= 0 else -2 * num - 1
        return int(retval)

def zigzag_decode(num):
    retval = - (num + 1) / 2 if num % 2 else num / 2
    return int(retval)


print zigzag_encode(-1)
print zigzag_decode(1)
