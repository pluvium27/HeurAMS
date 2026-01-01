import heurams.kernel.repolib as repolib
import heurams.kernel.particles as pt
from pathlib import Path
repo = repolib.Repo.create_from_repodir(Path('./test_repo'))
for i in repo.ident_index:
    n = pt.Nucleon.create_on_nucleonic_data(nucleonic_data=repo.nucleonic_data_lict.get_itemic_unit(i))
    e = pt.Electron.create_on_electonic_data(electronic_data=repo.electronic_data_lict.get_itemic_unit(i))
    e.activate()
    e.revisor(5, True)
    print(repr(n))
    print(repr(e))
print(repo)