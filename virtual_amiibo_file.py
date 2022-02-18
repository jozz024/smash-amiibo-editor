from amiibo import AmiiboMasterKey, cli
from ssbu_amiibo import SsbuAmiiboDump as AmiiboDump
from os.path import exists
import random


class VirtualAmiiboFile:
    def __init__(self, binfp, keyfp=None):
        if keyfp is not None:
            try:
                with open(keyfp, 'rb') as fp_j:
                    self.master_keys = AmiiboMasterKey.from_combined_bin(
                        fp_j.read())
            except:
                with open(keyfp[0], 'rb') as fp_d, \
                        open(keyfp[1], 'rb') as fp_t:
                    self.master_keys = AmiiboMasterKey.from_separate_bin(
                        fp_d.read(), fp_t.read())
        else:
            if exists(r"resources/key_retail.bin"):
                with open(r"resources/key_retail.bin", 'rb') as fp_j:
                    self.master_keys = AmiiboMasterKey.from_combined_bin(
                        fp_j.read())
            else:
                with open(r"resources/unfixed-info.bin", 'rb') as fp_d, \
                        open(r"resources/locked-secret.bin", 'rb') as fp_t:
                    self.master_keys = AmiiboMasterKey.from_separate_bin(
                        fp_d.read(), fp_t.read())

        self.dump = self.__open_bin(binfp)
        self.dump.unlock()
        self.dump.data = cli.dump_to_amiitools(self.dump.data)

    def __open_bin(self, bin_location):
        """
        Opens a bin and makes it 540 bytes if it wasn't
        :param bin_location: file location of bin you want to open
        :return: opened bin
        """
        bin_fp = open(bin_location, 'rb')

        bin_dump = bytes()
        for line in bin_fp:
            bin_dump += line
        bin_fp.close()

        if len(bin_dump) == 540:
            with open(bin_location, 'rb') as fp:
                dump = AmiiboDump(self.master_keys, fp.read())
                return dump
        elif 532 <= len(bin_dump) <= 572:
            while len(bin_dump) < 540:
                bin_dump += b'\x00'
            if len(bin_dump) > 540:
                bin_dump = bin_dump[:-(len(bin_dump) - 540)]
            b = open(bin_location, 'wb')
            b.write(bin_dump)
            b.close()

            with open(bin_location, 'rb') as fp:
                dump = AmiiboDump(self.master_keys, fp.read())
                return dump
        else:
            return None

    def save_bin(self, location):
        with open(location, 'wb') as fp:
            self.dump.data = cli.amiitools_to_dump(self.dump.data)
            self.dump.lock()
            fp.write(self.dump.data)
            # virtual amiibo file assumes dump is unlocked and in amiitools format
            self.dump.unlock()
            self.dump.data = cli.dump_to_amiitools(self.dump.data)

    def edit_bin(self, offset, bit_index, number_of_bits, value):
        hexdata = self.dump.data[offset]
        number = bin(hexdata)
        # clears bit
        number = int(number, 2) & ~(2 ** number_of_bits - 1 << 7 - bit_index)
        # sets bit
        self.dump.data[offset] = number | (int(value, 2) << 7 - bit_index)

    def get_bytes(self, start_index, end_index=None):
        """
        Gets bytes from locations requested

        :param start_index: starting index
        :param end_index: ending index
        :return: byte or bytes requested
        """
        if end_index is not None:
            return self.dump.data[start_index:end_index]
        else:
            return self.dump.data[start_index]

    def get_bits(self, byte_index, bit_index, number_of_bits):
        output = ""
        i = bit_index
        while len(output) != number_of_bits:
            # 2: slice is to get rid of 0b
            output += format(self.dump.data[byte_index], '#010b')[2:][7 - i]

            i -= 1
            if i == -1:
                i = 7
                byte_index += 1
        return int(output, 2)

    def set_bytes(self, start_index, value):
        for i, byte in enumerate(value):
            self.dump.data[start_index+i] = byte

    def set_bits(self, byte_index, bit_index, number_of_bits, value):
        pass

    def get_data(self):
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
