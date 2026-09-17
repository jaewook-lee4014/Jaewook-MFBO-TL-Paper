import re, collections, sys
main = open(sys.argv[1]).read()
si = open(sys.argv[2]).read()
refs = collections.defaultdict(set)
pat = re.compile(r'Supplementary (Notes?|Tables?|Figs?\.?)~?\s*([0-9]+(?:\s*~?(?:,|and|--)\s*~?\s*[0-9]+)*)')
for kind, body in pat.findall(main):
    k = 'Note' if kind.startswith('Note') else 'Table' if kind.startswith('Table') else 'Fig'
    nums = re.findall(r'[0-9]+', body)
    if '--' in body and len(nums) == 2:
        nums = [str(n) for n in range(int(nums[0]), int(nums[1]) + 1)]
    refs[k].update(nums)
notes = re.findall(r'\\suppnote\{.*?\}\{(suppnote:[^}]*)\}', si)
tables = re.findall(r'\\label\{(supptab:[^}]*)\}', si)
figs = re.findall(r'\\label\{(suppfig:[^}]*)\}', si)
for k, items in (('Note', notes), ('Table', tables), ('Fig', figs)):
    missing = [i + 1 for i in range(len(items)) if str(i + 1) not in refs[k]]
    print(f'{k}: {len(items)} in SI, referenced {sorted(refs[k], key=int)}, NOT referenced {missing}')
