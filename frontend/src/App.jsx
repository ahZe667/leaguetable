import { useCallback, useEffect, useState } from 'react'

import * as api from './api'
import Fixtures from './components/Fixtures.jsx'
import Standings from './components/Standings.jsx'
import Teams from './components/Teams.jsx'

const TABS = [
  ['table', 'Table'],
  ['fixtures', 'Fixtures'],
  ['teams', 'Teams'],
]

export default function App() {
  const [seasons, setSeasons] = useState([])
  const [seasonId, setSeasonId] = useState(null)
  const [teams, setTeams] = useState([])
  const [matches, setMatches] = useState([])
  const [standings, setStandings] = useState([])
  const [tab, setTab] = useState('table')
  const [error, setError] = useState(null)

  const report = useCallback((cause) => setError(cause.message), [])

  const refresh = useCallback(
    (id) =>
      Promise.all([api.listTeams(id), api.listMatches(id), api.getStandings(id)])
        .then(([nextTeams, nextMatches, nextStandings]) => {
          setTeams(nextTeams)
          setMatches(nextMatches)
          setStandings(nextStandings)
        })
        .catch(report),
    [report],
  )

  useEffect(() => {
    api
      .listSeasons()
      .then((loaded) => {
        setSeasons(loaded)
        setSeasonId((current) => current ?? loaded[0]?.id ?? null)
      })
      .catch(report)
  }, [report])

  useEffect(() => {
    if (seasonId === null) return
    refresh(seasonId)
  }, [seasonId, refresh])

  function run(action) {
    setError(null)
    return action()
      .then(() => refresh(seasonId))
      .then(() => true)
      .catch((cause) => {
        report(cause)
        return false
      })
  }

  function addSeason() {
    const name = window.prompt('Season name, for example 2027/28')
    if (name === null) return
    setError(null)
    api
      .createSeason(name)
      .then((season) => {
        setSeasons((current) => [...current, season])
        setSeasonId(season.id)
      })
      .catch(report)
  }

  const currentSeason = seasons.find((season) => season.id === seasonId)

  return (
    <main className="container">
      <hgroup>
        <h1>LeagueTable</h1>
        <p>Seasons, fixtures and standings for one amateur league.</p>
      </hgroup>

      <div className="toolbar">
        <select
          value={seasonId ?? ''}
          aria-label="Season"
          onChange={(event) => setSeasonId(Number(event.target.value))}
        >
          {seasons.map((season) => (
            <option key={season.id} value={season.id}>
              {season.name}
            </option>
          ))}
        </select>
        <button type="button" className="secondary" onClick={addSeason}>
          New season
        </button>
      </div>

      {error && <p className="error">{error}</p>}

      <div className="tabs">
        {TABS.map(([key, label]) => (
          <button
            key={key}
            type="button"
            className={tab === key ? '' : 'outline'}
            onClick={() => setTab(key)}
          >
            {label}
          </button>
        ))}
      </div>

      {currentSeason === undefined ? (
        <p className="muted">Create a season to get started.</p>
      ) : (
        <>
          {tab === 'table' && <Standings rows={standings} />}
          {tab === 'fixtures' && (
            <Fixtures
              matches={matches}
              teams={teams}
              onSave={(id, home, away) => run(() => api.setResult(id, home, away))}
              onClear={(id) => run(() => api.setResult(id, null, null))}
            />
          )}
          {tab === 'teams' && (
            <Teams
              teams={teams}
              fixturesExist={matches.length > 0}
              onAdd={(name) => run(() => api.addTeam(seasonId, name))}
              onRemove={(id) => run(() => api.deleteTeam(id))}
              onGenerate={() => run(() => api.generateFixtures(seasonId))}
              onClearFixtures={() => run(() => api.clearFixtures(seasonId))}
            />
          )}
        </>
      )}
    </main>
  )
}
