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


def chacha20_aead_encrypt(aad: bytes, key: bytes, iv: bytes, constant: bytes, plaintext: bytes):
    """
    The encrypt method for chacha20 aead as required by the Apple specification. The 96-bit nonce from RFC7539 is
    formed from the constant and the initialisation vector.

    :param aad: arbitrary length additional authenticated data
    :param key: 256-bit (32-byte) key of type bytes
    :param iv: the initialisation vector
    :param constant: constant
    :param plaintext: arbitrary length plaintext of type bytes or bytearray
    :return: the cipher text and tag
    """
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


def chacha20_aead_decrypt(aad: bytes, key: bytes, iv: bytes, constant: bytes, ciphertext: bytes):
    """
    The decrypt method for chacha20 aead as required by the Apple specification. The 96-bit nonce from RFC7539 is
    formed from the constant and the initialisation vector.

    :param aad: arbitrary length additional authenticated data
    :param key: 256-bit (32-byte) key of type bytes
    :param iv: the initialisation vector
    :param constant: constant
    :param ciphertext: arbitrary length plaintext of type bytes or bytearray
    :return: False if the tag could not be verified or the plaintext as bytes
    """
    assert type(ciphertext) in [bytes, bytearray], 'ciphertext is no instance of bytes: %s' % str(type(ciphertext))
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
