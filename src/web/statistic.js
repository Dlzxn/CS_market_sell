// Функция для форматирования числа в рубли с плавным переходом
const formatRuble = (value) => {
    if (typeof value !== 'number') {
        value = parseFloat(value) || 0;
    }
    return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
};

// Функция для анимации счетчика (для красивого появления значений)
function animateValue(obj, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const value = Math.floor(progress * (end - start) + start);
        obj.textContent = formatRuble(value);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        } else {
            obj.textContent = formatRuble(end);
        }
    };
    window.requestAnimationFrame(step);
}

// ----------------------------------------------------
// ГЛАВНЫЙ ФУНКЦИОНАЛ: ЗАПРОС К API
// ----------------------------------------------------

// Функция для имитации/получения данных за 30 дней для расчета среднего
function generateDailyDataFromMonthTotal(monthTotal, days = 30) {
    const avg = monthTotal / days;
    const data = [];
    for (let i = 0; i < days; i++) {
        data.push(avg * (1 + (Math.random() - 0.5) * 0.4));
    }
    return data;
}

// 💡 ИСПРАВЛЕНИЕ: Функция fetchData теперь использует GET и передает userId в URL
async function fetchData(userId) {
    // Формируем URL с параметром запроса
    const STAT_ENDPOINT = `/stat/api?user_id=${userId}`;

    try {
        // Метод изменен на GET
        const response = await fetch(STAT_ENDPOINT, {
            method: 'GET',
            headers: {
                // Content-Type: application/json не нужен для GET, но не повредит
                'Content-Type': 'application/json'
            }
            // Тело (body) удалено
        });

        if (!response.ok) {
            throw new Error(`Ошибка сети или сервера: ${response.status} ${response.statusText}`);
        }

        const rawData = await response.json();

        // 💡 Адаптация и обработка полученных данных
        const today = rawData.today || 0;
        const yesterday = rawData.yesterday || 0;
        const week = rawData.week || rawData.week_sales || 0;
        const month = rawData.month || 0;

        const dailyData = rawData.daily_data || generateDailyDataFromMonthTotal(month, 30);

        return {
            today: today,
            yesterday: yesterday,
            week: week,
            month: month,
            all: month + week + today,
            dailyData: dailyData
        };

    } catch (error) {
        console.error("Ошибка при получении статистики:", error);
        alert(`Не удалось загрузить данные статистики. Проверьте консоль. Ошибка: ${error.message}`);
        return { today: 0, yesterday: 0, week: 0, month: 0, all: 0, dailyData: [] };
    }
}

// ... (Функция processAndDisplayStats остается без изменений) ...
function processAndDisplayStats(data) {
    const duration = 1500;

    const dailyDataLength = data.dailyData.length || 1;

    const averageDailySales = data.month / dailyDataLength;

    const compareToAverage = (currentSales, elementId) => {
        const diff = currentSales - averageDailySales;
        const percent = (diff / averageDailySales) * 100;
        const element = document.getElementById(elementId);

        const sign = percent > 0 ? '↑' : (percent < 0 ? '↓' : '—');

        element.classList.remove('up', 'down');
        element.classList.add(percent > 0 ? 'up' : (percent < 0 ? 'down' : ''));

        element.textContent = `${sign} ${Math.abs(percent).toFixed(2)}%`;
    };

    animateValue(document.getElementById('total-sales'), 0, data.all, duration);
    animateValue(document.getElementById('today-sales'), 0, data.today, duration);
    animateValue(document.getElementById('yesterday-sales'), 0, data.yesterday, duration);
    animateValue(document.getElementById('week-sales'), 0, data.week, duration);
    animateValue(document.getElementById('month-sales'), 0, data.month, duration);

    compareToAverage(data.today, 'today-vs-avg');
    compareToAverage(data.yesterday, 'yesterday-vs-avg');

    document.getElementById('last-updated').textContent = new Date().toLocaleTimeString();

    document.body.classList.remove('is-loading');
}


// ----------------------------------------------------
// 💡 ИСПРАВЛЕНИЕ: ГЛАВНАЯ ФУНКЦИЯ РЕНДЕРИНГА
// ----------------------------------------------------

function renderStatistics() {

    // 1. Получаем текущий URL-адрес
    const urlParams = new URLSearchParams(window.location.search);

    // 2. Извлекаем user_id из параметра запроса 'user_id'
    const userId = urlParams.get('user_id');

    // 3. Выводим ID алертом (по вашему запросу)
    if (userId) {
        alert("Получен ID пользователя: " + userId);
    }

    if (!userId) {
        alert("Ошибка: ID пользователя не найден в URL-параметрах.");
        document.body.classList.remove('is-loading');
        return;
    }

    // 4. Запускаем загрузку данных
    fetchData(userId)
        .then(stats => {
            processAndDisplayStats(stats);
        })
        .catch(error => {
            // Ошибки уже обрабатываются внутри fetchData, но на всякий случай
            document.body.classList.remove('is-loading');
        });
}

// Инициализация при загрузке страницы
document.body.classList.add('is-loading'); // Активируем Skeleton Loader
renderStatistics();