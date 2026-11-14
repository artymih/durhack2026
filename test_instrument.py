import time
from types import SimpleNamespace

from glove.synth import Synth
from glove.instrument import Instrument


# -----------------------------------------------------
# Create synth + instrument
# -----------------------------------------------------

synth = Synth()
synth.start()

instrument = Instrument(synth)

DT = 0.05


# -----------------------------------------------------
# Helper
# -----------------------------------------------------

def tick(count=1):
    for _ in range(count):
        instrument.update(hands, DT)
        time.sleep(DT)


# -----------------------------------------------------
# Fake hands
# -----------------------------------------------------

right = SimpleNamespace(
    x=0.5,
    y=0.5,
    depth=0.0,
    roll=0.0,
    pinch=0.0,
    openness=1.0,
)

left = SimpleNamespace(
    thumb=False,
    index=False,
    middle=False,
    ring=False,
    pinky=False,
    y=0.5,
    roll=0.0,
)

hands = {
    "right": right,
    "left": left,
}

# -----------------------------------------------------
# TEST 1
# Pitch
# -----------------------------------------------------

print("Pitch sweep")

for i in range(100):

    right.x = i / 99

    tick()

# -----------------------------------------------------
# TEST 2
# Brightness
# -----------------------------------------------------

print("Brightness sweep")

right.x = 0.5

for i in range(100):

    right.y = i / 99

    tick()

# -----------------------------------------------------
# TEST 3
# Vibrato
# -----------------------------------------------------

print("Vibrato")

right.y = 0.5

for roll in [
    0.0,
    0.2,
    0.4,
    0.6,
    0.8,
    1.0,
]:

    right.roll = roll

    tick(30)

right.roll = 0

# -----------------------------------------------------
# TEST 4
# Reverb
# -----------------------------------------------------

print("Reverb")

for depth in [
    0.0,
    0.25,
    0.5,
    0.75,
    1.0,
]:

    right.depth = depth

    tick(40)

right.depth = 0

# -----------------------------------------------------
# TEST 5
# Delay
# -----------------------------------------------------

print("Delay")

for pinch in [
    0.0,
    0.25,
    0.5,
    0.75,
    1.0,
]:

    right.pinch = pinch

    tick(40)

right.pinch = 0

# -----------------------------------------------------
# TEST 6
# Chord build-up
# -----------------------------------------------------

print("Chord build")

left.thumb = True
tick(40)

left.index = True
tick(40)

left.middle = True
tick(40)

left.ring = True
tick(40)

left.pinky = True
tick(40)

# -----------------------------------------------------
# TEST 7
# Chord colour
# -----------------------------------------------------

print("Chord colour")

for roll in [
    -1.0,
    -0.5,
    0.0,
    0.5,
    1.0,
]:

    left.roll = roll

    tick(50)

left.roll = 0

# -----------------------------------------------------
# TEST 8
# Pad volume
# -----------------------------------------------------

print("Pad volume")

for pos in range(100):

    left.y = pos / 99

    tick()

for pos in reversed(range(100)):

    left.y = pos / 99

    tick()

# -----------------------------------------------------
# TEST 9
# Everything together
# -----------------------------------------------------

print("Full instrument demo")

left.thumb = True
left.index = True
left.middle = True

for i in range(200):

    t = i / 199

    right.x = t
    right.y = 0.3

    right.roll = 0.5
    right.depth = 0.5
    right.pinch = 0.4

    left.roll = 0.2
    left.y = 0.3

    tick()

# -----------------------------------------------------
# Shut down
# -----------------------------------------------------

print("Stopping")

synth.stop()