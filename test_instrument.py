import time
from types import SimpleNamespace

from glove.synth import Synth
from glove.instrument import Instrument


synth = Synth()
synth.start()

instrument = Instrument(synth)

dt = 0.05

# fake right hand
right = SimpleNamespace(
    x=0.0,
    y=0.5,
    openness=1.0,
)

hands = {
    "right": right,
    "left": None,
}

print("Sweeping left to right...")

# move hand left -> right
for i in range(200):

    right.x = i / 199.0

    instrument.update(
        hands,
        dt,
    )

    time.sleep(dt)

print("Closing hand (mute)...")

right.openness = 0.0

for _ in range(20):

    instrument.update(
        hands,
        dt,
    )

    time.sleep(dt)

print("Opening hand...")

right.openness = 1.0

for _ in range(20):

    instrument.update(
        hands,
        dt,
    )

    time.sleep(dt)

print("Brightness sweep...")

for i in range(100):

    right.y = i / 99.0

    instrument.update(
        hands,
        dt,
    )

    time.sleep(dt)

print("Done")

synth.stop()