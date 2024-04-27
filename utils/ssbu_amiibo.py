from amiibo import AmiiboDump
from amiibo.crypto import AmiiboBaseError
import copy

class InvalidAmiiboDump(AmiiboBaseError):
    pass

class IncorrectGameDataIdException(Exception):
    pass

class InvalidSsbuChecksum(Exception):
    pass

class SsbuAmiiboDump(AmiiboDump):
    """
    Class that's a thin wrapper around AmiiboDump.
    Checks the amiibo has the super smash bros game id in the game data section on unlock
    Writes the HMAC for the game data before locking
    """
    def __init__(self, master_keys, dump, is_locked=True):
        super().__init__(master_keys, dump, is_locked)
        self.dumpcopy = copy.deepcopy(self)
        if is_locked == True:
            self.dumpcopy.unlock()

    def unlock(self, verify=True):
        super().unlock(verify=verify)

        # Checks if the amiibo's game is Super Smash Bros. Ultimate, and if not, we initialize it.
        if bytes(self.data[266:270]).hex() != "34f80200":
            self.data[0x14] = self.data[0x14] | (1 << 5)
            self.data[266:270] = bytes.fromhex("34f80200")
            self.data[0x100:0x108] = bytes.fromhex('01006A803016E000')
            self.data[0x130:0x208] = bytes.fromhex("00" * 0xD8)
            self.data[304:308] = self._calculate_crc32(self.data[308:520]).to_bytes(4, "little")

        if self.data[304:308].hex() != self._calculate_crc32(self.data[308:520]).to_bytes(4, "little").hex():
            raise InvalidSsbuChecksum(f'The checksum for this game data is not correct. Please use an untampered amiibo')

    def lock(self):
        if self.data[444:502] != self.dumpcopy.data[444:502]:
            self.data[311] = self.data[311] | 1
            if self.amiibo_nickname[-1] != '□':
                if len(self.amiibo_nickname) == 10:
                    self.amiibo_nickname = self.amiibo_nickname[:-1] + '□'
                else:
                    self.amiibo_nickname = self.amiibo_nickname + '□'
        elif self.dumpcopy.amiibo_nickname[-1] == '□' and self.amiibo_nickname[-1] != '□':
            if len(self.amiibo_nickname) == 10:
                self.amiibo_nickname = self.amiibo_nickname[:-1] + '□'
            else:
                self.amiibo_nickname = self.amiibo_nickname + '□'
        checksum = self._calculate_crc32(self.data[308:520])
        mii_checksum = str(hex(self.crc16_ccitt_wii(self.data[0xA0:0xFE]))).lstrip('0x')
        while len(mii_checksum) < 4:
            mii_checksum = '0' + mii_checksum
        self.data[304:308] = checksum.to_bytes(4, "little")
        self.data[0xFE:0x100] = bytes.fromhex(mii_checksum)
        super().lock()

    @staticmethod
    def _calculate_crc32(input):
        # Setup CRC 32 table. Translated from js to python from amiibox codebase
        # (should move this out so it sets up once, but it's quick enough as is)
        p0 = 0xEDB88320 | 0x80000000
        p0 = p0 >> 0

        u0 = [0] * 0x100
        i = 1
        while (i & 0xFF):
            t0 = i
            for _ in range(8):
                b = (t0 & 0x1) >> 0
                t0 = (t0 >> 0x1) >> 0
                if b:
                    t0 = (t0 ^ p0) >> 0
            u0[i] = t0 >> 0
            i += 1

        # Calculate CRC32 from table
        t = 0x0
        for k in input:
            t = ((t >> 0x8) ^ u0[(k ^ t) & 0xFF]) >> 0
        return (t ^ 0xFFFFFFFF) >> 0

    def crc16_ccitt_wii(self, data):
        crc = 0

        for byte in data:
            byte = int.from_bytes([byte], 'big')

            crc = crc ^ (byte << 8)

            for _ in range(8):
                crc = crc << 1

                if (crc & 0x10000) > 0:
                    crc ^= 0x1021

        return (crc & 0xFFFF)


    @property
    def amiibo_nickname(self):
        # TODO: why is the Amiibo nickname big endian,
        # but the Mii nickname litle endian?
        return self.data[0x020:0x034].decode('utf-16-be').rstrip('\x00')

    @amiibo_nickname.setter
    def amiibo_nickname(self, name):
        utf16 = name.encode('utf-16-be')
        if len(utf16) > 20:
            raise ValueError
        self.data[0x020:0x034] = utf16.ljust(20, b'\x00')
