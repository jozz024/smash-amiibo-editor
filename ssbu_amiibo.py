from amiibo import AmiiboDump
import copy

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
        self.dumpcopy.unlock()

    def unlock(self, verify=True):
        super().unlock(verify=verify)

        if bytes(self.data[266:270]).hex() != "34f80200":
            raise IncorrectGameDataIdException(
                f'This bins game data id {self.data[266:270].hex()} does not match Super Smash Bros Ultimate game id 34f80200\n' \
                f'Please initialize this amiibo in Super Smash Bros Ultimate first')

        if self.data[304:308].hex() != self._calculate_crc32(self.data[308:520]).to_bytes(4, "little").hex():
            raise InvalidSsbuChecksum(f'The checksum for this game data is not correct. Please use an untampered amiibo')

    def lock(self):
        if self.data[444:502] != self.dumpcopy.data[444:502]:
            self.data[311] = self.data[311] | 1
            if len(self.amiibo_nickname) == 10:
                self.amiibo_nickname = self.amiibo_nickname[:-1] + '□'
            else:
                self.amiibo_nickname = self.amiibo_nickname + '□'
        checksum = self._calculate_crc32(self.data[308:520])
        self.data[304:308] = checksum.to_bytes(4, "little")
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