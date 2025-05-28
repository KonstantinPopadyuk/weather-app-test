<script lang="ts">
	export let value: number;
	export let max: number;
	export let height: string = 'h-2';
	export let color: string = 'blue'; // Изменяем на enum
	export let indeterminate: boolean = false;

	// Маппинг цветов
	const colorClasses = {
		blue: 'bg-blue-500',
		green: 'bg-green-500',
		red: 'bg-red-500',
		yellow: 'bg-yellow-500',
		purple: 'bg-purple-500'
	};

	$: barColor = colorClasses[color] || colorClasses.blue;
	$: widthPercentage = indeterminate ? '100%' : `${(value / max) * 100}%`;
</script>

<div class={`w-full overflow-hidden rounded-full bg-gray-200 ${height}`}>
	<div
		class={`h-full rounded-full transition-all duration-500 ease-out ${barColor} ${
			indeterminate ? 'animate-indeterminate-progress' : ''
		}`}
		style={`width: ${widthPercentage};`}
	></div>
</div>

<style>
	@keyframes indeterminate-progress {
		0% {
			transform: translateX(-100%);
		}
		100% {
			transform: translateX(200%);
		}
	}

	.animate-indeterminate-progress {
		animation: indeterminate-progress 1.5s linear infinite;
		width: 50% !important;
	}
</style>
