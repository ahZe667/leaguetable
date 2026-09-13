import { useState } from 'react'

function MatchRow({ match, nameOf, onSave, onClear }) {
  const [home, setHome] = useState(match.home_score ?? '')
  const [away, setAway] = useState(match.away_score ?? '')

  const played = match.home_score !== null && match.away_score !== null
  const filled = home !== '' && away !== ''

  return (
    <div className="match-row">
      <span className="home">{nameOf(match.home_team_id)}</span>
      <span className="scores">
        <input
          className="score-input"
          type="number"
          min="0"
          value={home}
          aria-label={`${nameOf(match.home_team_id)} score`}
          onChange={(event) => setHome(event.target.value)}
        />
        <span className="muted">:</span>
        <input
          className="score-input"
          type="number"
          min="0"
          value={away}
          aria-label={`${nameOf(match.away_team_id)} score`}
          onChange={(event) => setAway(event.target.value)}
        />
      </span>
      <span>{nameOf(match.away_team_id)}</span>
      <span className="actions">
        <button
          type="button"
          disabled={!filled}
          onClick={() => onSave(match.id, Number(home), Number(away))}
        >
          Save
        </button>
        <button
          type="button"
          className="outline secondary"
          disabled={!played}
          onClick={() => {
            setHome('')
            setAway('')
            onClear(match.id)
          }}
        >
          Clear
        </button>
      </span>
    </div>
  )
}

export default function Fixtures({ matches, teams, onSave, onClear }) {
  if (matches.length === 0) {
    return <p className="muted">No fixtures yet. Generate them from the Teams tab.</p>
  }

  const nameOf = (id) => teams.find((team) => team.id === id)?.name ?? 'Unknown'
  const rounds = [...new Set(matches.map((match) => match.round))].sort((a, b) => a - b)

  return (
    <section>
      {rounds.map((round) => (
        <article key={round}>
          <header>
            <strong>Round {round}</strong>
          </header>
          {matches
            .filter((match) => match.round === round)
            .map((match) => (
              <MatchRow
                key={match.id}
                match={match}
                nameOf={nameOf}
                onSave={onSave}
                onClear={onClear}
              />
            ))}
        </article>
      ))}
    </section>
  )
}
