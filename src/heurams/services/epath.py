from heurams.services.config import ConfigDict
from heurams.services.logger import get_logger

logger = get_logger(__name__)

def epath(dct, path: str = '', default=None, parents=False, enable_modify=False, new_value=None):
    if not path:
        return dct
    
    path = path.rstrip('.')
    path = path.lstrip('.')
    target = dct
    keys = path.split('.')
    logger.debug(f"处理 EPATH {path}, {new_value}")
    for idx, i in enumerate(keys):
        is_last = (idx == len(keys) - 1)
        
        # 处理字典键
        logger.debug(f'处理 {i}, {(isinstance(target, dict) or isinstance(target, ConfigDict))} {i in target}')
        
        if is_last and enable_modify:
            # 最后一次循环执行修改
            if (isinstance(target, dict) or isinstance(target, ConfigDict)):
                target[i] = new_value
                return new_value
            elif i.startswith('[') and i.endswith(']') and isinstance(target, (list, tuple)):
                idx_num = int(i[1:-1])
                if 0 <= idx_num < len(target):
                    target[idx_num] = new_value
                    return new_value
                elif parents:
                    while len(target) <= idx_num:
                        target.append(None)
                    target[idx_num] = new_value
                    return new_value
                else:
                    return default
            else:
                return default
        else:
            if (isinstance(target, dict) or isinstance(target, ConfigDict)) and i in target:
                target = target[i]
            elif i.startswith('[') and i.endswith(']') and isinstance(target, (list, tuple)):
                idx_num = int(i[1:-1])
                if 0 <= idx_num < len(target):
                    target = target[idx_num]
                elif parents:
                    while len(target) <= idx_num:
                        target.append(None)
                    target[idx_num] = {}
                    target = target[idx_num]
                else:
                    return default
            elif parents:
                target[i] = {}
                target = target[i]
            else:
                return default
    
    return target