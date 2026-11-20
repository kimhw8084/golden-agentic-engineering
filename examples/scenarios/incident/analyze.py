"""Small incident timeline helper. It reports correlation, never causal conclusions."""
import json
import sys
from datetime import datetime
from pathlib import Path


def timeline(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding='utf-8').splitlines():
        row = json.loads(line)
        if not all(key in row for key in ('timestamp', 'service', 'event', 'request_id')):
            raise ValueError('Event row missing required fields.')
        datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
        rows.append(row)
    return sorted(rows, key=lambda row: row['timestamp'])


if __name__ == '__main__':
    for row in timeline(Path(sys.argv[1])):
        print(row['timestamp'], row['service'], row['event'], row['request_id'])
    print('Correlation is not proof of cause.')
