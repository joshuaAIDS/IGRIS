import sys, re
sys.path.insert(0, r'C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\scripts')
from language_identifier_v2 import LanguageIdentifierV2

# Test the 5 previously misclassified English sentences
texts = [
    "Network transport layers establish reliable end-to-end connections using transmission control protocols.",
    "Asynchronous event loops handle multiple concurrent non-blocking input and output operations efficiently.",
    "Cache coherence mechanisms maintain memory uniformity across multiple processing cores in modern processors.",
    "High-availability architectures eliminate single points of failure through automated failover mechanisms.",
    "Microservice architectures decouple application components into independently deployable units communicating over HTTP.",
]

# And genuine Tanglish sentences
tanglish_texts = [
    "Innaiku office-ku seekiram kelambanum da, client meeting irukku.",
    "Indha hotel-la biryani taste romba nalla iruku pa.",
    "Server reboot aana piragu microservices automatically start aagala, script execute பண்ணனும்.",
    "Let us wrap up this release quickly da, otherwise deployment will get delayed.",
    "Decoder-only transformer architecture-ல் multi-head self-attention mechanisms language representations-ஐ generate செய்கின்றன.",
]

# Let's inspect improved logic
def improved_identify(text):
    # If we use refined suffix patterns:
    # Remove 'le' and 'la' and 'aa' from bare word.endswith() patterns!
    # Require hyphenated check for -la, -le, -aa, or standalone words
    pass
