const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
export const ROOT_URL = BASE_URL.replace(/\/?api$/, '')

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
	search(params = {}) {
		const q = new URLSearchParams(params)
		return http(`/search?${q.toString()}`)
	},
	suggestKeywords(q = '', limit = 10) {
		return http(`/suggest/keywords?q=${encodeURIComponent(q)}&limit=${limit}`)
	},
	suggestCompanies(q = '', limit = 10) {
		return http(`/suggest/companies?q=${encodeURIComponent(q)}&limit=${limit}`)
	},
	suggestLocations(q = '', limit = 10) {
		return http(`/suggest/locations?q=${encodeURIComponent(q)}&limit=${limit}`)
	},
	alerts(params = {}) {
		const q = new URLSearchParams(params)
		return http(`/alerts?${q.toString()}`)
	},
	scrape({ keywords, location, max_pages = 10 }) {
		const q = new URLSearchParams({ keywords, location, max_pages })
		return http(`/scrape?${q.toString()}`, { method: 'POST' })
	},
	advancedScrape({ keywords, location, max_pages = 10, enrich = true, headless = true, delay_min = 2, delay_max = 5 }) {
		const q = new URLSearchParams({ keywords, location, max_pages, enrich, headless, delay_min, delay_max })
		return http(`/scrape/advanced?${q.toString()}`, { method: 'POST' })
	}
}
