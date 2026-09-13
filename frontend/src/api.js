// All backend calls live here. Components never call fetch directly.

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

async function describeFailure(response) {
  const body = await response.json().catch(() => null)
  if (body && typeof body.detail === 'string') return body.detail
  if (body && Array.isArray(body.detail)) {
    return body.detail.map((item) => item.msg).join('; ')
  }
  return `${response.status} ${response.statusText}`.trim()
}

async function request(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!response.ok) {
    throw new Error(await describeFailure(response))
  }
  return response.status === 204 ? null : response.json()
}

function send(path, method, payload) {
  return request(path, { method, body: JSON.stringify(payload) })
}

export function listSeasons() {
  return request('/api/seasons')
}

export function createSeason(name) {
  return send('/api/seasons', 'POST', { name })
}

export function listTeams(seasonId) {
  return request(`/api/seasons/${seasonId}/teams`)
}

export function addTeam(seasonId, name) {
  return send(`/api/seasons/${seasonId}/teams`, 'POST', { name })
}

export function deleteTeam(teamId) {
  return request(`/api/teams/${teamId}`, { method: 'DELETE' })
}

export function generateFixtures(seasonId) {
  return request(`/api/seasons/${seasonId}/fixtures`, { method: 'POST' })
}

export function listMatches(seasonId) {
  return request(`/api/seasons/${seasonId}/matches`)
}

export function setResult(matchId, homeScore, awayScore) {
  return send(`/api/matches/${matchId}/result`, 'PUT', {
    home_score: homeScore,
    away_score: awayScore,
  })
}

export function getStandings(seasonId) {
  return request(`/api/seasons/${seasonId}/standings`)
}
