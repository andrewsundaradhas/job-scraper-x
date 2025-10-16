/** @type {import('tailwindcss').Config} */
export default {
	content: [
		"./index.html",
		"./src/**/*.{js,jsx}"
	],
	darkMode: 'class',
	theme: {
		extend: {
			colors: {
				primary: '#2563EB',
				secondary: '#10B981',
				text: '#1E293B'
			},
			backdropBlur: {
				xs: '2px'
			},
			boxShadow: {
				soft: '0 10px 30px rgba(2,6,23,0.08)'
			}
		}
	},
	plugins: []
}
