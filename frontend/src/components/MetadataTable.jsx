export default function MetadataTable({ data, title = 'Metadata' }) {
  if (!data || Object.keys(data).length === 0) {
    return (
      <div className="card text-center py-8">
        <p className="text-slate-500 text-sm">No {title.toLowerCase()} available.</p>
      </div>
    )
  }

  const entries = Object.entries(data).filter(([, v]) =>
    v != null && v !== '' && !(typeof v === 'object' && Object.keys(v).length === 0)
  )

  return (
    <div className="card overflow-hidden p-0">
      <div className="px-5 py-4 border-b border-surface-border">
        <h3 className="font-semibold text-slate-200 text-sm">{title}</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <tbody>
            {entries.map(([key, val], i) => (
              <tr
                key={key}
                className={i % 2 === 0 ? 'bg-surface-card' : 'bg-surface'}
              >
                <td className="px-5 py-2.5 font-mono text-xs text-primary-400 w-1/3 align-top whitespace-nowrap">
                  {key}
                </td>
                <td className="px-5 py-2.5 text-slate-300 break-all align-top">
                  {typeof val === 'object'
                    ? <pre className="text-xs font-mono text-slate-400 whitespace-pre-wrap">{JSON.stringify(val, null, 2)}</pre>
                    : String(val)
                  }
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
