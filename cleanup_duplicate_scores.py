#!/usr/bin/env python3
"""Clean up duplicate weekly scores caused by judge name variations."""

import json
from pathlib import Path
from collections import defaultdict

data_dir = Path(__file__).parent / "data"
scores_file = data_dir / "weekly_scores.json"

# Load scores
with open(scores_file, 'r') as f:
    scores = json.load(f)

print(f"Loaded {len(scores)} score entries")

# Judge name corrections (map variations to canonical names)
JUDGE_CORRECTIONS = {
    'Carri-Ann': 'Carrie-Ann',
    'Carrie Ann': 'Carrie-Ann',
    'CarrieAnn': 'Carrie-Ann',
}

def normalize_judge_name(name):
    """Normalize judge name to canonical form."""
    name = name.strip()
    # Check for known corrections
    if name in JUDGE_CORRECTIONS:
        return JUDGE_CORRECTIONS[name]
    return name

# Group scores by (team_id, week_number, normalized_judge_name)
score_groups = defaultdict(list)

for score in scores:
    # Normalize judge name
    normalized_judge = normalize_judge_name(score['judge_name'])
    key = (score['dwts_team_id'], score['week_number'], normalized_judge)
    score_groups[key].append(score)

# Find duplicates and apply corrections
print("\nLooking for duplicates and applying judge name corrections...")
duplicates_found = 0
cleaned_scores = []

for key, group in score_groups.items():
    team_id, week, judge = key

    # Apply judge name correction to all entries
    for entry in group:
        entry['judge_name'] = normalize_judge_name(entry['judge_name'])

    if len(group) > 1:
        duplicates_found += 1
        print(f"  Team {team_id}, Week {week}, Judge '{judge}': {len(group)} entries")
        print(f"    Scores: {[s['score'] for s in group]}")

        # Keep the most recent one (highest ID)
        group.sort(key=lambda x: x['id'], reverse=True)
        kept = group[0]
        print(f"    Keeping: ID {kept['id']}, score {kept['score']}")
        cleaned_scores.append(kept)
    else:
        cleaned_scores.append(group[0])

print(f"\nFound {duplicates_found} duplicate groups")
print(f"Original: {len(scores)} entries")
print(f"Cleaned: {len(cleaned_scores)} entries")
print(f"Removed: {len(scores) - len(cleaned_scores)} duplicates")

# Sort by ID
cleaned_scores.sort(key=lambda x: x['id'])

# Save cleaned data
with open(scores_file, 'w') as f:
    json.dump(cleaned_scores, f, indent=2)

print(f"\n✅ Cleaned data saved to {scores_file}")
print("You should now see correct totals in the app!")
