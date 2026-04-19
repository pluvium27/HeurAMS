from heurams.services.config import ConfigDict
from heurams.services.logger import get_logger

logger = get_logger(__name__)
def epath(dct, path: str = '', default=None, parents=False):
    if not path:
        return dct
    
    path = path.rstrip('.')
    path = path.lstrip('.')
    target = dct
    
    for i in path.split('.'):
        # 处理字典键
        logger.debug(f'处理 {i}, {(isinstance(target, dict) or isinstance(target, ConfigDict))} {i in target}')
        if (isinstance(target, dict) or isinstance(target, ConfigDict)) and i in target:
            target = target[i]
        # 处理列表索引
        elif i.startswith('[') and i.endswith(']') and isinstance(target, (list, tuple)):
            idx = int(i[1:-1])
            if 0 <= idx < len(target):
                target = target[idx]
            elif parents:
                while len(target) <= idx:
                    target.append(None)
                target[idx] = {}
                target = target[idx]
            else:
                return default
        elif parents:
            target[i] = {}
            target = target[i]
        else:
            return default
    
    return target