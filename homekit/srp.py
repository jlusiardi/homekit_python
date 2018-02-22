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
Implements the Secure Remote Password (SRP) algorithm. More information can be found on
https://tools.ietf.org/html/rfc5054. See HomeKit spec page 36 for adjustments imposed by Apple.
"""

import crypt
import gmpy2
import hashlib

import six
import binascii


class Srp:
    def __init__(self):
        # generator as defined by 3072bit group of RFC 5054
        self.g = gmpy2.mpz(int(six.b('5'), 16))
        # modulus as defined by 3072bit group of RFC 5054
        self.n = gmpy2.mpz(int(six.b('''\
FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E08\
8A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B\
302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9\
A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE6\
49286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8\
FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D\
670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C\
180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF695581718\
3995497CEA956AE515D2261898FA051015728E5A8AAAC42DAD33170D\
04507A33A85521ABDF1CBA64ECFB850458DBEF0A8AEA71575D060C7D\
B3970F85A6E1E4C7ABF5AE8CDB0933D71E8C94E04A25619DCEE3D226\
1AD2EE6BF12FFA06D98A0864D87602733EC86A64521F2B18177B200C\
BBE117577A615D6C770988C0BAD946E208E24FA074E5AB3143DB5BFC\
E0FD108E4B82D120A93AD2CAFFFFFFFFFFFFFFFF'''), 16))
        # HomeKit requires SHA-512 (See page 36)
        self.h = hashlib.sha512

    def _calculate_k(self) -> gmpy2.mpz:
        # calculate k (see https://tools.ietf.org/html/rfc5054#section-2.5.3)
        hash_instance = self.h()
        n = Srp.to_byte_array(self.n)
        g = bytearray.fromhex((383 * '00' + '05'))  # 383 * b'0' + '5'.encode()
        hash_instance.update(n)
        hash_instance.update(g)
        k = gmpy2.mpz(int(binascii.hexlify(hash_instance.digest()), 16))
        return k

    def _calculate_u(self) -> gmpy2.mpz:
        if self.A is None:
            raise RuntimeError('Client\'s public key is missing')
        if self.B is None:
            raise RuntimeError('Server\'s public key is missing')
        hash_instance = self.h()
        A_b = Srp.to_byte_array(self.A)
        B_b = Srp.to_byte_array(self.B)
        hash_instance.update(A_b)
        hash_instance.update(B_b)
        u = gmpy2.mpz(int(binascii.hexlify(hash_instance.digest()), 16))
        return u

    def get_session_key(self) -> int:
        hash_instance = self.h()
        hash_instance.update(Srp.to_byte_array(self.get_shared_secret()))
        hash_value = int(binascii.hexlify(hash_instance.digest()), 16)
        return hash_value

    @staticmethod
    def to_byte_array(num: int) -> bytearray:
        h = gmpy2.digits(num, 16)
        if len(h) % 2 == 1:
            h = '0' + h
        return bytearray.fromhex(h)

    def _calculate_x(self) -> int:
        i = (self.username + ':' + self.password).encode()
        hash_instance = self.h()
        hash_instance.update(i)
        hash_value = hash_instance.digest()

        hash_instance = self.h()
        hash_instance.update(Srp.to_byte_array(self.salt))
        hash_instance.update(hash_value)

        return int(binascii.hexlify(hash_instance.digest()), 16)


class SrpClient(Srp):
    """
    Implements all functions that are required to simulate an iOS HomeKit controller
    """
    def __init__(self, username: str, password: str):
        Srp.__init__(self)
        self.username = username
        self.password = password
        self.salt = None
        self.a = gmpy2.mpz(int(binascii.hexlify(crypt.mksalt(crypt.METHOD_SHA512)[3:].encode()), 16))
        self.A = pow(self.g, self.a, self.n)
        self.B = None

    def set_salt(self, salt):
        if isinstance(salt, bytearray):
            self.salt = gmpy2.mpz(salt.hex(), 16)
        else:
            self.salt = salt

    def get_public_key(self) -> gmpy2.mpz:
        return pow(self.g, self.a, self.n)

    def set_server_public_key(self, B):
        if isinstance(B, bytearray):
            self.B = gmpy2.mpz(B.hex(), 16)
        else:
            self.B = B

    def get_shared_secret(self):
        if self.B is None:
            raise RuntimeError('Server\'s public key is missing')
        u = self._calculate_u()
        x = self._calculate_x()
        k = self._calculate_k()
        tmp1 = (self.B - (k * pow(self.g, x, self.n)))
        tmp2 = (self.a + (u * x))  # % self.n
        S = pow(tmp1, tmp2, self.n)
        return S

    def get_proof(self):
        if self.B is None:
            raise RuntimeError('Server\'s public key is missing')

        hash_instance = self.h()
        hash_instance.update(Srp.to_byte_array(self.n))
        hN = bytearray(hash_instance.digest())

        hash_instance = self.h()
        hash_instance.update(Srp.to_byte_array(self.g))
        hg = bytearray(hash_instance.digest())

        for index in range(0, len(hN)):
            hN[index] ^= hg[index]

        u = self.username.encode()
        hash_instance = self.h()
        hash_instance.update(u)
        hu = hash_instance.digest()
        K = Srp.to_byte_array(self.get_session_key())

        hash_instance = self.h()
        hash_instance.update(hN)
        hash_instance.update(hu)
        hash_instance.update(Srp.to_byte_array(self.salt))
        hash_instance.update(Srp.to_byte_array(self.A))
        hash_instance.update(Srp.to_byte_array(self.B))
        hash_instance.update(K)
        r = binascii.hexlify(hash_instance.digest())
        return int(r, 16)

    def verify_servers_proof(self, M):
        if isinstance(M, bytearray):
            tmp = gmpy2.mpz(M.hex(), 16)
        else:
            tmp = M
        hash_instance = self.h()
        hash_instance.update(Srp.to_byte_array(self.A))
        hash_instance.update(Srp.to_byte_array(self.get_proof()))
        hash_instance.update(Srp.to_byte_array(self.get_session_key()))
        return tmp == gmpy2.mpz(binascii.hexlify(hash_instance.digest()), 16)


class SrpServer(Srp):
    """
    Implements all functions that are required to simulate an iOS HomeKit accessory
    """
    def __init__(self, username, password):
        Srp.__init__(self)
        self.username = username
        self.salt = SrpServer._create_salt()
        self.password = password
        self.verifier = self._get_verifier()
        salt = crypt.mksalt(crypt.METHOD_SHA256)[3:].encode()
        salt_b = binascii.hexlify(salt)
        self.b = gmpy2.mpz(int(salt_b, 16))
        k = self._calculate_k()
        g_b = pow(self.g, self.b, self.n)
        self.B = (k * self.verifier + g_b) % self.n

        self.A = None

    @staticmethod
    def _create_salt() -> gmpy2.mpz:
        salt = crypt.mksalt(crypt.METHOD_SHA512)[3:]
        salt_b = salt.encode()
        salt_hex = binascii.hexlify(salt_b)
        salt_int = int(salt_hex, 16)
        assert len(salt) == 16
        return gmpy2.mpz(salt_int)

    def _get_verifier(self) -> int:
        hash_value = self._calculate_x()
        v = pow(self.g, hash_value, self.n)
        return v

    def set_client_public_key(self, A):
        self.A = A

    def get_salt(self):
        return self.salt

    def get_public_key(self):
        k = self._calculate_k()
        return (k * self.verifier + pow(self.g, self.b, self.n)) % self.n

    def get_shared_secret(self):
        if self.A is None:
            raise RuntimeError('Client\'s public key is missing')

        tmp1 = self.A * pow(self.verifier, self._calculate_u(), self.n)
        return pow(tmp1, self.b, self.n)

    def verify_clients_proof(self, m) -> bool:
        if self.B is None:
            raise RuntimeError('Server\'s public key is missing')

        hash_instance = self.h()
        hash_instance.update(Srp.to_byte_array(self.n))
        hN = bytearray(hash_instance.digest())

        hash_instance = self.h()
        hash_instance.update(Srp.to_byte_array(self.g))
        hg = bytearray(hash_instance.digest())

        for index in range(0, len(hN)):
            hN[index] ^= hg[index]

        u = self.username.encode()
        hash_instance = self.h()
        hash_instance.update(u)
        hu = hash_instance.digest()
        K = Srp.to_byte_array(self.get_session_key())

        hash_instance = self.h()
        hash_instance.update(hN)
        hash_instance.update(hu)
        hash_instance.update(Srp.to_byte_array(self.salt))
        hash_instance.update(Srp.to_byte_array(self.A))
        hash_instance.update(Srp.to_byte_array(self.B))
        hash_instance.update(K)
        r = binascii.hexlify(hash_instance.digest())
        return m == gmpy2.mpz(r, 16)

    def get_proof(self, m) -> gmpy2.mpz:
        hash_instance = self.h()
        hash_instance.update(Srp.to_byte_array(self.A))
        hash_instance.update(Srp.to_byte_array(m))
        hash_instance.update(Srp.to_byte_array(self.get_session_key()))
        return gmpy2.mpz(binascii.hexlify(hash_instance.digest()), 16)


if __name__ == '__main__':
    # step M1

    # step M2
    setup_code = '123-45-678'  # transmitted on second channel
    server = SrpServer('Pair-Setup', setup_code)
    server_pub_key = server.get_public_key()
    server_salt = server.get_salt()

    # step M3
    client = SrpClient('Pair-Setup', setup_code)
    client.set_salt(server_salt)
    client.set_server_public_key(server_pub_key)

    client_pub_key = client.get_public_key()
    clients_proof = client.get_proof()

    # step M4
    server.set_client_public_key(client_pub_key)
    server_shared_secret = server.get_shared_secret()
    assert server.verify_clients_proof(clients_proof)
    servers_proof = server.get_proof(clients_proof)

    # step M5
    assert client.verify_servers_proof(servers_proof)
