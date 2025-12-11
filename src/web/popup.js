const server_url = "https://salesinovbot1488.ru/users/get_api";

// Получаем ссылки на оба блока
const apiBlock = document.getElementById("api-block");
const appMainBlock = document.getElementById("app-main");
// 💡 ПОЛУЧАЕМ ССЫЛКУ НА КНОПКУ ПОВТОРНОГО ВХОДА (ID, который должен быть в popup.html)
const reloginBtn = document.getElementById("relogin-btn");

document.addEventListener("DOMContentLoaded", () => {

    // 💡 ШАГ 1: Скрываем ОБА блока при загрузке DOM, чтобы избежать "мерцания"
    apiBlock.classList.add("hidden");
    appMainBlock.classList.add("hidden");

    chrome.storage.local.get(["api_key", "user_id"], data => {

        if (!data.api_key) {
            // Если API нет → показываем ТОЛЬКО ввод
            showApiInput();
        } else {
            // Если API есть → показываем ТОЛЬКО информацию
            appMainBlock.classList.remove("hidden");
            document.getElementById("uid").innerText = data.user_id || "Не получен";
            setupStatsButton(data.user_id);
        }
    });

    // 💡 ШАГ 2: ОБРАБОТЧИК КНОПКИ ПОВТОРНОГО ВХОДА
    if (reloginBtn) {
        reloginBtn.onclick = () => {
            if (confirm("Вы уверены, что хотите сменить API-KEY? Для применения сброса расширение будет перезагружено.")) {
                // Удаляем сохраненные данные, чтобы сбросить авторизацию
                chrome.storage.local.remove(["api_key", "user_id"], () => {
                    // Перезагружаем расширение, чтобы выполнить логику проверки авторизации заново
                    location.reload();
                });
            }
        };
    }
});

function showApiInput() {
    // Эта функция вызывается ТОЛЬКО когда api_key нет.
    // Она удаляет класс .hidden, делая блок #api-block видимым.
    apiBlock.classList.remove("hidden");

    // Очищаем поле ввода на случай, если пользователь вернулся после ошибки
    document.getElementById("api-input").value = '';

    document.getElementById("api-save-btn").onclick = () => {
        // Логика сохранения API ключа остается без изменений
        const api_value = document.getElementById("api-input").value.trim();
        if (!api_value) return alert("Введите ключ");

        fetch(server_url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ api_key: api_value })
        })
        .then(res => res.json())
        .then(result => {
            if (result.status === true) {
                chrome.storage.local.set({
                    api_key: api_value,
                    user_id: result.user_id
                });
                alert("API подтверждён!");
                location.reload();
            } else alert("❗ Неверный API ключ");
        })
        .catch(() => alert("Ошибка соединения с сервером"));
    };
}
const STATS_PAGE_URL = "https://salesinovbot1488.ru/stat/info";
const statsBtn = document.getElementById("stats-btn");

/**
 * Назначает обработчик клика кнопке статистики.
 *
 * @param {string | null} userId ID пользователя, полученный из chrome.storage.
 */
function setupStatsButton(userId) {
    if (!statsBtn) {
        console.error("Кнопка статистики с ID 'stats-btn' не найдена.");
        return;
    }

    // 1. Проверяем, есть ли валидный ID
    if (!userId) {
         statsBtn.disabled = true;
         statsBtn.textContent = "Статистика (ID не найден)";
         // Убедимся, что на кнопке нет обработчика, если она неактивна
         statsBtn.onclick = null;
         return;
    }

    // 2. Если ID есть, делаем кнопку активной и назначаем обработчик клика
    statsBtn.disabled = false;
    statsBtn.textContent = "Статистика Продаж 📈"; // Восстанавливаем оригинальный текст

    statsBtn.onclick = () => {
        // userId гарантированно существует и передано как аргумент
        const url = `${STATS_PAGE_URL}?user_id=${userId}`;

        // Открываем новую вкладку
        chrome.tabs.create({ url: url });
    };
}