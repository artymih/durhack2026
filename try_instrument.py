from glove.hands import HandState
from glove.instrument import Instrument


class FakeSynth:
    def set_lead(self, **kw):
        print({k: (round(v, 1) if isinstance(v, float) else v) for k, v in kw.items()})


inst = Instrument(FakeSynth())
for x in (0.1, 0.3, 0.5, 0.9):
    info = inst.update({"left": None, "right": HandState(x=x, y=0.5, openness=1.0)}, 0.016)
    print("  ->", info["lead_name"])