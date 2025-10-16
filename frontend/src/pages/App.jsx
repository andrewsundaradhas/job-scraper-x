import React, { useEffect, useMemo, useState } from 'react'
import Header from '../components/Header'
import Filters from '../components/Filters'
import JobCard from '../components/JobCard'
import { Button } from '../components/ui/button'
import { api, ROOT_URL } from '../lib/api'
import { useSearchParams } from 'react-router-dom'

export default function App() {
	const [params] = useSearchParams()
	const [filters, setFilters] = useState({ order_by: '-created_at' })
	const [jobs, setJobs] = useState([])
	const [loading, setLoading] = useState(false)
	const [scraping, setScraping] = useState(false)
	const [maxPages, setMaxPages] = useState(10)

	const keyword = params.get('q') || undefined

	useEffect(() => {
		setLoading(true)
		api.search({ keyword: keyword || '', location: filters.location || '', max_pages: maxPages })
			.then(setJobs)
			.finally(() => setLoading(false))
	}, [keyword, filters.order_by, filters.company, filters.location, maxPages])

	async function runScrape() {
		setScraping(true)
		try {
			await api.scrape({ keywords: keyword || 'Software Engineer', location: filters.location || 'Remote', max_pages: maxPages })
			await api.jobs({ keyword, ...filters, limit: 50, offset: 0 }).then(setJobs)
		} finally {
			setScraping(false)
		}
	}

	return (
		<div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-200 dark:from-slate-900 dark:to-slate-950">
			<Header />
			<Filters filters={filters} setFilters={setFilters} />
			<div className="mx-4 my-4 flex items-center justify-between">
				<h2 className="text-slate-700 dark:text-slate-200 font-semibold">Jobs</h2>
				<div className="flex items-center gap-3">
					<input type="number" min={1} max={50} value={maxPages} onChange={e=>setMaxPages(Number(e.target.value)||10)} className="w-24 bg-transparent border rounded px-3 py-2" title="Max pages"/>
					<Button onClick={runScrape} disabled={scraping}>{scraping ? 'Scraping…' : 'Run Scrape'}</Button>
					<Button variant="outline" onClick={async ()=>{
						setScraping(true)
						try {
							const res = await api.advancedScrape({ keywords: keyword || 'Software Engineer', location: filters.location || 'Remote', max_pages: maxPages, enrich: true })
							await api.jobs({ keyword, ...filters, limit: 50, offset: 0 }).then(setJobs)
							if (res?.files) {
								const links = Object.values(res.files).filter(Boolean)
								if (links.length) {
									window.open(`${ROOT_URL}${links[0]}`, '_blank')
								}
							}
						} finally { setScraping(false) }} } disabled={scraping}>Advanced Scrape</Button>
				</div>
			</div>
			{loading ? (
				<div className="mx-4 text-slate-600 dark:text-slate-300">Loading…</div>
			) : (
				<div className="mx-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
					{jobs.map(j => (
						<JobCard key={j.id} job={j} />
					))}
				</div>
			)}
		</div>
	)
}
