import { useState } from 'react'

export default function Teams({ teams, fixturesExist, onAdd, onRemove, onGenerate }) {
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
          onChange={(event) => setName(event.target.value)}
        />
        <button type="submit">Add team</button>
      </form>

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

      <button type="button" disabled={teams.length < 2} onClick={onGenerate}>
        {fixturesExist ? 'Regenerate fixtures' : 'Generate fixtures'}
      </button>
      {fixturesExist && (
        <p className="muted">
          Regenerating replaces the schedule and clears every result.
        </p>
      )}
    </section>
  )
}
