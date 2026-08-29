# Structural App — FINAL elevation population rule

Tables 3.2.2 through 3.2.8 use STORY DATA as the authoritative story/elevation list.

Population rule:
- Exclude only stories with elevation < 0.00.
- Exclude only the final/highest top story.
- Include every other story.
- Always include GROUND FL at elevation 0.00.
- Display from the highest retained elevation down to 0.00.
- If a source calculation table has no record for a valid story, the story remains visible and only unavailable calculated cells show `-`; the app does not fabricate source values.

## Stiffness Distribution Charts

Tables 3.2.6 and 3.2.7 now automatically generate a stiffness-distribution chart after calculation. The X-direction and Y-direction charts plot calculated stiffness (kN/m) against the actual STORY DATA elevation, use the same displayed storeys as the tables, and include the elevation 0.00 storey when it is part of the report range.
