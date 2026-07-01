# Hi!

This repository contains every FRC match played in the 2022-2026 seasons. The data was scraped from The Blue Alliance (TBA). The script in [getData.py](getData.py) fetches the data and writes it to [matches.json](matches.json).

## File Format

`matches.json` is a JSON array of match objects. Each object has the following shape:

```json
{
    "event_key": "String",        // TBA event key
    "match_key": "String",        // TBA match key
    "comp_level": "String",       // qm, ef, qf, sf, or f
    "competition_week": "i32",    // Event week used for sorting and time ordering
    "match_number": "i32",        // Match number within the event
    "blue_t1": "i32",             // Blue alliance team 1, with the frc prefix removed
    "blue_t2": "i32",             // Blue alliance team 2, with the frc prefix removed
    "blue_t3": "i32",             // Blue alliance team 3, with the frc prefix removed
    "red_t1": "i32",              // Red alliance team 1, with the frc prefix removed
    "red_t2": "i32",              // Red alliance team 2, with the frc prefix removed
    "red_t3": "i32",              // Red alliance team 3, with the frc prefix removed
    "red_auto_points": "i32",     // Red alliance auto score
    "blue_auto_points": "i32",    // Blue alliance auto score
    "red_main_points": "i32",     // Red alliance teleop / main score
    "blue_main_points": "i32",    // Blue alliance teleop / main score
    "red_endgame_points": "i32",  // Red alliance endgame score
    "blue_endgame_points": "i32", // Blue alliance endgame score
    "red_total_points": "i32",    // Red alliance total score
    "blue_total_points": "i32",   // Blue alliance total score
    "red_won": "bool",            // True if red won the match
    "match_year": "i32",          // Season year
    "match_rank": "i32"           // Derived ranking tier from event type and comp_level
}
```

## `match_rank`

`match_rank` is assigned by `getData.py` to group matches by event prestige and round:

- `0` = district qualification
- `1` = district playoff
- `2` = district championship qualification
- `3` = district championship playoff
- `4` = regional qualification
- `5` = regional playoff
- `6` = world championship qualification
- `7` = world championship playoff

The matches are sorted by `match_year` and `competition_week` before they are written.