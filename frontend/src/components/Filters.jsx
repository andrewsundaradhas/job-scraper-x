import React, { useEffect, useState } from 'react'
import { api } from '../lib/api'

export default function Filters({ filters, setFilters }) {
	function set(k, v) { setFilters(prev => ({ ...prev, [k]: v })) }
    const [companyOpts, setCompanyOpts] = useState([])
    const [locationOpts, setLocationOpts] = useState([])

    useEffect(() => {
        const v = (filters.company || '').trim()
        if (!v) { setCompanyOpts([]); return }
        const t = setTimeout(() => { api.suggestCompanies(v, 8).then(setCompanyOpts) }, 200)
        return () => clearTimeout(t)
    }, [filters.company])

    useEffect(() => {
        const v = (filters.location || '').trim()
        if (!v) { setLocationOpts([]); return }
        const t = setTimeout(() => { api.suggestLocations(v, 8).then(setLocationOpts) }, 200)
        return () => clearTimeout(t)
    }, [filters.location])
	return (
        <div className="glass mx-4 rounded-xl px-4 py-3 flex flex-wrap gap-3 items-center sticky top-[72px] z-30">
            <div className="relative">
                <input list="company-suggest" type="text" placeholder="Company" value={filters.company||''} onChange={e=>set('company', e.target.value||undefined)} className="bg-transparent border rounded px-3 py-2"/>
                <datalist id="company-suggest">
                    {companyOpts.map(o => <option key={o} value={o} />)}
                </datalist>
            </div>
            <div className="relative">
                <input list="location-suggest" type="text" placeholder="Location" value={filters.location||''} onChange={e=>set('location', e.target.value||undefined)} className="bg-transparent border rounded px-3 py-2"/>
                <datalist id="location-suggest">
                    {locationOpts.map(o => <option key={o} value={o} />)}
                </datalist>
            </div>
			<select value={filters.order_by||'-created_at'} onChange={e=>set('order_by', e.target.value)} className="bg-transparent border rounded px-3 py-2">
				<option value="-created_at">Newest</option>
				<option value="created_at">Oldest</option>
			</select>
		</div>
	)
}
