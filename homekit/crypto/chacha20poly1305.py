# -*- coding: UTF-8 -*-

#
# Copyright 2018 Joachim Lusiardi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Implements the ChaCha20 stream cipher and the Poly1350 authenticator. More information can be found on
https://tools.ietf.org/html/rfc7539. See HomeKit spec page 51.
"""
from math import ceil


def rotate_left(num: int, num_size: int, shift_bits: int) -> int:
    """
    Rotate a number num of num_size bits by shift_bits bits. See
    https://en.wikipedia.org/wiki/Bitwise_operation#Rotate_no_carry for more information.

    :param num: the number to rotate
    :param num_size: the size of the number in bits
    :param shift_bits: the number of bits the number is rotated by
    :return: the rotated number
    """
    mask = (2 ** shift_bits - 1) << (num_size - shift_bits)
    bits = (num & mask) >> (num_size - shift_bits)
    num = (num << shift_bits) & (2 ** num_size - 1)
    num |= bits
    return num


def chacha20_quarter_round(s: list, a: int, b: int, c: int, d: int):
    """
    Computes a chacha20 quarter round on the given state s as describe in RFC7539 Chapter 2.1. The state gets updated
    inplace.

    :param s: the state
    :param a: the first index into the state
    :param b: the second index into the state
    :param c: the third index into the state
    :param d: the fourth index into the state
    :return: None
    """
    assert len(s) == 16, 'state must have 16 ints'
    s[a] = (s[a] + s[b]) & (2 ** 32 - 1)
    s[d] = (s[d] ^ s[a])
    s[d] = rotate_left(s[d], 32, 16)

    s[c] = (s[c] + s[d]) & (2 ** 32 - 1)
    s[b] = (s[b] ^ s[c])
    s[b] = rotate_left(s[b], 32, 12)

    s[a] = (s[a] + s[b]) & (2 ** 32 - 1)
    s[d] = (s[d] ^ s[a])
    s[d] = rotate_left(s[d], 32, 8)

    s[c] = (s[c] + s[d]) & (2 ** 32 - 1)
    s[b] = (s[b] ^ s[c])
    s[b] = rotate_left(s[b], 32, 7)


def convert(num: int) -> int:
    return int.from_bytes(num.to_bytes(4, byteorder='little'), byteorder='big')


def extract_nth_word(num: bytes, w: int) -> int:
    m = len(num)
    bs = num[m - 4 * (w + 1):m - 4 * (w + 0)]
    return int.from_bytes(bs, byteorder='big')


def chacha20_create_initial_state(key: bytes, nonce: bytes, counter: int) -> list:
    """
    Creates the initial chacha20 state for the block function as described in RFC7539 chapter 2.3.

    :param key: the 256 bit key to use as bytes
    :param nonce: the 96 bit nonce as bytes
    :param counter: the 32bit block counter
    :return: the initial state as list of ints
    """
    assert type(key) is bytes, 'key is no instance of bytes'
    assert len(key) == 32
    assert type(nonce) is bytes, 'nonce is no instance of bytes'
    assert len(nonce) == 3 * 32 / 8
    state = [0x61707865, 0x3320646e, 0x79622d32, 0x6b206574,
             0, 0, 0, 0,
             0, 0, 0, 0,
             0, 0, 0, 0]
    for i in range(0, 8):
        state[4 + i] = convert(extract_nth_word(key, 7 - i))
    state[12] = counter & (2 ** 32 - 1)
    state[13] = convert(extract_nth_word(nonce, 2))
    state[14] = convert(extract_nth_word(nonce, 1))
    state[15] = convert(extract_nth_word(nonce, 0))
    return state


def chacha20_inner_block(state: list):
    """
    The function to perform the inner quarter rounds as described in RFC7539 chapter 2.3.1. The state is updated
    inplace.

    :param state: the chacha20 state
    :return: None
    """
    assert len(state) == 16, 'state must have 16 ints'
    chacha20_quarter_round(state, 0, 4, 8, 12)
    chacha20_quarter_round(state, 1, 5, 9, 13)
    chacha20_quarter_round(state, 2, 6, 10, 14)
    chacha20_quarter_round(state, 3, 7, 11, 15)
    chacha20_quarter_round(state, 0, 5, 10, 15)
    chacha20_quarter_round(state, 1, 6, 11, 12)
    chacha20_quarter_round(state, 2, 7, 8, 13)
    chacha20_quarter_round(state, 3, 4, 9, 14)


def chacha20_block(key: bytes, nonce: bytes, counter: int) -> int:
    """
    The function to perform the computation for one chacha20 block as  described in RFC7539 chapter 2.3.1.

    :param key: the 256 bit key to use as bytes
    :param nonce: the 96 bit nonce as bytes
    :param counter: the 32bit block counter
    :return: the state serialized as int
    """
    assert type(key) is bytes, 'key is no instance of bytes'
    assert len(key) == 32
    assert type(nonce) is bytes, 'nonce is no instance of bytes'
    assert len(nonce) == 3 * 32 / 8
    state = chacha20_create_initial_state(key, nonce, counter)
    w_state = state.copy()
    for i in range(0, 10):
        chacha20_inner_block(w_state)
    result = 0
    for i in range(0, 16):
        state[i] = (state[i] + w_state[i]) & (2 ** 32 - 1)
        result <<= 32
        result += convert(state[i])
    return result


def chacha20_encrypt(key: bytes, counter: int, nonce: int, plaintext: bytes) -> bytes:
    assert type(key) is bytes, 'key is no instance of bytes'
    assert len(key) == 32
    assert type(nonce) is bytes, 'nonce is no instance of bytes'
    assert len(nonce) == 12
    encrypted = bytearray()
    for i in range(0, int(len(plaintext) / 64)):
        key_stream = chacha20_block(key, nonce, counter + i)
        key_stream = key_stream.to_bytes(64, byteorder='big')
        block = plaintext[i * 64:i * 64 + 64]
        encrypted += bytes([a ^ b for (a, b) in zip(block, key_stream)])

    if (len(plaintext) % 64) != 0:
        j = int(len(plaintext) / 64)
        key_stream = chacha20_block(key, nonce, counter + j)
        block = plaintext[(j * 64):len(plaintext)]
        key_stream = key_stream.to_bytes(64, byteorder='big')
        key_stream = key_stream[:len(block)]
        encrypted += bytes([a ^ b for (a, b) in zip(block, key_stream)])
    return encrypted


def clamp(r: int) -> int:
    tmp = r.to_bytes(length=16, byteorder='little')
    msk = 0x0ffffffc0ffffffc0ffffffc0fffffff.to_bytes(length=16, byteorder='big')
    res = bytearray()
    for i in range(0, len(tmp)):
        res.append(tmp[i] & msk[i])
    return int.from_bytes(res, byteorder='big')


def calc_r(k: int) -> int:
    assert type(k) is bytes, 'key is no instance of bytes'
    assert len(k) == 32
    tmp = k[0:16]
    return int.from_bytes(tmp, byteorder='big')


def calc_s(k: bytes) -> int:
    assert type(k) is bytes, 'key is no instance of bytes'
    assert len(k) == 32
    tmp = k[16:32]
    return int.from_bytes(tmp, byteorder='little')


def poly1305_mac(msg: bytes, key: bytes) -> bytes:
    assert type(key) is bytes, 'key is no instance of bytes'
    assert len(key) == 32
    r = calc_r(key)
    r = clamp(r)
    s = calc_s(key)
    a = 0
    p = (1 << 130) - 5
    for i in range(0, ceil(len(msg) / 16)):
        block = bytearray(msg[i * 16:i * 16 + 16])
        block.append(0x01)
        n = int.from_bytes(block, byteorder='little')
        a += n
        a = (r * a)
        a %= p
    a += s
    a &= (2 ** (16 * 8) - 1)
    return a.to_bytes(length=16, byteorder='little')


def poly1305_key_gen(key: bytes, nonce: bytes) -> bytes:
    assert type(key) is bytes, 'key is no instance of bytes'
    assert len(key) == 32
    assert type(nonce) is bytes, 'nonce is no instance of bytes'
    assert len(nonce) == 12
    counter = 0
    block = chacha20_block(key, nonce, counter)
    mask = (2 ** (32 * 8) - 1) << (32 * 8)
    block &= mask
    block >>= (32 * 8)
    block = block.to_bytes(length=32, byteorder='big')
    return block


def pad16(x: bytes) -> bytes:
    tmp = len(x) % 16
    if tmp == 0:
        return bytearray([])
    tmp = 16 - tmp
    return bytearray([0 for i in range(0, tmp)])


def chacha20_aead_encrypt(aad: bytes, key: bytes, iv: bytes, constant: bytes, plaintext: bytes):
    assert type(plaintext) in [bytes, bytearray], 'plaintext is no instance of bytes: %s' % str(type(plaintext))
    assert type(key) is bytes, 'key is no instance of bytes'
    assert len(key) == 32
    nonce = constant + iv
    otk = poly1305_key_gen(key, nonce)
    ciphertext = chacha20_encrypt(key, 1, nonce, plaintext)
    assert len(plaintext) == len(ciphertext)
    mac_data = aad + pad16(aad)
    assert len(mac_data) % 16 == 0
    mac_data += ciphertext + pad16(ciphertext)
    assert len(mac_data) % 16 == 0
    mac_data += len(aad).to_bytes(length=8, byteorder='little')
    mac_data += len(ciphertext).to_bytes(length=8, byteorder='little')
    tag = poly1305_mac(mac_data, otk)
    return ciphertext, tag


def chacha20_aead_verify_tag(aad: bytes, key: bytes, iv: bytes, constant: bytes, ciphertext: bytes):
    digest = ciphertext[-16:]
    ciphertext = ciphertext[:-16]

    nonce = constant + iv
    otk = poly1305_key_gen(key, nonce)
    mac_data = aad + pad16(aad)
    assert len(mac_data) % 16 == 0
    mac_data += ciphertext + pad16(ciphertext)
    assert len(mac_data) % 16 == 0
    mac_data += len(aad).to_bytes(length=8, byteorder='little')
    mac_data += len(ciphertext).to_bytes(length=8, byteorder='little')
    tag = poly1305_mac(mac_data, otk)

    return digest == tag


def chacha20_aead_decrypt(aad: bytes, key: bytes, iv: bytes, constant: bytes, ciphertext: bytes):
    assert type(ciphertext) in [bytes, bytearray], 'plaintext is no instance of bytes: %s' % str(type(ciphertext))
    assert type(key) is bytes, 'key is no instance of bytes'
    assert len(key) == 32

    # break up on difference
    if not chacha20_aead_verify_tag(aad, key, iv, constant, ciphertext):
        return False

    # decrypt and return
    ciphertext = ciphertext[:-16]
    nonce = constant + iv
    plaintext = chacha20_encrypt(key, 1, nonce, ciphertext)
    assert len(plaintext) == len(ciphertext)
    return plaintext


#
#   Implement some basic test with the test vectors from the RFC 7539
#
if __name__ == '__main__':
    # Test aus 2.1.1
    s = [0x11111111, 0, 0, 0,
         0x01020304, 0, 0, 0,
         0x9b8d6f43, 0, 0, 0,
         0x01234567, 0, 0, 0]
    chacha20_quarter_round(s, 0, 4, 8, 12)
    assert s[0] == 0xea2a92f4
    assert s[4] == 0xcb1cf8ce
    assert s[8] == 0x4581472e
    assert s[12] == 0x5881c4bb

    # Test aus 2.2.1
    s = [0x879531e0, 0xc5ecf37d, 0x516461b1, 0xc9a62f8a,
         0x44c20ef3, 0x3390af7f, 0xd9fc690b, 0x2a5f714c,
         0x53372767, 0xb00a5631, 0x974c541a, 0x359e9963,
         0x5c971061, 0x3d631689, 0x2098d9d6, 0x91dbd320]
    chacha20_quarter_round(s, 2, 7, 8, 13)

    assert s[2] == 0xbdb886dc
    assert s[7] == 0xcfacafd2
    assert s[8] == 0xe46bea80
    assert s[13] == 0xccc07c79

    # Test aus 2.3.2
    k = 0x000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f.to_bytes(length=32, byteorder='big')
    n = 0x000000090000004a00000000.to_bytes(length=12, byteorder='big')
    c = 1
    init = chacha20_create_initial_state(k, n, c)
    assert init == [0x61707865, 0x3320646e, 0x79622d32, 0x6b206574,
                    0x03020100, 0x07060504, 0x0b0a0908, 0x0f0e0d0c,
                    0x13121110, 0x17161514, 0x1b1a1918, 0x1f1e1d1c,
                    0x00000001, 0x09000000, 0x4a000000, 0x00000000]
    r = chacha20_block(k, n, c)
    assert r == 0x10f1e7e4d13b5915500fdd1fa32071c4c7d1f4c733c068030422aa9ac3d46c4ed2826446079faa0914c2d705d98b02a2b5129cd1de164eb9cbd083e8a2503c4e

    # Test aus 2.4.2
    k = 0x000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f.to_bytes(length=32, byteorder='big')
    n = 0x000000000000004a00000000.to_bytes(length=12, byteorder='big')
    c = 1
    plain_text = "Ladies and Gentlemen of the class of '99: If I could offer you only one tip for the future, sunscreen would be it."
    r = chacha20_encrypt(k, c, n, plain_text.encode())
    r_ = [0x6e, 0x2e, 0x35, 0x9a, 0x25, 0x68, 0xf9, 0x80, 0x41, 0xba, 0x07, 0x28, 0xdd, 0x0d, 0x69, 0x81,
          0xe9, 0x7e, 0x7a, 0xec, 0x1d, 0x43, 0x60, 0xc2, 0x0a, 0x27, 0xaf, 0xcc, 0xfd, 0x9f, 0xae, 0x0b,
          0xf9, 0x1b, 0x65, 0xc5, 0x52, 0x47, 0x33, 0xab, 0x8f, 0x59, 0x3d, 0xab, 0xcd, 0x62, 0xb3, 0x57,
          0x16, 0x39, 0xd6, 0x24, 0xe6, 0x51, 0x52, 0xab, 0x8f, 0x53, 0x0c, 0x35, 0x9f, 0x08, 0x61, 0xd8,
          0x07, 0xca, 0x0d, 0xbf, 0x50, 0x0d, 0x6a, 0x61, 0x56, 0xa3, 0x8e, 0x08, 0x8a, 0x22, 0xb6, 0x5e,
          0x52, 0xbc, 0x51, 0x4d, 0x16, 0xcc, 0xf8, 0x06, 0x81, 0x8c, 0xe9, 0x1a, 0xb7, 0x79, 0x37, 0x36,
          0x5a, 0xf9, 0x0b, 0xbf, 0x74, 0xa3, 0x5b, 0xe6, 0xb4, 0x0b, 0x8e, 0xed, 0xf2, 0x78, 0x5e, 0x42,
          0x87, 0x4d]
    r_ = bytearray(r_)
    assert r == r_

    # Test aus 2.5.2
    key = 0x85d6be7857556d337f4452fe42d506a80103808afb0db2fd4abff6af4149f51b.to_bytes(length=32, byteorder='big')
    text = 'Cryptographic Forum Research Group'

    s = calc_s(key)
    assert s == 0x1bf54941aff6bf4afdb20dfb8a800301

    r = calc_r(key)
    assert r == 0x85d6be7857556d337f4452fe42d506a8
    r = clamp(r)
    assert r == 0x806d5400e52447c036d555408bed685, 'clamping'

    r = poly1305_mac(text.encode(), key)
    r_ = [0xa8, 0x06, 0x1d, 0xc1, 0x30, 0x51, 0x36, 0xc6, 0xc2, 0x2b, 0x8b, 0xaf, 0x0c, 0x01, 0x27, 0xa9]
    r_ = bytearray(r_)
    assert r == r_

    # Test aus 2.6.2
    key = 0x808182838485868788898a8b8c8d8e8f909192939495969798999a9b9c9d9e9f.to_bytes(length=32, byteorder='big')
    nonce = 0x000000000001020304050607.to_bytes(length=12, byteorder='big')
    r_ = [0x8a, 0xd5, 0xa0, 0x8b, 0x90, 0x5f, 0x81, 0xcc, 0x81, 0x50, 0x40, 0x27, 0x4a, 0xb2, 0x94, 0x71, 0xa8, 0x33,
          0xb6, 0x37, 0xe3, 0xfd, 0x0d, 0xa5, 0x08, 0xdb, 0xb8, 0xe2, 0xfd, 0xd1, 0xa6, 0x46]
    r_ = bytes(r_)

    r = poly1305_key_gen(key, nonce)
    assert r == r_

    # Test aus 2.8.2
    plain_text = "Ladies and Gentlemen of the class of '99: If I could offer you only one tip for the future, sunscreen would be it.".encode()
    aad = 0x50515253c0c1c2c3c4c5c6c7.to_bytes(length=12, byteorder='big')
    key = 0x808182838485868788898a8b8c8d8e8f909192939495969798999a9b9c9d9e9f.to_bytes(length=32, byteorder='big')
    iv = 0x4041424344454647.to_bytes(length=8, byteorder='big')
    fixed = 0x07000000.to_bytes(length=4, byteorder='big')
    r_ = (
        bytes(
            [0xd3, 0x1a, 0x8d, 0x34, 0x64, 0x8e, 0x60, 0xdb, 0x7b, 0x86, 0xaf, 0xbc, 0x53, 0xef, 0x7e, 0xc2, 0xa4, 0xad,
             0xed, 0x51, 0x29, 0x6e, 0x08, 0xfe, 0xa9, 0xe2, 0xb5, 0xa7, 0x36, 0xee, 0x62, 0xd6, 0x3d, 0xbe, 0xa4, 0x5e,
             0x8c, 0xa9, 0x67, 0x12, 0x82, 0xfa, 0xfb, 0x69, 0xda, 0x92, 0x72, 0x8b, 0x1a, 0x71, 0xde, 0x0a, 0x9e, 0x06,
             0x0b, 0x29, 0x05, 0xd6, 0xa5, 0xb6, 0x7e, 0xcd, 0x3b, 0x36, 0x92, 0xdd, 0xbd, 0x7f, 0x2d, 0x77, 0x8b, 0x8c,
             0x98, 0x03, 0xae, 0xe3, 0x28, 0x09, 0x1b, 0x58, 0xfa, 0xb3, 0x24, 0xe4, 0xfa, 0xd6, 0x75, 0x94, 0x55, 0x85,
             0x80, 0x8b, 0x48, 0x31, 0xd7, 0xbc, 0x3f, 0xf4, 0xde, 0xf0, 0x8e, 0x4b, 0x7a, 0x9d, 0xe5, 0x76, 0xd2, 0x65,
             0x86, 0xce, 0xc6, 0x4b, 0x61, 0x16]),
        bytes([0x1a, 0xe1, 0x0b, 0x59, 0x4f, 0x09, 0xe2, 0x6a, 0x7e, 0x90, 0x2e, 0xcb, 0xd0, 0x60, 0x06, 0x91])
    )

    r = chacha20_aead_encrypt(aad, key, iv, fixed, plain_text)
    assert r[0] == r_[0], 'ciphertext'
    assert r[1] == r_[1], 'tag'

    assert chacha20_aead_verify_tag(aad, key, iv, fixed, r[0] + r[1])
    assert False == chacha20_aead_verify_tag(aad, key, iv, fixed, r[0] + r[1] + bytes([0, 1, 2, 3]))

    plain_text_ = chacha20_aead_decrypt(aad, key, iv, fixed, r[0] + r[1])
    assert plain_text == plain_text_

    assert False == chacha20_aead_decrypt(aad, key, iv, fixed, r[0] + r[1] + bytes([0, 1, 2, 3]))
