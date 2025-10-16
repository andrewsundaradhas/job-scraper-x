import React from 'react'

export default function Filters({ filters, setFilters }) {
	function set(k, v) { setFilters(prev => ({ ...prev, [k]: v })) }
	return (
		<div className="glass mx-4 rounded-xl px-4 py-3 flex flex-wrap gap-3 items-center sticky top-[72px] z-30">
			<select value={filters.company||''} onChange={e=>set('company', e.target.value||undefined)} className="bg-transparent border rounded px-3 py-2">
				<option value="">Company</option>
				{/* Could be dynamically populated */}
				<option>Google</option>
				<option>Microsoft</option>
				<option>Amazon</option>
			</select>
			<input type="text" placeholder="Location" value={filters.location||''} onChange={e=>set('location', e.target.value||undefined)} className="bg-transparent border rounded px-3 py-2"/>
			<select value={filters.order_by||'-created_at'} onChange={e=>set('order_by', e.target.value)} className="bg-transparent border rounded px-3 py-2">
				<option value="-created_at">Newest</option>
				<option value="created_at">Oldest</option>
			</select>
		</div>
	)
}
