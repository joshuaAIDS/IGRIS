from __future__ import annotations
import json, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STRUCTURAL = [
    '<|pad|>', '<|begin_of_text|>', '<|end_of_text|>', '<think>',
    '</think>', '<action>', '</action>', '<action_result>',
    '</action_result>', '<|system|>', '<|user|>', '<|assistant|>',
]
VOCAB_SIZE = 32768


def bytelevel_alphabet():
    bs = list(range(ord('!'), ord('~') + 1))
    bs += list(range(ord('¡'), ord('¬') + 1))
    bs += list(range(ord('®'), ord('ÿ') + 1))
    cs = bs[:]
    n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b); cs.append(256 + n); n += 1
    return [chr(c) for c in cs]


def build_candidate_a(path: Path):
    from tokenizers import Tokenizer, AddedToken
    from tokenizers.models import BPE
    from tokenizers.pre_tokenizers import ByteLevel
    from tokenizers.decoders import ByteLevel as ByteLevelDecoder

    vocab = {token: i for i, token in enumerate(STRUCTURAL)}
    for token in bytelevel_alphabet():
        if token not in vocab:
            vocab[token] = len(vocab)
    i = 0
    while len(vocab) < VOCAB_SIZE:
        token = f'<|synthetic_a_{i:05d}|>'
        if token not in vocab:
            vocab[token] = len(vocab)
        i += 1
    tok = Tokenizer(BPE(vocab=vocab, merges=[], unk_token=None))
    tok.pre_tokenizer = ByteLevel(add_prefix_space=False, use_regex=True)
    tok.decoder = ByteLevelDecoder()
    tok.add_special_tokens([
        AddedToken(s, special=True, lstrip=False, rstrip=False)
        for s in STRUCTURAL
    ])
    tok.save(str(path))


def build_candidate_b(path: Path):
    from sentencepiece import sentencepiece_model_pb2 as pb
    from sentencepiece import SentencePieceProcessor

    model = pb.ModelProto()
    spec = model.trainer_spec
    spec.model_type = pb.TrainerSpec.UNIGRAM
    spec.vocab_size = VOCAB_SIZE
    spec.byte_fallback = True
    spec.pad_id = 0
    spec.bos_id = -1
    spec.eos_id = -1
    spec.unk_id = -1

    norm = model.normalizer_spec
    norm.name = 'identity'
    norm.add_dummy_prefix = False
    norm.remove_extra_whitespaces = False
    norm.escape_whitespaces = True

    def add_piece(piece, score, kind):
        p = model.pieces.add(); p.piece = piece; p.score = score; p.type = kind

    sp = pb.ModelProto.SentencePiece
    add_piece(STRUCTURAL[0], 0.0, sp.CONTROL)
    for token in STRUCTURAL[1:]:
        add_piece(token, 0.0, sp.CONTROL)
    for b in range(256):
        add_piece(f'<0x{b:02X}>', -10.0, sp.BYTE)
    i = 0
    while len(model.pieces) < VOCAB_SIZE:
        add_piece(f'syntheticb{i:05d}', -20.0, sp.NORMAL)
        i += 1
    path.write_bytes(model.SerializeToString())
    proc = SentencePieceProcessor(model_file=str(path))
    if proc.get_piece_size() != VOCAB_SIZE:
        raise RuntimeError(f'Candidate B fixture size mismatch: {proc.get_piece_size()}')


def main():
    # Import from the extracted patch tree; this script is standalone and never reads the corpus.
    import sys
    src = ROOT / 'src'
    if not src.exists():
        raise SystemExit('Expected the integrated-code ZIP to be extracted beside this kit, or copy src/igris into this kit.')
    sys.path.insert(0, str(src))
    from igris.tokenizer.strict import load_candidate_a, load_candidate_b

    with tempfile.TemporaryDirectory(prefix='igris_synthetic_') as tmp:
        tmp = Path(tmp)
        a_path, b_path = tmp / 'candidate_a.json', tmp / 'candidate_b.model'
        build_candidate_a(a_path)
        build_candidate_b(b_path)

        results = {}
        for name, loader, path in (
            ('A', load_candidate_a, a_path),
            ('B', load_candidate_b, b_path),
        ):
            tok = loader(str(path))
            sample = 'IGRIS synthetic loader check — தமிழ் test 123'
            ids = tok.encode_content(sample)
            decoded = tok.decode_content(ids)
            if decoded != sample:
                raise AssertionError(f'Candidate {name} round-trip mismatch: {decoded!r}')
            binary = bytes(range(256))
            codec = tok.raw_binary_codec()
            if codec.decode_bytes(codec.encode_bytes(binary)) != binary:
                raise AssertionError(f'Candidate {name} raw-binary round-trip mismatch')
            results[name] = {
                'loader': 'PASS', 'vocab_size': tok.vocab_size,
                'text_round_trip': 'PASS', 'raw_binary_round_trip': 'PASS',
                'fixture': 'synthetic; not trained; not production data',
            }

        report = {
            'status': 'PASS_SYNTHETIC_BACKEND_LOADERS',
            'candidate_a': results['A'],
            'candidate_b': results['B'],
            'training_started': False,
            'corpus_read': False,
            'production_artifacts_created': False,
            'note': 'Synthetic fixtures validate loader/config wiring only; they are not production tokenizers.',
        }
        out = ROOT / 'synthetic_backend_validation_report.json'
        out.write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
