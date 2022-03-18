from amiibo import AmiiboMasterKey, cli
from amiibo.crypto import AmiiboHMACTagError, AmiiboHMACDataError
from ssbu_amiibo import SsbuAmiiboDump as AmiiboDump
from ssbu_amiibo import InvalidAmiiboDump
import random
import personality

class VirtualAmiiboFile:
    """
    Class that represents an amiibo bin file
    """
    def __init__(self, binfp, keyfp, verify=True):
        """
        Initializes the class

        :param str binfp: filepath to bin to open
        :param str keyfp: filepath to keys/key
        """
        try:
            with open(keyfp, 'rb') as fp_j:
                self.master_keys = AmiiboMasterKey.from_combined_bin(
                    fp_j.read())
        except TypeError:
            with open(keyfp[0], 'rb') as fp_d, \
                    open(keyfp[1], 'rb') as fp_t:
                self.master_keys = AmiiboMasterKey.from_separate_bin(
                    fp_d.read(), fp_t.read())
        self.dump = self.__open_bin(binfp, verify)
        if verify == True:
            self.dump.unlock()
        self.dump.data = cli.dump_to_amiitools(self.dump.data)

    def __open_bin(self, bin_location, verify=True):
        """
        Opens a bin and makes it 540 bytes if it wasn't

        :param str bin_location: file location of bin you want to open
        :return: opened bin
        """
        bin_fp = open(bin_location, 'rb')

        bin_dump = bytes()
        for line in bin_fp:
            bin_dump += line
        bin_fp.close()

        if len(bin_dump) == 540:
            with open(bin_location, 'rb') as fp:
                dump = AmiiboDump(self.master_keys, fp.read(), verify)
                return dump
        # if bin isn't 540 bytes, set it to that
        elif 532 <= len(bin_dump) <= 572:
            while len(bin_dump) < 540:
                bin_dump += b'\x00'
            if len(bin_dump) > 540:
                bin_dump = bin_dump[:-(len(bin_dump) - 540)]
            b = open(bin_location, 'wb')
            b.write(bin_dump)
            b.close()

            with open(bin_location, 'rb') as fp:
                dump = AmiiboDump(self.master_keys, fp.read(), verify)
                return dump
        else:
            raise InvalidAmiiboDump

    def save_bin(self, location):
        """
        Saves current bin to location

        :param str location: file location to save bin
        :return: None
        """
        with open(location, 'wb') as fp:
            self.dump.data = cli.amiitools_to_dump(self.dump.data)
            self.dump.lock()
            fp.write(self.dump.data)
            # virtual amiibo file assumes dump is unlocked and in amiitools format
            self.dump.unlock()
            self.dump.data = cli.dump_to_amiitools(self.dump.data)

    def get_bytes(self, start_index, end_index=None):
        """
        Gets bytes from locations requested

        :param int start_index: starting index
        :param int end_index: ending index
        :return: byte or bytes requested
        """
        if end_index is not None:
            return self.dump.data[start_index:end_index]
        else:
            return self.dump.data[start_index]

    def get_bits(self, byte_index, bit_index, number_of_bits, reverse=False):
        """
        Gets requested bits from bin

        :param int byte_index: starting byte index
        :param int bit_index: starting bit index #least sig bit if reverse is True
        :param int number_of_bits: length of request
        :param bool reverse: If true, then it is read in big endian
        :return: bits requested as int
        """
        output = ""

        i = bit_index
        while len(output) != number_of_bits:
            # 2: slice is to get rid of 0b
            output += format(self.dump.data[byte_index], '#010b')[2:][i]
            if reverse:
                i -= 1
            else:
                i += 1
            if i == 8 or i == -1:
                if reverse:
                    i = 7
                else:
                    i = 0
                byte_index += 1
        if reverse:
            # reverse string
            output = output[::-1]
        return int(output, 2)

    def set_bytes(self, start_index, value):
        """
        Sets bytes starting at start_index using values from value

        :param int start_index: Starting location in bin to set bytes at
        :param List[int] value: values to be used for setting
        :return: None
        """
        for i, byte in enumerate(value):
            self.dump.data[start_index+i] = byte

    def set_bits(self, byte_index, bit_index, number_of_bits, value, reverse=False):
        """
        Sets bits in bin using value

        :param int byte_index: starting byte index
        :param int bit_index: starting bit index #least sig bit if reverse is True
        :param int number_of_bits: length of request
        :param int value: value to be used to set
        :param bool reverse: If true, then it is set as big endian
        :return: None
        """
        # 2: and +2 account for 0b included
        value = format(value, f'#0{number_of_bits+2}b')[2:]

        i = bit_index
        # 2: slice is to get rid of 0b
        bit_array = list(format(self.dump.data[byte_index], '#010b')[2:])
        # better ways to set bits probably exist
        while value != "":
            if reverse:
                bit_array[i] = value[-1]

                value = value[:-1]
                i -= 1
            else:
                bit_array[i] = value[0]

                value = value[1:]
                i += 1
            if i == 8 or i == -1:
                self.dump.data[byte_index] = int(''.join(bit_array), 2)
                if reverse:
                    i = 7
                else:
                    i = 0
                byte_index += 1

                bit_array = list(format(self.dump.data[byte_index], '#010b')[2:])
            # to catch case when it doesn't end on byte border
            elif value == "":
                self.dump.data[byte_index] = int(''.join(bit_array), 2)

    def get_data(self):
        """
        Returns bin file data

        :return: bytearray of bin file
        """
        return self.dump.data

    def randomize_sn(self):
        """
        Randomizes the serial number of a given bin dump

        :return: None
        """
        serial_number = "04"
        while len(serial_number) < 20:
            temp_sn = hex(random.randint(0, 255))
            # removes 0x prefix
            temp_sn = temp_sn[2:]
            # creates leading zero
            if len(temp_sn) == 1:
                temp_sn = '0' + temp_sn
            serial_number += ' ' + temp_sn
        # current SN function uses positions from pyamiibo dump, not amiitools
        self.dump.data = cli.amiitools_to_dump(self.dump.data)
        self.dump.uid_hex = serial_number
        self.dump.data = cli.dump_to_amiitools(self.dump.data)

    def get_personality(self):
        self.dump.data = cli.amiitools_to_dump(self.dump.data)
        params = personality.decode_behavior_params(self.dump)
        actual_personality = personality.calculate_personality_from_data(params)
        self.dump.data = cli.dump_to_amiitools(self.dump.data)

        return actual_personality
