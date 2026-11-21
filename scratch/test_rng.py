import os
import tempfile
import torch

state = torch.get_rng_state()
print("original type:", type(state), state.dtype, isinstance(state, torch.ByteTensor))

path = os.path.join(tempfile.gettempdir(), "test_rng.pt")
torch.save({"rng": state}, path)
loaded = torch.load(path, weights_only=False)
loaded_rng = loaded["rng"]
print("loaded type:", type(loaded_rng), loaded_rng.dtype, isinstance(loaded_rng, torch.ByteTensor))

# If loaded_rng is a ByteTensor, why did torch.set_rng_state fail?
try:
    torch.set_rng_state(loaded_rng)
    print("set_rng_state with loaded_rng directly: SUCCESS")
except Exception as e:
    print("set_rng_state with loaded_rng directly FAILED:", type(e), e)

# Test with .cpu().byte()
try:
    torch.set_rng_state(loaded_rng.cpu().to(torch.uint8))
    print("set_rng_state with .cpu().to(torch.uint8): SUCCESS")
except Exception as e:
    print("set_rng_state with .cpu().to(torch.uint8) FAILED:", type(e), e)

if os.path.exists(path):
    os.remove(path)
