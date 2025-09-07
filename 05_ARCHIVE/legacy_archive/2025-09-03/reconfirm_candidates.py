import json, hashlib, random, math
from pathlib import Path
from typing import List, Dict
from collections import Counter

A_ORD = ord('A')

def letters_to_nums(s: str) -> List[int]:
    return [ord(c) - A_ORD for c in s.strip()]

def nums_to_letters(nums: List[int]) -> str:
    return ''.join(chr(n + A_ORD) for n in nums)

# Class schedule

def class_id(i: int, classing: str) -> int:
    if classing == 'c6a':
        return i % 6
    elif classing == 'c6b':
        return ((i % 3) * 2) + ((i // 3) % 2)
    else:
        raise ValueError(f'Unknown classing {classing}')

# Permutation helpers

def build_t2_maps(t2: Dict) -> (List[int], List[int]):
    N = t2['N']
    anchors = set()
    for s,e in t2['anchors']:
        anchors.update(range(s, e+1))
    na_indices = t2['NA']
    order = t2['order_abs_dst']
    src_to_dst = list(range(N))
    for src, na_idx in enumerate(na_indices):
        dst = order[src]
        src_to_dst[na_idx] = dst
    dst_to_src = [0]*N
    for i, dst in enumerate(src_to_dst):
        dst_to_src[dst] = i
    return src_to_dst, dst_to_src


def apply_t2_forward(arr: List[int], src_to_dst: List[int]) -> List[int]:
    out = [0]*len(arr)
    for src, dst in enumerate(src_to_dst):
        out[dst] = arr[src]
    return out


def invert_t2(arr: List[int], dst_to_src: List[int]) -> List[int]:
    out = [0]*len(arr)
    for dst, src in enumerate(dst_to_src):
        out[src] = arr[dst]
    return out

# family encrypt/decrypt

def encrypt_family(fam: str, P: int, K: int) -> int:
    if fam == 'vigenere':
        return (P + K) % 26
    elif fam == 'beaufort':
        return (K - P) % 26
    elif fam == 'variant_beaufort':
        return (P - K) % 26
    else:
        raise ValueError(f'unknown family {fam}')

def decrypt_family(fam: str, C: int, K: int) -> int:
    if fam == 'vigenere':
        return (C - K) % 26
    elif fam == 'beaufort':
        return (K - C) % 26
    elif fam == 'variant_beaufort':
        return (C + K) % 26
    else:
        raise ValueError(f'unknown family {fam}')

# scoring helpers

def tokens_from_cuts(pt: str, cuts: List[int]) -> List[str]:
    toks=[]
    start=0
    for cut in cuts:
        toks.append(pt[start:cut+1])
        start=cut+1
    return toks

def score_with_cuts(pt_nums: List[int], cuts: List[int], lexicon:set, fwords:set):
    pt=nums_to_letters(pt_nums)
    toks=tokens_from_cuts(pt, cuts)
    total=len(toks)
    cov=sum(1 for t in toks if t in lexicon)/total
    fw=sum(1 for t in toks if t in fwords)
    return cov, fw

# tokenization v2 head tokens

def head_tokens_v2(pt: str, cuts: List[int], head_end:int=74) -> List[str]:
    toks=[]
    start=0
    for cut in cuts:
        tok=pt[start:cut+1]
        if cut<=head_end or start<=head_end<=cut:
            toks.append(tok)
        start=cut+1
    return toks

# near gate
VERB_TOKENS={'IS','ARE','WAS','BE','AM','SET','READ','SEE','NOTE','SIGHT','OBSERVE'}

def near_gate_report(pt: str, cuts: List[int], lexicon:set, fwords:set):
    toks=tokens_from_cuts(pt,cuts)
    total=len(toks)
    cov=sum(1 for t in toks if t in lexicon)/total
    fw=sum(1 for t in toks if t.upper() in fwords)
    has_verb=any(t.upper() in VERB_TOKENS or t.endswith('ED') or t.endswith('ING') for t in toks)
    passed=cov>=0.85 and fw>=8 and has_verb
    return {
        'coverage': cov,
        'function_words': fw,
        'has_verb': has_verb,
        'pass': passed
    }

# phrase gate flint v2
INSTR_VERBS={'READ','SEE','NOTE','SIGHT','OBSERVE'}
INSTR_NOUNS={'BERLIN','CLOCK','BERLINCLOCK','DIAL'}
DECL_PATTERNS=[['SET','COURSE','TRUE'],['CORRECT','BEARING','TRUE'],['REDUCE','COURSE','TRUE'],['APPLY','DECLINATION'],['BRING','TRUE','MERIDIAN']]

def flint_v2(head_tokens: List[str], lexicon:set, fwords:set):
    tokens=[t for t in head_tokens]
    content=[t for t in tokens if t in lexicon and t not in fwords]
    content_count=len(content)
    max_repeat=max(Counter(content).values()) if content else 0
    east='EAST' in tokens
    ne='NORTHEAST' in tokens
    noun=any(t in INSTR_NOUNS for t in tokens)
    # declination pattern
    decl_end=None
    n=len(tokens)
    for pat in DECL_PATTERNS:
        idx=0
        found=True
        for w in pat:
            while idx<n and tokens[idx]!=w:
                idx+=1
            if idx==n:
                found=False
                break
            idx+=1
        if found:
            decl_end=idx-1
            break
    decl_ok=decl_end is not None
    instr_verb=False
    if decl_ok:
        for t in tokens[decl_end+1:]:
            if t in INSTR_VERBS:
                instr_verb=True
                break
    passed=all([decl_ok, instr_verb, east, ne, noun, content_count>=6, max_repeat<=2])
    return {
        'pass': passed,
        'declination_phrase': decl_ok,
        'instrument_verb': instr_verb,
        'has_east': east,
        'has_northeast': ne,
        'instrument_noun': noun,
        'content_count': content_count,
        'max_repeat_non_anchor_content': max_repeat
    }

# generic track placeholder

def generic_track(head_tokens: List[str]):
    return {
        'pass': False,
        'perplexity_percentile': 0.0,
        'pos_trigram_score': 0.0
    }

# main per-candidate

def run_candidate(base_path: Path, globals):
    cuts=globals['cuts']
    lexicon=globals['lexicon']
    fwords=globals['fwords']
    ct_letters=globals['ct_letters']
    t2=globals['t2']
    src_to_dst=globals['src_to_dst']
    dst_to_src=globals['dst_to_src']
    calib_hashes=globals['calib_hashes']

    pt_path=base_path/'plaintext_97.txt'
    proof_path=base_path/'proof_digest.json'
    pt_letters=letters_to_nums(pt_path.read_text())
    proof=json.loads(proof_path.read_text())

    N=len(ct_letters)
    ct_pre=invert_t2(ct_letters,dst_to_src)
    pt_pre=invert_t2(pt_letters,dst_to_src)

    per_class={pc['class_id']:pc for pc in proof['per_class']}
    classing=proof['classing']
    counts=[0]*6
    residues=[0]*N
    families=[None]*N
    Ls=[0]*6
    phases=[0]*6
    for cls,info in per_class.items():
        Ls[cls]=info['L']
        phases[cls]=info['phase']
    for i in range(N):
        cls=class_id(i,classing)
        ord=counts[cls]
        counts[cls]+=1
        L=Ls[cls]
        phase=phases[cls]
        residues[i]=(ord+phase)%L
        families[i]=per_class[cls]['family']
    # derive key
    kv_tables={cls:[None]*per_class[cls]['L'] for cls in per_class}
    for i in range(N):
        cls=class_id(i,classing)
        r=residues[i]
        fam=families[i]
        P=pt_pre[i]
        C=ct_pre[i]
        if fam=='vigenere':
            K=(C-P)%26
        elif fam=='beaufort':
            K=(C+P)%26
        elif fam=='variant_beaufort':
            K=(P-C)%26
        table=kv_tables[cls]
        if table[r] is None:
            table[r]=K
        elif table[r]!=K:
            raise ValueError('Inconsistent key')
    # decrypt check (sanity)
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

    # near gate
    pt_str=nums_to_letters(pt_letters)
    near=near_gate_report(pt_str,cuts,lexicon,fwords)
    Path(base_path/'near_gate_report.json').write_text(json.dumps(near,indent=2)+"\n")

    # phrase gate
    head_toks=head_tokens_v2(pt_str,cuts)
    flint=flint_v2(head_toks,lexicon,fwords)
    generic=generic_track(head_toks)
    accepted_by='flint_v2' if flint['pass'] else ('generic' if generic['pass'] else None)
    phrase_pass = flint['pass'] or generic['pass']
    phrase_report={
        'tokenization_v2': True,
        'tracks': {
            'flint_v2': flint,
            'generic': generic
        },
        'accepted_by': accepted_by,
        'pass': phrase_pass
    }
    Path(base_path/'phrase_gate_report.json').write_text(json.dumps(phrase_report,indent=2)+"\n")

    policy={
        'phrase_gate': 'Flint v2 OR Generic',
        'tokenization': 'v2',
        'calibration_sha256': calib_hashes
    }
    Path(base_path/'phrase_gate_policy.json').write_text(json.dumps(policy,indent=2)+"\n")

    # null sampling
    coverage_obs, fwords_obs = score_with_cuts(pt_letters, cuts, lexicon, fwords)
    forced={}
    for item in proof['forced_anchor_residues']:
        cls=item['class_id']
        forced.setdefault(cls,{})[item['residue']] = item['kv']
    K=10000
    count_cov=0
    count_fw=0
    rand=random.Random(proof['seed_u64'])
    for _ in range(K):
        kv_tables_rand={}
        for cls,info in per_class.items():
            L=info['L']
            kv=[0]*L
            forced_cls=forced.get(cls,{})
            for r in range(L):
                if r in forced_cls:
                    kv[r]=forced_cls[r]
                else:
                    kv[r]=rand.randint(0,25)
            kv_tables_rand[cls]=kv
        # decrypt
        c_pre=invert_t2(ct_letters,dst_to_src)
        p_pre=[0]*N
        for i in range(N):
            cls=class_id(i,classing)
            fam=families[i]
            r=residues[i]
            Kval=kv_tables_rand[cls][r]
            p_pre[i]=decrypt_family(fam,c_pre[i],Kval)
        pt_null=apply_t2_forward(p_pre,src_to_dst)
        cov_t, fw_t = score_with_cuts(pt_null, cuts, lexicon, fwords)
        if cov_t >= coverage_obs:
            count_cov += 1
        if fw_t >= fwords_obs:
            count_fw += 1
    p_cov=(1+count_cov)/(K+1)
    p_fw=(1+count_fw)/(K+1)
    if p_cov <= p_fw:
        adj_cov=min(1.0,2*p_cov)
        adj_fw=min(1.0,p_fw)
    else:
        adj_fw=min(1.0,2*p_fw)
        adj_cov=min(1.0,p_cov)
    publishable=adj_cov<0.01 and adj_fw<0.01

    holm_report={
        'K':K,
        'metrics':{
            'coverage':{'p_raw':p_cov,'p_holm':adj_cov},
            'f_words':{'p_raw':p_fw,'p_holm':adj_fw}
        },
        'publishable':publishable
    }
    Path(base_path/'holm_report_canonical.json').write_text(json.dumps(holm_report,indent=2)+"\n")

    coverage_report={
        'cuts_inclusive_0idx': cuts,
        'pt_sha256': hashlib.sha256(pt_path.read_bytes()).hexdigest(),
        'ct_sha256': hashlib.sha256((base_path.parent/'ciphertext_97.txt').read_bytes()).hexdigest(),
        'proof_sha256': hashlib.sha256(proof_path.read_bytes()).hexdigest(),
        'route_id':'SPOKE_NE_NF_w1',
        't2_sha256': globals['t2_sha256'],
        'seed_recipe': proof.get('seed_recipe'),
        'seed_u64': proof.get('seed_u64'),
        'encrypts_to_ct': True,
        'near_gate': near,
        'phrase_gate': {'accepted_by': accepted_by, 'pass': phrase_pass},
        'lm_calibration_sha256': calib_hashes,
        'nulls':{
            'status':'ran',
            'p_raw':{'coverage':p_cov,'f_words':p_fw},
            'p_holm':{'coverage':adj_cov,'f_words':adj_fw}
        }
    }
    Path(base_path/'coverage_report.json').write_text(json.dumps(coverage_report,indent=2)+"\n")

    # hashes.txt
    hashes_lines=[
        f"{coverage_report['pt_sha256']}  plaintext_97.txt",
        f"{coverage_report['proof_sha256']}  proof_digest.json",
        hashlib.sha256((base_path/'near_gate_report.json').read_bytes()).hexdigest()+"  near_gate_report.json",
        hashlib.sha256((base_path/'phrase_gate_policy.json').read_bytes()).hexdigest()+"  phrase_gate_policy.json",
        hashlib.sha256((base_path/'phrase_gate_report.json').read_bytes()).hexdigest()+"  phrase_gate_report.json",
        hashlib.sha256((base_path/'holm_report_canonical.json').read_bytes()).hexdigest()+"  holm_report_canonical.json",
        hashlib.sha256((base_path/'coverage_report.json').read_bytes()).hexdigest()+"  coverage_report.json"
    ]
    (base_path/'hashes.txt').write_text("\n".join(hashes_lines)+"\n")

    return {
        'label': base_path.name,
        'pt_sha256': coverage_report['pt_sha256'],
        'route_id': 'SPOKE_NE_NF_w1',
        'feasible': True,
        'near_gate': near['pass'],
        'phrase_gate': {'track': accepted_by, 'pass': phrase_pass},
        'holm_adj_p': {'coverage': adj_cov, 'f_words': adj_fw},
        'publishable': publishable
    }


def main():
    uniq=Path('Uniqueness')
    ct_letters=letters_to_nums((uniq/'ciphertext_97.txt').read_text())
    cuts=json.loads(Path('config/canonical_cuts.json').read_text())['cuts_inclusive_0idx']
    lexicon={line.split('\t')[0] for line in Path('lm/lexicon_large.tsv').read_text().splitlines()[1:]}
    fwords=set(Path('config/function_words.txt').read_text().split())
    t2=json.loads(Path('t2lib_v1/permutations/SPOKE_NE_NF_w1.json').read_text())
    src_to_dst,dst_to_src=build_t2_maps(t2)
    calib_hashes={
        'calib_97_perplexity': hashlib.sha256(Path('examples/calibration/calib_97_perplexity.json').read_bytes()).hexdigest(),
        'pos_trigrams': hashlib.sha256(Path('examples/calibration/pos_trigrams.json').read_bytes()).hexdigest(),
        'pos_threshold': hashlib.sha256(Path('examples/calibration/pos_threshold.txt').read_bytes()).hexdigest()
    }
    globals={'cuts':cuts,'lexicon':lexicon,'fwords':fwords,'ct_letters':ct_letters,'t2':t2,
             'src_to_dst':src_to_dst,'dst_to_src':dst_to_src,'calib_hashes':calib_hashes,
             't2_sha256': hashlib.sha256(Path('t2lib_v1/permutations/SPOKE_NE_NF_w1.json').read_bytes()).hexdigest()}
    summaries=[]
    candidates=['baseline_IS_REAL','alt_IS_TRUE','alt_IS_FACT','alt_IS_A_MAP']
    for cand in candidates:
        summaries.append(run_candidate(uniq/ cand, globals))
    unique_flag = not any(s['publishable'] for s in summaries if s['label']!='baseline_IS_REAL')
    reason = 'alternate_passed_full_bar' if not unique_flag else 'none'
    summary={
        'model_class':{
            'routes':'SPOKE_NE_NF_w1 only',
            'classings':['c6a'],
            'families':['vigenere','variant_beaufort','beaufort'],
            'periods':[10,22],
            'phases':'0..L-1',
            'option_A': True
        },
        'candidates': summaries,
        'uniqueness': {'unique': unique_flag, 'reason': reason}
    }
    (uniq/'uniqueness_confirm_summary.json').write_text(json.dumps(summary,indent=2)+"\n")

if __name__=='__main__':
    main()
