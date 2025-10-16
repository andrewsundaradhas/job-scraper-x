import React from 'react'
import { motion } from 'framer-motion'
import { ExternalLink } from 'lucide-react'

export default function JobCard({ job }) {
	return (
		<motion.a
			href={job.job_link}
			target="_blank"
			rel="noreferrer"
			whileHover={{ y: -4 }}
			className="glass rounded-xl p-4 flex flex-col gap-2 hover:shadow-soft"
		>
			<div className="flex items-center justify-between">
				<h3 className="font-semibold text-slate-800 dark:text-slate-100">{job.title}</h3>
				<ExternalLink className="w-4 h-4 text-slate-500" />
			</div>
			<div className="text-sm text-slate-600 dark:text-slate-300">{job.company} • {job.location}</div>
			<div className="text-xs text-slate-500">{job.posted_date || ''}</div>
		</motion.a>
	)
}
