const server_url = "http://127.0.0.1:8000/users/get_api";

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