import React from 'react'
import { clsx } from 'clsx'

const base = 'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-50 disabled:pointer-events-none h-9 px-4 py-2'

const variants = {
	primary: 'bg-primary text-white hover:bg-blue-600',
	ghost: 'bg-transparent hover:bg-slate-100 dark:hover:bg-slate-800',
}

export function Button({ variant = 'primary', className, ...props }) {
	return <button className={clsx(base, variants[variant], className)} {...props} />
}
