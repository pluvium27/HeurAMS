from heurams.services.logger import get_logger

logger = get_logger(__name__)

class Nucleon:
    """原子核: 带有运行时隔离的半只读材料元数据容器
    """

    def __init__(self, ident, payload, common):
        self.ident = ident
        self.payload = payload
        self.common = common
        self.rtlayer = dict() # 运行时层

    def __getitem__(self, key):
        if key == "ident":
            return self.ident
        merged = self.rtlayer | self.payload | self.common
        return merged[key]
            
    def __setitem__(self, key, value):
        if key == "ident":
            raise AttributeError("ident 应为只读")
        else:
            self.rtlayer[key] = value

    def __delitem__(self, key):
        raise AttributeError("Nucleon 包含的数据被设计为无法删除")

    def __iter__(self):
        merged = self.rtlayer | self.payload | self.common
        return iter(merged)

    def __contains__(self, key):
        return key in (self.rtlayer | self.payload | self.common)
    
    def get(self, key, default=None):
        if key in self:
            return self[key]
        return default
    
    def __len__(self):
        return len(self.rtlayer | self.payload | self.common)

    def __repr__(self):
        return f"""RUNTIME:{repr(self.rtlayer)}
        PAYLOAD:{repr(self.payload)}
        COMMON:{repr(self.common)}"""

    @staticmethod
    def create_on_nucleonic_data(nucleonic_data: tuple):
        _data = nucleonic_data
        payload = _data[1][0]
        common = _data[1][1]
        ident = _data[0] #TODO:实现eval
        return Nucleon(ident, payload, common)