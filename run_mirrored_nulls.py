import json
import random
from pathlib import Path
from typing import List, Dict
import hashlib

# Helper conversions
A_ORD = ord('A')

def letters_to_nums(s: str) -> List[int]:
    return [ord(c) - A_ORD for c in s.strip()]

def nums_to_letters(nums: List[int]) -> str:
    return ''.join(chr(n + A_ORD) for n in nums)

# Class schedule functions

def class_id(i: int, classing: str) -> int:
    if classing == 'c6a':
        return i % 6
    elif classing == 'c6b':
        return ((i % 3) * 2) + ((i // 3) % 2)
    else:
        raise ValueError(f'Unknown classing {classing}')

# T2 permutation helpers

def build_t2_maps(t2: Dict) -> (List[int], List[int]):
    N = t2['N']
    anchors = set()
    for s, e in t2['anchors']:
        anchors.update(range(s, e+1))
    na_indices = t2['NA']
    order = t2['order_abs_dst']
    # map src->dst
    src_to_dst = list(range(N))
    for src, na_idx in enumerate(na_indices):
        dst = order[src]
        src_to_dst[na_idx] = dst
    # anchors already map to themselves (in initial src_to_dst)
    # build dst->src
    dst_to_src = [0]*N
    for src, dst in enumerate(src_to_dst):
        dst_to_src[dst] = src
    return src_to_dst, dst_to_src


def apply_t2_forward(seq: List[int], src_to_dst: List[int]) -> List[int]:
    out = [0]*len(seq)
    for src, dst in enumerate(src_to_dst):
        out[dst] = seq[src]
    return out


def invert_t2(seq: List[int], dst_to_src: List[int]) -> List[int]:
    out = [0]*len(seq)
    for dst, src in enumerate(dst_to_src):
        out[src] = seq[dst]
    return out

# Family operations

def encrypt_family(fam: str, p: int, k: int) -> int:
    if fam == 'vigenere':
        return (p + k) % 26
    elif fam == 'beaufort':
        return (k - p) % 26
    elif fam == 'variant_beaufort':
        return (p - k) % 26
    else:
        raise ValueError(f'unknown family {fam}')

def decrypt_family(fam: str, c: int, k: int) -> int:
    if fam == 'vigenere':
        return (c - k) % 26
    elif fam == 'beaufort':
        return (k - c) % 26
    elif fam == 'variant_beaufort':
        return (c + k) % 26
    else:
        raise ValueError(f'unknown family {fam}')

# Scoring

def tokens_from_cuts(pt: str, cuts: List[int]) -> List[str]:
    toks = []
    start = 0
    for cut in cuts:
        toks.append(pt[start:cut+1])
        start = cut+1
    return toks


def score_with_cuts(pt_nums: List[int], cuts: List[int], lexicon: set, fwords: set):
    pt = nums_to_letters(pt_nums)
    toks = tokens_from_cuts(pt, cuts)
    total = len(toks)
    cov = sum(1 for t in toks if t in lexicon) / total
    fw = sum(1 for t in toks if t in fwords)
    return cov, fw

# Main per-candidate routine

def run_candidate(base_path: Path, ct_letters: List[int], cuts: List[int], lexicon: set, fwords: set):
    pt_path = base_path / 'plaintext_97.txt'
    proof_path = base_path / 'proof_digest.json'
    pt_letters = letters_to_nums(pt_path.read_text())
    proof = json.loads(proof_path.read_text())
    t2 = json.loads((base_path.parent / Path(proof['t2_path']).name).read_text())
    src_to_dst, dst_to_src = build_t2_maps(t2)
    N = len(ct_letters)

    # invert T2 on pt and ct
    ct_pre = invert_t2(ct_letters, dst_to_src)
    pt_pre = invert_t2(pt_letters, dst_to_src)

    # build per-class info
    per_class = {pc['class_id']: pc for pc in proof['per_class']}
    classing = proof['classing']
    ordinals = [0]*N
    counts = [0]*6
    residues = [0]*N
    families = [None]*N
    Ls = [0]*6
    phases = [0]*6
    for cls, info in per_class.items():
        Ls[cls] = info['L']
        phases[cls] = info['phase']
    for i in range(N):
        cls = class_id(i, classing)
        ord = counts[cls]
        counts[cls] += 1
        L = Ls[cls]
        phase = phases[cls]
        residues[i] = (ord + phase) % L
        families[i] = per_class[cls]['family']

    # derive key from pt and ct
    kv_tables = {cls: [None]*per_class[cls]['L'] for cls in per_class}
    for i in range(N):
        cls = class_id(i, classing)
        r = residues[i]
        fam = families[i]
        P = pt_pre[i]
        C = ct_pre[i]
        if fam == 'vigenere':
            K = (C - P) % 26
        elif fam == 'beaufort':
            K = (C + P) % 26
        elif fam == 'variant_beaufort':
            K = (P - C) % 26
        else:
            raise ValueError
        table = kv_tables[cls]
        if table[r] is None:
            table[r] = K
        elif table[r] != K:
            raise ValueError('Inconsistent key')
    # sanity check decrypt
    def decrypt_with_tables(ct_letters_local, kv_tables_local):
        c_pre_l = invert_t2(ct_letters_local, dst_to_src)
        p_pre_l = [0]*N
        for i in range(N):
            cls = class_id(i, classing)
            fam = families[i]
            r = residues[i]
            K = kv_tables_local[cls][r]
            p_pre_l[i] = decrypt_family(fam, c_pre_l[i], K)
        pt_l = apply_t2_forward(p_pre_l, src_to_dst)
        return pt_l

    pt_check = decrypt_with_tables(ct_letters, kv_tables)
    if pt_check != pt_letters:
        raise AssertionError('decrypt sanity failed')

    # compute observed metrics
    coverage_obs, fwords_obs = score_with_cuts(pt_letters, cuts, lexicon, fwords)

    # prepare forced residues mapping
    forced = {}
    for item in proof['forced_anchor_residues']:
        cls = item['class_id']
        forced.setdefault(cls, {})[item['residue']] = item['kv']

    # null sampling
    K = 10000
    count_cov = 0
    count_fw = 0
    rand = random.Random(proof['seed_u64'])
    for _ in range(K):
        kv_tables_rand = {}
        for cls, info in per_class.items():
            L = info['L']
            kv = [0]*L
            forced_cls = forced.get(cls, {})
            for r in range(L):
                if r in forced_cls:
                    kv[r] = forced_cls[r]
                else:
                    kv[r] = rand.randint(0,25)
            kv_tables_rand[cls] = kv
        pt_null = decrypt_with_tables(ct_letters, kv_tables_rand)
        cov_t, fw_t = score_with_cuts(pt_null, cuts, lexicon, fwords)
        if cov_t >= coverage_obs:
            count_cov += 1
        if fw_t >= fwords_obs:
            count_fw += 1

    p_cov = (1 + count_cov) / (K + 1)
    p_fw = (1 + count_fw) / (K + 1)
    # Holm m=2
    if p_cov <= p_fw:
        adj_cov = min(1.0, 2 * p_cov)
        adj_fw = min(1.0, p_fw)
    else:
        adj_fw = min(1.0, 2 * p_fw)
        adj_cov = min(1.0, p_cov)
    publishable = adj_cov < 0.01 and adj_fw < 0.01

    holm_report = {
        "K": K,
        "metrics": {
            "coverage": {"p_raw": p_cov, "p_holm": adj_cov},
            "f_words": {"p_raw": p_fw, "p_holm": adj_fw}
        },
        "publishable": publishable
    }
    (base_path / 'holm_report_canonical.json').write_text(json.dumps(holm_report, indent=2) + '\n')

    coverage_report = {
        "pt_sha256": hashlib.sha256(pt_path.read_bytes()).hexdigest(),
        "ct_sha256": hashlib.sha256((base_path.parent / 'ciphertext_97.txt').read_bytes()).hexdigest(),
        "proof_sha256": hashlib.sha256(proof_path.read_bytes()).hexdigest(),
        "encrypts_to_ct": True,
        "t2_sha256": proof['t2_sha256'],
        "nulls": {
            "status": "ran",
            "p_raw": {"coverage": p_cov, "f_words": p_fw},
            "p_holm": {"coverage": adj_cov, "f_words": adj_fw}
        }
    }
    (base_path / 'coverage_report.json').write_text(json.dumps(coverage_report, indent=2) + '\n')

    return {
        'label': base_path.name,
        'pt_sha256': coverage_report['pt_sha256'],
        'publishable': publishable
    }


def main():
    uniq = Path('Uniqueness')
    ct_letters = letters_to_nums((uniq / 'ciphertext_97.txt').read_text())
    cuts = json.loads((uniq / 'canonical_cuts.json').read_text())['cuts_inclusive_0idx']
    lexicon = {line.split('\t')[0] for line in (uniq / 'lexicon_large.tsv').read_text().splitlines()[1:]}
    fwords = set((uniq / 'function_words.txt').read_text().split())

    summaries = []
    for cand in ['baseline_IS_REAL', 'alt_IS_TRUE', 'alt_IS_FACT', 'alt_IS_A_MAP']:
        summaries.append(run_candidate(uniq / cand, ct_letters, cuts, lexicon, fwords))

    unique_flag = not any(s['publishable'] for s in summaries)
    summary = {
        'candidates': summaries,
        'unique': unique_flag
    }
    (uniq / 'uniqueness_confirm_summary.json').write_text(json.dumps(summary, indent=2) + '\n')

if __name__ == '__main__':
    main()
