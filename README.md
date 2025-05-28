# Weather Application

Результат выполнения тестового задания. В приложении реализована фронтенд часть с помощью Svelte, бекенд - FastAPI. В качестве хранения статистики - SQLite. Запуск через docker-compose.

## Основные функции

- Поиск погоды по названию города
- Вывод прогноза на ближайшие 7 дней (средние значения)
- Автодополнение при вводе названия города (подсказки)
- Сохранение статистики поисковых запросов
- API для получения популярных поисковых запросов
- Отображение текущей погоды и прогноза

## Technologies Used

- **Backend**:
  - FastAPI (Python)
  - Poetry for dependency management
  - SQLite database
  - OpenWeatherMap API для данных о погоде

- **Frontend**:
  - SvelteKit
  - Vite
  - Node.js
  - TailwindCSS для стилизации

## Prerequisites

- Docker
- Docker Compose

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/KonstantinPopadyuk/weather-app-test
cd weather-test-app
```

2. Start the application using Docker Compose:
```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API docs: http://localhost:8005/docs