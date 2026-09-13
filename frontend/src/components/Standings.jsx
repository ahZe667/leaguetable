export default function Standings({ rows }) {
  if (rows.length === 0) {
    return <p className="muted">Add teams to see the table.</p>
  }

  return (
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Team</th>
          <th className="numeric">P</th>
          <th className="numeric">W</th>
          <th className="numeric">D</th>
          <th className="numeric">L</th>
          <th className="numeric">GF</th>
          <th className="numeric">GA</th>
          <th className="numeric">GD</th>
          <th className="numeric">Pts</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row, index) => (
          <tr key={row.team_id}>
            <td className="muted">{index + 1}</td>
            <td>{row.team_name}</td>
            <td className="numeric">{row.played}</td>
            <td className="numeric">{row.won}</td>
            <td className="numeric">{row.drawn}</td>
            <td className="numeric">{row.lost}</td>
            <td className="numeric">{row.goals_for}</td>
            <td className="numeric">{row.goals_against}</td>
            <td className="numeric">
              {row.goal_difference > 0 ? `+${row.goal_difference}` : row.goal_difference}
            </td>
            <td className="numeric">
              <strong>{row.points}</strong>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
