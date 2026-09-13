import { useState } from 'react'

export default function Teams({
  teams,
  fixturesExist,
  onAdd,
  onRemove,
  onGenerate,
  onClearFixtures,
}) {
  const [name, setName] = useState('')

  function submit(event) {
    event.preventDefault()
    onAdd(name).then((added) => {
      if (added) setName('')
    })
  }

  return (
    <section>
      <form onSubmit={submit} className="toolbar">
        <input
          type="text"
          value={name}
          placeholder="Team name"
          aria-label="Team name"
          disabled={fixturesExist}
          onChange={(event) => setName(event.target.value)}
        />
        <button type="submit" disabled={fixturesExist}>
          Add team
        </button>
      </form>

      {fixturesExist && (
        <p className="muted">
          The team list is locked while the schedule exists. Clear the fixtures to
          change it.
        </p>
      )}

      {teams.length === 0 ? (
        <p className="muted">No teams in this season yet.</p>
      ) : (
        <ul>
          {teams.map((team) => (
            <li key={team.id}>
              {team.name}{' '}
              <button
                type="button"
                className="outline secondary"
                disabled={fixturesExist}
                onClick={() => onRemove(team.id)}
              >
                Remove
              </button>
            </li>
          ))}
        </ul>
      )}

      <div className="toolbar">
        <button type="button" disabled={teams.length < 2} onClick={onGenerate}>
          {fixturesExist ? 'Regenerate fixtures' : 'Generate fixtures'}
        </button>
        {fixturesExist && (
          <button type="button" className="outline secondary" onClick={onClearFixtures}>
            Clear fixtures
          </button>
        )}
      </div>
      {fixturesExist && (
        <p className="muted">
          Regenerating replaces the schedule and clears every result.
        </p>
      )}
    </section>
  )
}
