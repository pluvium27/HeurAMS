import heurams.kernel.repolib as repolib
import heurams.kernel.particles as pt
from heurams.services.textproc import truncate
from pathlib import Path
import time
repo = repolib.Repo.create_from_repodir(Path("./test_repo"))
alist = list()
print(repo.ident_index)
for i in repo.ident_index:
    n = pt.Nucleon.create_on_nucleonic_data(
        nucleonic_data=repo.nucleonic_data_lict.get_itemic_unit(i)
    )
    e = pt.Electron.create_on_electonic_data(
        electronic_data=repo.electronic_data_lict.get_itemic_unit(i)
    )
    a = pt.Atom(n, e, repo.orbitic_data)
    alist.append(a)
    #e.activate()
    #e.revisor(5, True)
    print(repr(a))
    # print(repr(e))
print(repo)
import heurams.kernel.reactor as rt
ph: rt.Phaser = rt.Phaser(alist)
print(ph)
pr: rt.Procession = ph.current_procession() # type: ignore
print(pr)
pr.forward()
print(pr)
pr.forward() # 如果过界了?
print(pr) # 静默设置状态 无报错
pr.forward()
print(pr)
pr = ph.current_procession() # type: ignore # 下一个队列
print(pr)
pr.forward()
print(pr)
pr.append() # 如果记忆失败了?
print(pr)
pr.forward()
pr.append() # 如果记忆失败了?
pr.append() # 如果记忆失败了?
pr.append() # 如果记忆失败了?
pr.append() # 如果记忆失败了?
pr.append() # 如果记忆失败了?
# 重复项目只会占据一个车尾
print(pr)
pr.forward()
print(pr)
pr = ph.current_procession() # type: ignore
print(pr)
