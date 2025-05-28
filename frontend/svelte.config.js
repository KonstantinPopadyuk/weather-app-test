// frontend/svelte.config.js
import adapter from '@sveltejs/adapter-auto';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: vitePreprocess(),
	kit: {
		adapter: adapter(),
	},
	onwarn: (warning, handler) => {
		// Игнорировать конкретные предупреждения
		if (warning.code.startsWith('a11y-')) return;
		handler(warning);
	}
};

export default config;