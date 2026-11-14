import time

from glove.synth import Synth

s = Synth()

print("\nStarting synth...")
s.start()

# =====================================================
# 1. LEAD OSCILLATOR
# =====================================================

print("\nTEST 1: Lead voice")

s.set_lead(
    midi=60,
    gate=True,
    cutoff_hz=8000,
    vibrato_cents=0,
    reverb=0,
    delay=0,
)

time.sleep(3)

# =====================================================
# 2. GLIDE
# =====================================================

print("\nTEST 2: Glide")

for note in [60, 64, 67, 72, 79]:

    print("Note:", note)

    s.set_lead(
        midi=note,
        gate=True,
        cutoff_hz=8000,
        vibrato_cents=0,
        reverb=0,
        delay=0,
    )

    time.sleep(1)

# =====================================================
# 3. FILTER / BRIGHTNESS
# =====================================================

print("\nTEST 3: Filter brightness")

s.set_lead(
    midi=60,
    gate=True,
    cutoff_hz=200,
    vibrato_cents=0,
    reverb=0,
    delay=0,
)

time.sleep(2)

for cutoff in [
    300,
    600,
    1200,
    2500,
    5000,
    8000,
]:

    print("Cutoff:", cutoff)

    s.set_lead(
        midi=60,
        gate=True,
        cutoff_hz=cutoff,
        vibrato_cents=0,
        reverb=0,
        delay=0,
    )

    time.sleep(1)

# =====================================================
# 4. VIBRATO
# =====================================================

print("\nTEST 4: Vibrato")

for vib in [0, 10, 20, 40, 80]:

    print("Vibrato:", vib)

    s.set_lead(
        midi=69,
        gate=True,
        cutoff_hz=8000,
        vibrato_cents=vib,
        reverb=0,
        delay=0,
    )

    time.sleep(2)

# =====================================================
# 5. CHORDS
# =====================================================

print("\nTEST 5: Pad chords")

chords = [
    ("G",  [55, 59, 62]),
    ("Bm", [59, 62, 66]),
    ("C",  [60, 64, 67]),
    ("Cm", [60, 63, 67]),
]

for name, chord in chords:

    print(name)

    s.set_pad(
        notes=chord,
        cutoff_hz=3000,
        level=1.0,
    )

    time.sleep(3)

# =====================================================
# 6. LEAD + CHORD
# =====================================================

print("\nTEST 6: Lead + Pad")

s.set_pad(
    notes=[55, 59, 62],
    cutoff_hz=3000,
    level=1.0,
)

for note in [
    67,
    69,
    71,
    74,
    71,
    69,
    67,
]:

    s.set_lead(
        midi=note,
        gate=True,
        cutoff_hz=5000,
        vibrato_cents=20,
        reverb=0,
        delay=0,
    )

    time.sleep(0.5)

# =====================================================
# 7. DELAY
# =====================================================

print("\nTEST 7: Delay")

s.set_pad(None, 0, 0)

for amount in [
    0.0,
    0.25,
    0.5,
    0.75,
    1.0,
]:

    print("Delay:", amount)

    s.set_lead(
        midi=72,
        gate=True,
        cutoff_hz=7000,
        vibrato_cents=0,
        reverb=0,
        delay=amount,
    )

    time.sleep(3)

# =====================================================
# 8. REVERB
# =====================================================

print("\nTEST 8: Reverb")

for amount in [
    0.0,
    0.25,
    0.5,
    0.75,
    1.0,
]:

    print("Reverb:", amount)

    s.set_lead(
        midi=60,
        gate=True,
        cutoff_hz=5000,
        vibrato_cents=0,
        reverb=amount,
        delay=0,
    )

    time.sleep(3)

# =====================================================
# 9. EVERYTHING TOGETHER
# =====================================================

print("\nTEST 9: Full synth")

s.set_pad(
    notes=[55, 59, 62],
    cutoff_hz=3000,
    level=1.0,
)

melody = [
    67,
    69,
    71,
    74,
    79,
    74,
    71,
    69,
]

for note in melody:

    s.set_lead(
        midi=note,
        gate=True,
        cutoff_hz=5000,
        vibrato_cents=25,
        reverb=0.5,
        delay=0.4,
    )

    print(
        "RMS:",
        round(
            s.level(),
            3
        )
    )

    time.sleep(0.6)



# =====================================================
# SHUTDOWN
# =====================================================

print("\nStopping")

s.set_lead(
    midi=None,
    gate=False,
    cutoff_hz=1000,
    vibrato_cents=0,
    reverb=0,
    delay=0,
)

s.set_pad(
    notes=None,
    cutoff_hz=1000,
    level=0,
)

time.sleep(1)

s.stop()

print("\nDone")