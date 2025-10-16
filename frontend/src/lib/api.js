const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

async function http(path, opts = {}) {
	const res = await fetch(`${BASE_URL}${path}`, {
		...opts,
		headers: {
			'Content-Type': 'application/json',
			...(opts.headers || {})
		}
	})
	if (!res.ok) throw new Error(`HTTP ${res.status}`)
	return res.json()
}

export const api = {
	jobs(params = {}) {
		const q = new URLSearchParams(params)
		return http(`/jobs?${q.toString()}`)
	},
	alerts(params = {}) {
		const q = new URLSearchParams(params)
		return http(`/alerts?${q.toString()}`)
	},
	scrape({ keywords, location }) {
		const q = new URLSearchParams({ keywords, location })
		return http(`/scrape?${q.toString()}`, { method: 'POST' })
	}
}
