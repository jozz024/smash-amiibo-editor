from itertools import chain


class ImplicitSumManager:
    def __init__(self, implicit_sums, sections):
        self.implicit_sums = []
        self.connections = {}
        if implicit_sums is not None:
            for implicit_sum in implicit_sums:
                self.add_implicit_sum(implicit_sum, sections)

    def add_implicit_sum(self, implicit_sum, sections):
        counterparts = []
        counterpart_sigs = implicit_sum.get_counterpart_signatures()
        for section in sections:
            if section.get_signature() in counterpart_sigs:
                counterparts.append(section)

        self.connections[implicit_sum.get_name()] = counterparts
        self.implicit_sums.append(implicit_sum)

    def __get_keys(self, implicit_sum_name):
        if len(self.implicit_sums) != 0:
            key_list = []
            for section in self.connections[implicit_sum_name]:
                key_list.append(section.get_keys())

            # unnest lists
            return list(chain.from_iterable(key_list))
        return None

    def update(self, event, window, amiibo, sections):
        if len(self.implicit_sums) != 0:
            if event == "LOAD_AMIIBO" or event == "Open (CTRL+O)" or event == "Load (CTRL+L)":
                for implicit_sum in self.implicit_sums:
                    value = 100
                    for section in self.connections[implicit_sum.get_name()]:
                        value -= section.get_value_from_bin(amiibo)
                    # fix rounding
                    value = round(value, 5)
                    if -.01 < value < .01:
                        value = 0
                    implicit_sum.update(event, window, amiibo, value)
            else:
                for implicit_sum_name in self.connections:
                    if event in self.__get_keys(implicit_sum_name):
                        value = 100
                        for section in self.connections[implicit_sum_name]:
                            value -= section.get_value_from_bin(amiibo)
                        # fix rounding
                        value = round(value, 5)
                        if -.01 < value < .01:
                            value = 0
                        for implicit_sum in self.implicit_sums:
                            if implicit_sum.get_name() == implicit_sum_name:
                                implicit_sum.update(event, window, amiibo, value)
