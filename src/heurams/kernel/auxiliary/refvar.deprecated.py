# 已弃用
class RefVar:
    def __init__(self, initvalue) -> None:
        self.data = initvalue

    def __repr__(self) -> str:
        return f"RefVar({repr(self.data)})"

    def __str__(self) -> str:
        return str(self.data)

    def __add__(self, other):
        if isinstance(other, RefVar):
            return RefVar(self.data + other.data)
        return RefVar(self.data + other)

    def __radd__(self, other):
        return RefVar(other + self.data)

    def __sub__(self, other):
        if isinstance(other, RefVar):
            return RefVar(self.data - other.data)
        return RefVar(self.data - other)

    def __rsub__(self, other):
        return RefVar(other - self.data)

    def __mul__(self, other):
        if isinstance(other, RefVar):
            return RefVar(self.data * other.data)
        return RefVar(self.data * other)

    def __rmul__(self, other):
        return RefVar(other * self.data)

    def __truediv__(self, other):
        if isinstance(other, RefVar):
            return RefVar(self.data / other.data)
        return RefVar(self.data / other)

    def __rtruediv__(self, other):
        return RefVar(other / self.data)

    def __floordiv__(self, other):
        if isinstance(other, RefVar):
            return RefVar(self.data // other.data)
        return RefVar(self.data // other)

    def __rfloordiv__(self, other):
        return RefVar(other // self.data)

    def __mod__(self, other):
        if isinstance(other, RefVar):
            return RefVar(self.data % other.data)
        return RefVar(self.data % other)

    def __rmod__(self, other):
        return RefVar(other % self.data)

    def __pow__(self, other):
        if isinstance(other, RefVar):
            return RefVar(self.data**other.data)
        return RefVar(self.data**other)

    def __rpow__(self, other):
        return RefVar(other**self.data)

    def __neg__(self):
        return RefVar(-self.data)

    def __pos__(self):
        return RefVar(+self.data)

    def __abs__(self):
        return RefVar(abs(self.data))

    def __eq__(self, other):
        if isinstance(other, RefVar):
            return self.data == other.data
        return self.data == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if isinstance(other, RefVar):
            return self.data < other.data
        return self.data < other

    def __le__(self, other):
        if isinstance(other, RefVar):
            return self.data <= other.data
        return self.data <= other

    def __gt__(self, other):
        if isinstance(other, RefVar):
            return self.data > other.data
        return self.data > other

    def __ge__(self, other):
        if isinstance(other, RefVar):
            return self.data >= other.data
        return self.data >= other

    # 位运算
    def __and__(self, other):
        if isinstance(other, RefVar):
            return RefVar(self.data & other.data)
        return RefVar(self.data & other)

    def __rand__(self, other):
        return RefVar(other & self.data)

    def __or__(self, other):
        if isinstance(other, RefVar):
            return RefVar(self.data | other.data)
        return RefVar(self.data | other)

    def __ror__(self, other):
        return RefVar(other | self.data)

    def __xor__(self, other):
        if isinstance(other, RefVar):
            return RefVar(self.data ^ other.data)
        return RefVar(self.data ^ other)

    def __rxor__(self, other):
        return RefVar(other ^ self.data)

    def __lshift__(self, other):
        if isinstance(other, RefVar):
            return RefVar(self.data << other.data)
        return RefVar(self.data << other)

    def __rlshift__(self, other):
        return RefVar(other << self.data)

    def __rshift__(self, other):
        if isinstance(other, RefVar):
            return RefVar(self.data >> other.data)
        return RefVar(self.data >> other)

    def __rrshift__(self, other):
        return RefVar(other >> self.data)

    def __invert__(self):
        return RefVar(~self.data)

    # 类型转换
    def __int__(self):
        return int(self.data)

    def __float__(self):
        return float(self.data)

    def __bool__(self):
        return bool(self.data)

    def __complex__(self):
        return complex(self.data)

    def __bytes__(self):
        return bytes(self.data)

    def __hash__(self):
        return hash(self.data)

    # 容器操作（如果底层数据支持）
    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def __contains__(self, item):
        return item in self.data

    def __iter__(self):
        return iter(self.data)

    def __iadd__(self, other):
        if isinstance(other, RefVar):
            self.data += other.data
        else:
            self.data += other
        return self

    def __isub__(self, other):
        if isinstance(other, RefVar):
            self.data -= other.data
        else:
            self.data -= other
        return self

    def __imul__(self, other):
        if isinstance(other, RefVar):
            self.data *= other.data
        else:
            self.data *= other
        return self

    def __itruediv__(self, other):
        if isinstance(other, RefVar):
            self.data /= other.data
        else:
            self.data /= other
        return self

    def __ifloordiv__(self, other):
        if isinstance(other, RefVar):
            self.data //= other.data
        else:
            self.data //= other
        return self

    def __imod__(self, other):
        if isinstance(other, RefVar):
            self.data %= other.data
        else:
            self.data %= other
        return self

    def __ipow__(self, other):
        if isinstance(other, RefVar):
            self.data **= other.data
        else:
            self.data **= other
        return self

    def __call__(self, *args, **kwargs):
        if callable(self.data):
            return self.data(*args, **kwargs)
        raise TypeError(f"'{type(self.data).__name__}' object is not callable")

    def __getattr__(self, name):
        return getattr(self.data, name)
