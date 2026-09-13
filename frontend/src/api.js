// All backend calls live here. The implementation below is an in-memory mock;
// it will be replaced by real HTTP calls once the backend exists.

const LATENCY_MS = 120

let nextId = 1
const db = {
  seasons: [],
  teams: [],
  matches: [],
}

function seed() {
  const season = { id: nextId++, name: '2026/27' }
  db.seasons.push(season)
  for (const name of ['Arrows FC', 'Beacon United', 'Cobblers', 'Dockside Rovers']) {
    db.teams.push({ id: nextId++, season_id: season.id, name })
  }
}
seed()

function delay(value) {
  return new Promise((resolve) => setTimeout(() => resolve(structuredClone(value)), LATENCY_MS))
}

function fail(message) {
  return Promise.reject(new Error(message))
}

/** Single round-robin using the circle method. Returns an array of rounds. */
export function roundRobin(teamIds) {
  const ids = [...teamIds]
  if (ids.length % 2 === 1) ids.push(null) // bye
  const size = ids.length
  const rounds = []
  for (let round = 0; round < size - 1; round += 1) {
    const pairs = []
    for (let i = 0; i < size / 2; i += 1) {
      const first = ids[i]
      const second = ids[size - 1 - i]
      if (first === null || second === null) continue
      pairs.push(round % 2 === 0 ? [first, second] : [second, first])
    }
    rounds.push(pairs)
    ids.splice(1, 0, ids.pop())
  }
  return rounds
}

/** Standings computed from played matches only. */
export function computeStandings(teams, matches) {
  const rows = new Map(
    teams.map((team) => [
      team.id,
      {
        team_id: team.id,
        team_name: team.name,
        played: 0,
        won: 0,
        drawn: 0,
        lost: 0,
        goals_for: 0,
        goals_against: 0,
        goal_difference: 0,
        points: 0,
      },
    ]),
  )

  for (const match of matches) {
    if (match.home_score === null || match.away_score === null) continue
    const home = rows.get(match.home_team_id)
    const away = rows.get(match.away_team_id)
    if (!home || !away) continue

    home.played += 1
    away.played += 1
    home.goals_for += match.home_score
    home.goals_against += match.away_score
    away.goals_for += match.away_score
    away.goals_against += match.home_score

    if (match.home_score > match.away_score) {
      home.won += 1
      home.points += 3
      away.lost += 1
    } else if (match.home_score < match.away_score) {
      away.won += 1
      away.points += 3
      home.lost += 1
    } else {
      home.drawn += 1
      away.drawn += 1
      home.points += 1
      away.points += 1
    }
  }

  const table = [...rows.values()]
  for (const row of table) {
    row.goal_difference = row.goals_for - row.goals_against
  }
  table.sort(
    (a, b) =>
      b.points - a.points ||
      b.goal_difference - a.goal_difference ||
      b.goals_for - a.goals_for ||
      a.team_name.localeCompare(b.team_name),
  )
  return table
}

export function listSeasons() {
  return delay(db.seasons)
}

export function createSeason(name) {
  const trimmed = name.trim()
  if (!trimmed) return fail('Season name is required')
  if (db.seasons.some((s) => s.name === trimmed)) return fail('That season already exists')
  const season = { id: nextId++, name: trimmed }
  db.seasons.push(season)
  return delay(season)
}

export function listTeams(seasonId) {
  const teams = db.teams
    .filter((t) => t.season_id === seasonId)
    .sort((a, b) => a.name.localeCompare(b.name))
  return delay(teams)
}

export function addTeam(seasonId, name) {
  const trimmed = name.trim()
  if (!trimmed) return fail('Team name is required')
  const clash = db.teams.some((t) => t.season_id === seasonId && t.name === trimmed)
  if (clash) return fail('That team is already in this season')
  const team = { id: nextId++, season_id: seasonId, name: trimmed }
  db.teams.push(team)
  return delay(team)
}

export function deleteTeam(teamId) {
  const team = db.teams.find((t) => t.id === teamId)
  if (!team) return fail('Team not found')
  if (db.matches.some((m) => m.season_id === team.season_id)) {
    return fail('Remove the fixtures before changing the teams')
  }
  db.teams = db.teams.filter((t) => t.id !== teamId)
  return delay(null)
}

export function generateFixtures(seasonId) {
  const teams = db.teams.filter((t) => t.season_id === seasonId)
  if (teams.length < 2) return fail('Add at least two teams first')

  db.matches = db.matches.filter((m) => m.season_id !== seasonId)
  const rounds = roundRobin(teams.map((t) => t.id))
  rounds.forEach((pairs, index) => {
    for (const [homeId, awayId] of pairs) {
      db.matches.push({
        id: nextId++,
        season_id: seasonId,
        round: index + 1,
        home_team_id: homeId,
        away_team_id: awayId,
        home_score: null,
        away_score: null,
      })
    }
  })
  return listMatches(seasonId)
}

export function listMatches(seasonId) {
  const matches = db.matches
    .filter((m) => m.season_id === seasonId)
    .sort((a, b) => a.round - b.round || a.id - b.id)
  return delay(matches)
}

export function setResult(matchId, homeScore, awayScore) {
  const match = db.matches.find((m) => m.id === matchId)
  if (!match) return fail('Match not found')

  const cleared = homeScore === null || awayScore === null
  if (!cleared) {
    const invalid = [homeScore, awayScore].some(
      (value) => !Number.isInteger(value) || value < 0,
    )
    if (invalid) return fail('Scores must be whole numbers of zero or more')
  }
  match.home_score = cleared ? null : homeScore
  match.away_score = cleared ? null : awayScore
  return delay(match)
}

export function getStandings(seasonId) {
  const teams = db.teams.filter((t) => t.season_id === seasonId)
  const matches = db.matches.filter((m) => m.season_id === seasonId)
  return delay(computeStandings(teams, matches))
}
