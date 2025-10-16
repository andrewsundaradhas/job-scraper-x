import React, { useEffect, useState } from 'react'
import Header from '../components/Header'
import { api } from '../lib/api'

export default function Alerts() {
	const [logs, setLogs] = useState([])

	useEffect(() => {
		api.alerts({ limit: 200, offset: 0 }).then(setLogs)
	}, [])

	return (
		<div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-200 dark:from-slate-900 dark:to-slate-950">
			<Header />
			<div className="glass mx-4 my-4 p-4 rounded-xl overflow-auto">
				<table className="min-w-full text-sm">
					<thead>
						<tr className="text-left text-slate-600 dark:text-slate-300">
							<th className="py-2">Time</th>
							<th className="py-2">Channel</th>
							<th className="py-2">Status</th>
							<th className="py-2">Message</th>
						</tr>
					</thead>
					<tbody>
						{logs.map(l => (
							<tr key={l.id} className="border-t border-slate-200/40 dark:border-slate-800/60">
								<td className="py-2 text-slate-700 dark:text-slate-200">{new Date(l.created_at).toLocaleString()}</td>
								<td className="py-2">{l.channel}</td>
								<td className="py-2">{l.status}</td>
								<td className="py-2 text-slate-600 dark:text-slate-300 truncate max-w-[40ch]" title={l.message||''}>{l.message || ''}</td>
							</tr>
						))}
					</tbody>
				</table>
			</div>
		</div>
	)
}
