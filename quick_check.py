import pandas as pd
import sys

print(sys.argv)

df = pd.read_csv(sys.argv[1], index_col=False)


missing = [i for i in range(103)]

for idx in df.index:
    run = df.loc[idx, 'case name']
    run = run.replace('Run_','')
    run = int(run[:3:])
    if run in missing:
        missing.remove(run)
    else:
        print(f"Already removed run {run}, must be a duplicate")

out = "for JOB in "
for m in missing:
    out += f"{m+1} "
out = out.strip()
out += "; do"
if len(missing) > 0:
    print(out)
else:
    print("All good")
