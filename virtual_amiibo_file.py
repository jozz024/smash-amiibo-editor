from amiibo import AmiiboMasterKey
from ssbu_amiibo import SsbuAmiiboDump as AmiiboDump
import random

class VirtualAmiiboFile:
    def __init__(self, binfp, keyfp):
        try:
            with open(keyfp, 'rb') as fp_j:
                self.master_keys = AmiiboMasterKey.from_combined_bin(
                    fp_j.read())
        except FileNotFoundError:
            print('key path not found')
            exit()
        self.dump = self.__open_bin(binfp) 
        self.dump.unlock()


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
                self.dump.lock()
                fp.write(self.dump.data)

    def edit_bin(self, offset, bit_index, number_of_bits, value):
        hexdata = self.dump.data[offset]
        number = bin(hexdata)
        # clears bit
        number = int(number, 2) & ~(2**number_of_bits-1 << 7-bit_index)
        # sets bit
        self.dump.data[offset] = number | (int(value, 2) << 7-bit_index)

    def getdata(self):
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
        # if unlocked, keep it unlocked, otherwise unlock and lock
        self.dump.uid_hex = serial_number

