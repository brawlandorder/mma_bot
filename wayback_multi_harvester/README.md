# Multi-Source Wayback Harvester — Beginner Guide

## 0) Install
```
pip install -r requirements.txt
```

## 1) Index URL lists (no list required)
```
python cdx_index.py
```
Outputs URL lists in `indexes/` for:
- sherdog_events, sherdog_fights, tapology_events, wikipedia_events, mmadecisions_events, mmajunkie_tags

## 2) Resolve to snapshot URLs
```
python resolve_latest_generic.py indexes/sherdog_events.txt maps/sherdog_events_map.txt
python resolve_latest_generic.py indexes/tapology_events.txt maps/tapology_events_map.txt
python resolve_latest_generic.py indexes/wikipedia_events.txt maps/wikipedia_events_map.txt
python resolve_latest_generic.py indexes/mmadecisions_events.txt maps/mmadecisions_events_map.txt
python resolve_latest_generic.py indexes/mmajunkie_tags.txt maps/mmajunkie_tags_map.txt
# (Optional, big) fights:
python resolve_latest_generic.py indexes/sherdog_fights.txt maps/sherdog_fights_map.txt
```

## 3) Download HTML snapshots
```
python download_maps.py maps/sherdog_events_map.txt sources/sherdog/events
python download_maps.py maps/tapology_events_map.txt sources/tapology/events
python download_maps.py maps/wikipedia_events_map.txt sources/wikipedia/events
python download_maps.py maps/mmadecisions_events_map.txt sources/mmadecisions/events
python download_maps.py maps/mmajunkie_tags_map.txt sources/mmajunkie/tags
# (Optional)
python download_maps.py maps/sherdog_fights_map.txt sources/sherdog/fights
```

### Notes
- Coverage varies; Wayback doesn't have everything.
- Tapology fights not included here; start with event pages.
- Sherdog fights include all orgs; filter later if needed.
- Run locally to avoid blocks.
