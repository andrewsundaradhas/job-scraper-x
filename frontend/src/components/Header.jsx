import React, { useState, useEffect } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { Button } from './ui/button'
import { Sun, Moon, Bell, Search } from 'lucide-react'
import { api } from '../lib/api'

export default function Header() {
	const [dark, setDark] = useState(false)
	const [params] = useSearchParams()
	const navigate = useNavigate()
	const [q, setQ] = useState(params.get('q') || '')

	useEffect(() => {
		document.documentElement.classList.toggle('dark', dark)
	}, [dark])

    function onSubmit(e) {
		e.preventDefault()
		navigate(`/?q=${encodeURIComponent(q)}`)
	}

    const [suggestions, setSuggestions] = useState([])
    useEffect(() => {
        let active = true
        const v = q.trim()
        if (!v) { setSuggestions([]); return }
        const t = setTimeout(() => {
            api.suggestKeywords(v, 8).then(s => { if (active) setSuggestions(s) })
        }, 200)
        return () => { active = false; clearTimeout(t) }
    }, [q])

	return (
		<header className="sticky top-0 z-40 glass mx-4 my-4 rounded-xl px-4 py-3 flex items-center gap-3">
			<Link to="/" className="font-semibold text-slate-800 dark:text-slate-100">LISA<span className="text-primary">.</span></Link>
			<form onSubmit={onSubmit} className="flex-1 flex items-center gap-2">
                <div className="relative flex items-center gap-2 flex-1 bg-white/70 dark:bg-slate-800/50 rounded-lg px-3 py-2">
					<Search className="w-4 h-4 text-slate-500"/>
					<input value={q} onChange={e=>setQ(e.target.value)} placeholder="Search jobs" className="flex-1 bg-transparent outline-none text-slate-800 dark:text-slate-100" />
                    {suggestions.length > 0 && (
                        <div className="absolute left-0 right-0 top-full mt-1 bg-white dark:bg-slate-800 rounded-md shadow border z-50 max-h-64 overflow-auto">
                            {suggestions.map(s => (
                                <button key={s} type="button" onClick={() => setQ(s)} className="w-full text-left px-3 py-2 hover:bg-slate-100 dark:hover:bg-slate-700 text-sm">{s}</button>
                            ))}
                        </div>
                    )}
				</div>
				<Button type="submit" className="shrink-0">Search</Button>
			</form>
			<Link to="/alerts" className="text-slate-600 dark:text-slate-300"><Bell className="w-5 h-5"/></Link>
			<Button variant="ghost" onClick={()=>setDark(!dark)} aria-label="Toggle theme">
				{dark ? <Sun className="w-5 h-5"/> : <Moon className="w-5 h-5"/>}
			</Button>
		</header>
	)
}
