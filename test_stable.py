from glove.smoothing import Stable

# the first sample is accepted immediately
s = Stable(frames=3)
assert s(True) is True

# a real change needs 3 frames in a row
assert s(False) is True     # 1st frame of False: still True
assert s(False) is True     # 2nd
assert s(False) is False    # 3rd: accepted

# flicker never gets through
s = Stable(frames=3)
s(True)
for v in [False, True, False, True, False, True]:
    assert s(v) is True

# reset forgets everything
s.reset()
assert s(False) is False

print("Stable tests passed")