class Base():
    def __init__(self, start_location, length, name, description):
        self.start_location = start_location
        self.length = length
        self.name = name
        self.description = description
        
class u8(Base):
    pass

class u16(Base):
    pass

class bits(Base):
    pass

class ENUM(Base):
    def __init__(self, start_location, length, name, description, options):
        super().__init__(start_location, length, name, description)
        self.options = options


