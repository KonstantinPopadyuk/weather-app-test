<script lang="ts">
	import ProgressBar from '../lib/ProgressBar.svelte';

	const generateUserId = () => {
		let userId = localStorage.getItem('userId');
		if (!userId) {
			userId = crypto.randomUUID(); // или другой метод генерации
			localStorage.setItem('userId', userId);
		}
		return userId;
	};

	interface Location {
		id: number;
		name: string;
		latitude: number;
		longitude: number;
		elevation: number;
		country: string;
		admin1: string;
		population?: number;
	}

	const progressValue = 50;

	// Изначально пустой массив для данных прогноза
	let forecast: { date: string; mean_temp: number }[] = [];
	let loading = false;
	let error: string | null = null;
	let searchQuery = 'Москва';
	let suggestions: Location[] = [];
	let showSuggestions = false;
	let timeoutId: ReturnType<typeof setTimeout> | null = null;

	// Функция для получения подсказок
	async function fetchSuggestions() {
		const query = searchQuery.trim();
		if (!query) {
			suggestions = [];
			showSuggestions = false;
			return;
		}

		try {
			const encodedQuery = encodeURIComponent(query);
			const response = await fetch(
				`https://geocoding-api.open-meteo.com/v1/search?name=${encodedQuery}&count=5&language=ru&format=json`
			);

			if (!response.ok) return;

			const data = await response.json();
			suggestions = data.results || [];
			showSuggestions = suggestions.length > 0;
		} catch (e) {
			suggestions = [];
			showSuggestions = false;
		}
	}

	// Обработчик выбора подсказки
	function selectSuggestion(suggestion: Location) {
		searchQuery = suggestion.name;
		showSuggestions = false;
		suggestions = [];
		fetchLocationAndForecast(suggestion);
	}

	async function fetchLocationAndForecast(locationArg?: Location) {
		if (!searchQuery.trim() && !locationArg) return;

		loading = true;
		error = null;
		forecast = []; // Сбрасываем предыдущий прогноз
		showSuggestions = false; // Скрываем подсказки при запросе
		suggestions = []; // Очищаем подсказки

		try {
			let latitude: number;
			let longitude: number;

			if (locationArg) {
				// Используем переданные координаты
				latitude = locationArg.latitude;
				longitude = locationArg.longitude;
			} else {
				// 1. Запрос координат города
				const encodedQuery = encodeURIComponent(searchQuery.trim());
				const geoResponse = await fetch(
					`https://geocoding-api.open-meteo.com/v1/search?name=${encodedQuery}&count=1&language=ru&format=json`
				);

				if (!geoResponse.ok) throw new Error('Ошибка геокодинга');

				const geoData = await geoResponse.json();
				const results: Location[] = geoData.results || [];

				if (results.length === 0) {
					error = 'Город не найден';
					return;
				}

				latitude = results[0].latitude;
				longitude = results[0].longitude;
			}

			// 2. Запрос прогноза по координатам
			const forecastResponse = await fetch(
				`http://localhost:8005/weather/forecast_7days?lat=${latitude}&lon=${longitude}&query=${encodeURIComponent(searchQuery.trim())}`,
				{
					headers: {
						'X-User-ID': generateUserId()
					}
				}
			);

			if (!forecastResponse.ok) throw new Error('Ошибка прогноза');

			forecast = await forecastResponse.json();
		} catch (e: unknown) {
			error = 'Ошибка: ' + (e instanceof Error ? e.message : String(e));
			showSuggestions = false;
			suggestions = [];
		} finally {
			loading = false;
		}
	}

	// Добавляем отслеживание изменений для подсказок
	$: if (searchQuery) {
		if (timeoutId) clearTimeout(timeoutId);
		timeoutId = setTimeout(() => {
			if (searchQuery.trim()) {
				fetchSuggestions();
			} else {
				flagOnLoad = true;
				showSuggestions = false;
				suggestions = [];
			}
		}, 300);
	} else {
		showSuggestions = false;
		suggestions = [];
	}

	// Загружаем данные для Москвы при инициализации
	showSuggestions = false;
	suggestions = [];
	let flagOnLoad = false;
	fetchLocationAndForecast();
</script>

<div class="card preset-outlined-surface-500 p-4">
	<div class="grid grid-cols-2 gap-2 p-4">
		<label class="label">
			<div class="relative">
				<input
					class="input"
					type="text"
					placeholder="Введите город"
					bind:value={searchQuery}
					on:keydown={(e) => e.key === 'Enter' && fetchLocationAndForecast()}
				/>
				{#if flagOnLoad && showSuggestions && suggestions.length > 0}
					<ul
						class="absolute z-10 mt-1 w-full rounded border border-gray-300 bg-white text-gray-800 shadow"
					>
						{#each suggestions as suggestion (suggestion.id)}
							<li
								class="cursor-pointer p-2 text-gray-800 hover:bg-gray-100"
								on:click|preventDefault={() => selectSuggestion(suggestion)}
								on:mousedown|preventDefault={() => selectSuggestion(suggestion)}
							>
								<span class="font-medium">{suggestion.name}</span>, {suggestion.admin1}, {suggestion.country}
							</li>
						{/each}
					</ul>
				{/if}
			</div>
		</label>
		<button
			type="button"
			class="btn preset-outlined-primary-500"
			on:click={() => fetchLocationAndForecast()}
			disabled={loading}
		>
			{#if loading}Загрузка...{:else}Показать{/if}
		</button>
	</div>

	{#if error}
		<div class="p-4 text-red-500">{error}</div>
	{/if}
	<div class="flex w-full flex-col p-4">
		<ProgressBar indeterminate={true} value={0} max={100} height="h-0.5" color="blue" />
	</div>

	<!-- Таблица с прогнозом -->
	<div class="table-wrap p-8">
		<table class="table caption-bottom">
			<thead>
				<tr>
					<th>Дата</th>
					<th class="!text-right">Прогноз температуры (°C)</th>
				</tr>
			</thead>
			<tbody class="[&>tr]:hover:preset-tonal-primary">
				{#if forecast.length === 0 && !loading}
					<tr>
						<td colspan="2" class="text-center">Нет данных</td>
					</tr>
				{:else}
					{#each forecast as row}
						<tr>
							<td>{row.date}</td>
							<td class="text-right">{row.mean_temp.toFixed(1)}</td>
						</tr>
					{/each}
				{/if}
			</tbody>
		</table>
	</div>
</div>
