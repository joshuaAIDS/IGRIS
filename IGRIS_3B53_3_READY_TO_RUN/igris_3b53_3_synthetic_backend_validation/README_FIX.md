IGRIS 3B.53.3 FIX

The SentencePiece protobuf does not define a PAD piece type. The PAD ID is represented by trainer_spec.pad_id=0; the piece at that ID must use a supported piece type (CONTROL here).

Replace these files:
1. scripts/run_synthetic_backend_validation.py -> the same path in your extracted synthetic kit.
2. src/igris/tokenizer/artifact_validation.py -> the same path in your extracted synthetic kit AND in the 3B.52 patch tokenizer folder.

The synthetic fixture sets piece 0 to CONTROL and the validator checks pad_id=0 plus CONTROL type.
No corpus is read and no training is performed.
