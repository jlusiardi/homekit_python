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
import math
import hashlib


class Srp:
    def __init__(self):
        # generator as defined by 3072bit group of RFC 5054
        self.g = int(b'5', 16)
        # modulus as defined by 3072bit group of RFC 5054
        self.n = int(b'''\
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
E0FD108E4B82D120A93AD2CAFFFFFFFFFFFFFFFF''', 16)
        # HomeKit requires SHA-512 (See page 36)
        self.h = hashlib.sha512
        self.A = None
        self.B = None
        self.salt = None
        self.username = None
        self.password = None

    @staticmethod
    def generate_private_key():
        """
        Static function to generate a 16 byte random key.

        :return: the key as an integer
        """
        private_key = crypt.mksalt(crypt.METHOD_SHA512)[3:].encode()
        return int.from_bytes(private_key, "big")

    def _calculate_k(self) -> int:
        # calculate k (see https://tools.ietf.org/html/rfc5054#section-2.5.3)
        hash_instance = self.h()
        n = Srp.to_byte_array(self.n)
        g = bytearray.fromhex((383 * '00' + '05'))  # 383 * b'0' + '5'.encode()
        hash_instance.update(n)
        hash_instance.update(g)
        k = int.from_bytes(hash_instance.digest(), "big")
        return k

    def _calculate_u(self) -> int:
        if self.A is None:
            raise RuntimeError('Client\'s public key is missing')
        if self.B is None:
            raise RuntimeError('Server\'s public key is missing')
        hash_instance = self.h()
        A_b = Srp.to_byte_array(self.A)
        B_b = Srp.to_byte_array(self.B)
        hash_instance.update(A_b)
        hash_instance.update(B_b)
        u = int.from_bytes(hash_instance.digest(), "big")
        return u

    def get_session_key(self) -> int:
        hash_instance = self.h()
        hash_instance.update(Srp.to_byte_array(self.get_shared_secret()))
        hash_value = int.from_bytes(hash_instance.digest(), "big")
        return hash_value

    @staticmethod
    def to_byte_array(num: int) -> bytearray:
        return bytearray(num.to_bytes(int(math.ceil(num.bit_length() / 8)), "big"))

    def _calculate_x(self) -> int:
        i = (self.username + ':' + self.password).encode()
        hash_instance = self.h()
        hash_instance.update(i)
        hash_value = hash_instance.digest()

        hash_instance = self.h()
        hash_instance.update(Srp.to_byte_array(self.salt))
        hash_instance.update(hash_value)

        return int.from_bytes(hash_instance.digest(), "big")

    def get_shared_secret(self):
        raise NotImplementedError()


class SrpClient(Srp):
    """
    Implements all functions that are required to simulate an iOS HomeKit controller
    """
    def __init__(self, username: str, password: str):
        Srp.__init__(self)
        self.username = username
        self.password = password
        self.salt = None
        self.a = self.generate_private_key()
        self.A = pow(self.g, self.a, self.n)
        self.B = None

    def set_salt(self, salt):
        if isinstance(salt, bytearray):
            self.salt = int.from_bytes(salt, "big")
        else:
            self.salt = salt

    def get_public_key(self):
        return pow(self.g, self.a, self.n)

    def set_server_public_key(self, B):
        if isinstance(B, bytearray):
            self.B = int.from_bytes(B, "big")
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
        return int.from_bytes(hash_instance.digest(), "big")

    def verify_servers_proof(self, M):
        if isinstance(M, bytearray):
            tmp = int.from_bytes(M, "big")
        else:
            tmp = M
        hash_instance = self.h()
        hash_instance.update(Srp.to_byte_array(self.A))
        hash_instance.update(Srp.to_byte_array(self.get_proof()))
        hash_instance.update(Srp.to_byte_array(self.get_session_key()))
        return tmp == int.from_bytes(hash_instance.digest(), "big")


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
        self.b = self.generate_private_key()
        k = self._calculate_k()
        g_b = pow(self.g, self.b, self.n)
        self.B = (k * self.verifier + g_b) % self.n
        self.A = None

    @staticmethod
    def _create_salt() -> int:
        # generate random salt
        salt = crypt.mksalt(crypt.METHOD_SHA512)[3:]
        assert len(salt) == 16
        salt_b = salt.encode()
        return int.from_bytes(salt_b, "big")

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
        return m == int.from_bytes(hash_instance.digest(), "big")

    def get_proof(self, m) -> int:
        hash_instance = self.h()
        hash_instance.update(Srp.to_byte_array(self.A))
        hash_instance.update(Srp.to_byte_array(m))
        hash_instance.update(Srp.to_byte_array(self.get_session_key()))
        return int.from_bytes(hash_instance.digest(), "big")
