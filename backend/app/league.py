"""Pure league logic: fixture generation and the standings table."""

from .schemas import Match, StandingsRow, Team

WIN_POINTS = 3
DRAW_POINTS = 1


def round_robin(team_ids: list[int]) -> list[list[tuple[int, int]]]:
    """Single round-robin using the circle method.

    Returns one list of (home, away) pairs per round. With an odd number of
    teams one team sits out each round.
    """
    ids: list[int | None] = list(team_ids)
    if len(ids) % 2 == 1:
        ids.append(None)  # bye

    size = len(ids)
    rounds: list[list[tuple[int, int]]] = []
    for index in range(size - 1):
        pairs: list[tuple[int, int]] = []
        for slot in range(size // 2):
            first, second = ids[slot], ids[size - 1 - slot]
            if first is None or second is None:
                continue
            # Alternate venues so no team is always at home.
            pairs.append((first, second) if index % 2 == 0 else (second, first))
        rounds.append(pairs)
        ids.insert(1, ids.pop())
    return rounds


def compute_standings(teams: list[Team], matches: list[Match]) -> list[StandingsRow]:
    """Table built from played matches only."""
    rows = {team.id: StandingsRow(team_id=team.id, team_name=team.name) for team in teams}

    for match in matches:
        if match.home_score is None or match.away_score is None:
            continue
        home, away = rows.get(match.home_team_id), rows.get(match.away_team_id)
        if home is None or away is None:
            continue

        home.played += 1
        away.played += 1
        home.goals_for += match.home_score
        home.goals_against += match.away_score
        away.goals_for += match.away_score
        away.goals_against += match.home_score

        if match.home_score > match.away_score:
            home.won += 1
            home.points += WIN_POINTS
            away.lost += 1
        elif match.home_score < match.away_score:
            away.won += 1
            away.points += WIN_POINTS
            home.lost += 1
        else:
            home.drawn += 1
            away.drawn += 1
            home.points += DRAW_POINTS
            away.points += DRAW_POINTS

    return sorted(
        rows.values(),
        key=lambda row: (-row.points, -row.goal_difference, -row.goals_for, row.team_name),
    )
