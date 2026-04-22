# Attic 服务
import pickle as pkl
from heurams.services.logger import get_logger
from heurams.context import config_var
from pathlib import Path
from heurams.services.hasher import get_md5
import atexit
from heurams.services import timer
from heurams.services.exceptions import WTFException
logger = get_logger(__name__)

def singleton(cls):
    instances = {}
    def get_instance(ident, default):
        key = ident
        if key not in instances:
            instances[key] = cls(ident)
        instances[key].patch_dict(default)
        return instances[key]
    return get_instance

atticdir = Path(config_var.get()['global']['paths']['misc']) / 'attics'
atticdir.mkdir(parents=True, exist_ok=True)

@singleton
class Attic:
    def __init__(self, ident, default:dict={}):
        self.ident = ident
        self.ident = self.ident.replace('<DAYSTAMP>', str(timer.get_daystamp()))
        self.ident = self.ident.replace('<TIMESTAMP>', str(timer.get_timestamp()))
        if '<' in ident or '>' in ident:
            raise WTFException
        #self.ident = get_md5(self.ident)
        self.pklpath = atticdir / f'{self.ident}.pkl'
        atexit.register(self.save)
        self.data = default
        if self.pklpath.exists():
            try:
                self.load()
                return
            except:
                self.pklpath.unlink(missing_ok=True)
        self.pklpath.touch(exist_ok=True)

    def patch_dict(self, dct):
        self.data.update({k: v for k, v in dct.items() if k not in self.data})

    def save(self):
        with open(atticdir / f'{self.ident}.pkl', 'wb') as f:
            pkl.dump(self.data, f)

    def load(self):
        with open(atticdir / f'{self.ident}.pkl', 'rb') as f:
            self.data.update(dict(pkl.load(f)))