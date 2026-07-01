import json
import requests
from dataclasses import dataclass
import sys
headers = {
    "X-TBA-Auth-Key": "AFeMEKN9ZTshaTU9KWxFId4Pi4vfzWOTEOrGfVlsAIhoNbSQDYkwCanQhKvCDMcx"
}

@dataclass
class Match:
    event_key: str
    match_key: str
    comp_level: str  # TBA: "qm" qual, or "ef"/"qf"/"sf"/"f" playoff
    competition_week: int
    match_number: int
    blue_t1: int
    blue_t2: int
    blue_t3: int
    red_t1: int
    red_t2: int
    red_t3: int
    red_auto_points: int
    blue_auto_points: int
    red_main_points: int
    blue_main_points: int
    red_endgame_points: int
    blue_endgame_points: int
    red_total_points: int
    blue_total_points: int
    red_won: bool
    match_year: int
    #0 for district quals, 1 for district playoffs, 2 for regional quals, 3 for for regional playoffs, 4 for worlds quals, 5 for world championchips
    match_rank: int
    def __init__(
        self,
        event_key: str,
        match_key: str,
        comp_level: str,
        competition_week: int,
        match_number: int,
        blue_t1: str,
        blue_t2: str,
        blue_t3: str,
        red_t1: str,
        red_t2: str,
        red_t3: str,
        red_auto_points: int,
        blue_auto_points: int,
        red_main_points: int,
        blue_main_points: int,
        red_endgame_points: int,
        blue_endgame_points: int,
        red_total_points: int,
        blue_total_points: int,
        red_won: bool,
        match_year: int,
        match_rank: int
    ):
        self.event_key = event_key
        self.match_key = match_key
        self.comp_level = comp_level
        self.competition_week = competition_week
        self.match_number = match_number
        self.blue_t1 = int(blue_t1.removeprefix("frc"))
        self.blue_t2 = int(blue_t2.removeprefix("frc"))
        self.blue_t3 = int(blue_t3.removeprefix("frc"))
        self.red_t1 = int(red_t1.removeprefix("frc"))
        self.red_t2 = int(red_t2.removeprefix("frc"))
        self.red_t3 = int(red_t3.removeprefix("frc"))
        self.red_auto_points = red_auto_points
        self.blue_auto_points = blue_auto_points
        self.red_main_points = red_main_points
        self.blue_main_points = blue_main_points
        self.red_endgame_points = red_endgame_points
        self.blue_endgame_points = blue_endgame_points
        self.red_total_points = red_total_points
        self.blue_total_points = blue_total_points
        self.red_won = red_won
        self.match_year = match_year
        self.match_rank = match_rank


# Map TBA event_type + comp_level -> the prestige tiers on Match.match_rank (qual/playoff):
#   0/1 district event | 2/3 district championship | 4/5 regional | 6/7 world championship
# TBA event_type ints: 0 Regional, 1 District, 2 District Champ, 3 Champ Division,
# 4 Champ Finals (Einstein), 5 District Champ Division. comp_level "qm" = qual, else playoff.
def match_rank_for(event_type: int, comp_level: str) -> int:
    is_playoff = comp_level != "qm"
    if event_type == 1:              # district event
        return 1 if is_playoff else 0
    if event_type in (2, 5):         # district championship (+ its divisions)
        return 3 if is_playoff else 2
    if event_type == 0:              # regional
        return 5 if is_playoff else 4
    if event_type in (3, 4):         # world championship (divisions + Einstein)
        return 7 if is_playoff else 6
    return -1                        # offseason / preseason / unknown


def fetch_matches_for_year(year: int) -> list[Match]:
    response_events = requests.get(
        f"https://www.thebluealliance.com/api/v3/events/{year}", headers
    ).json()

    events: list[tuple[str, int, int]] = []
    for event in response_events:
        event_type = event["event_type"]
        if event_type not in (0, 1, 2, 3, 4, 5):
            continue
        # Championship-level events have week == None; slot them after the 0-5 regular weeks
        # (district champs at 7, worlds at 8) so temporal ordering / the train-test split hold.
        week = event["week"]
        if week is None:
            week = 7 if event_type in (2, 5) else 8
        events.append((event["key"], week, event_type))

    matches: list[Match] = []
    for event in events:
        code = event[0]
        response_matches = requests.get(
            f"https://www.thebluealliance.com/api/v3/event/{code}/matches", headers
        ).json()
        for match in response_matches:
            sb = match["score_breakdown"]
            if sb is None:
                continue
            if year == 2026:
                blue_auto_points    = int(sb["blue"]["autoTowerPoints"]) + int(sb["blue"]["hubScore"]["autoPoints"])
                red_auto_points     = int(sb["red"]["autoTowerPoints"])  + int(sb["red"]["hubScore"]["autoPoints"])
                blue_main_points    = int(sb["blue"]["hubScore"]["teleopPoints"])
                red_main_points     = int(sb["red"]["hubScore"]["teleopPoints"])
                blue_endgame_points = int(sb["blue"]["endGameTowerPoints"]) + int(sb["blue"]["hubScore"]["endgamePoints"])
                red_endgame_points  = int(sb["red"]["endGameTowerPoints"])  + int(sb["red"]["hubScore"]["endgamePoints"])
            elif year == 2025:  # 2025
                blue_auto_points    = int(sb["blue"]["autoPoints"])
                red_auto_points     = int(sb["red"]["autoPoints"])
                blue_main_points    = int(sb["blue"]["teleopPoints"])
                red_main_points     = int(sb["red"]["teleopPoints"])
                blue_endgame_points = int(sb["blue"]["endGameBargePoints"])
                red_endgame_points  = int(sb["red"]["endGameBargePoints"])
            elif year == 2024:
                blue_auto_points    = int(sb["blue"]["autoPoints"])
                red_auto_points     = int(sb["red"]["autoPoints"])
                blue_main_points    = int(sb["blue"]["teleopPoints"])
                red_main_points     = int(sb["red"]["teleopPoints"])
                blue_endgame_points = int(sb["blue"]["endGameTotalStagePoints"])
                red_endgame_points  = int(sb["red"]["endGameTotalStagePoints"])
            elif year == 2023:
                blue_auto_points    = int(sb["blue"]["autoPoints"])
                red_auto_points     = int(sb["red"]["autoPoints"])
                blue_main_points    = int(sb["blue"]["teleopPoints"])
                red_main_points     = int(sb["red"]["teleopPoints"])
                blue_endgame_points = int(sb["blue"]["endGameChargeStationPoints"]) + int(sb["blue"]["endGameParkPoints"])
                red_endgame_points  = int(sb["red"]["endGameChargeStationPoints"]) + int(sb["red"]["endGameParkPoints"])
            elif year == 2022:
                blue_auto_points    = int(sb["blue"]["autoPoints"])
                red_auto_points     = int(sb["red"]["autoPoints"])
                blue_main_points    = int(sb["blue"]["teleopPoints"])
                red_main_points     = int(sb["red"]["teleopPoints"])
                blue_endgame_points = int(sb["blue"]["endgamePoints"])
                red_endgame_points  = int(sb["red"]["endgamePoints"])                                
            else:
                print(f"Error: {year} is invalid")
                sys.exit(1)
            blue_total_points = int(sb["blue"]["totalPoints"])
            red_total_points  = int(sb["red"]["totalPoints"])

            comp_level = match["comp_level"]
            match_rank = match_rank_for(event[2], comp_level)

            matches.append(Match(
                match["event_key"],
                match["key"],
                comp_level,
                event[1],
                match["match_number"],
                match["alliances"]["blue"]["team_keys"][0],
                match["alliances"]["blue"]["team_keys"][1],
                match["alliances"]["blue"]["team_keys"][2],
                match["alliances"]["red"]["team_keys"][0],
                match["alliances"]["red"]["team_keys"][1],
                match["alliances"]["red"]["team_keys"][2],
                red_auto_points,
                blue_auto_points,
                red_main_points,
                blue_main_points,
                red_endgame_points,
                blue_endgame_points,
                red_total_points,
                blue_total_points,
                match["winning_alliance"] == "red",
                year,
                match_rank
            ))

    print(f"{len(matches)} matches detected in {year}")
    return matches


all_matches: list[Match] = []
for year in [2022, 2023, 2024, 2025, 2026]:
    all_matches.extend(fetch_matches_for_year(year))

all_matches.sort(key=lambda m: (m.match_year, m.competition_week))
print(f"Total matches: {len(all_matches)}")
with open("matches.json", "w") as f:
    json.dump([m.__dict__ for m in all_matches], f)