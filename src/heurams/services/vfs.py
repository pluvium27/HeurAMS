"""vfs.py
得益于 FSSpec, 无需实现大部分虚拟文件系统的 Providers
"""

from pathlib import Path

import fsspec as fs


class VFSObject:
    def __init__(self, protocol, base_url):
        self.base_url = base_url
        self.protocol = protocol
        self.fs = fs.filesystem(protocol=protocol, base_url=base_url)

    def open(self, path: Path):
        return self.fs.open(path)

    def open_by_list(self, path_list: list[Path]):
        return self.fs.open_files(path_list)
