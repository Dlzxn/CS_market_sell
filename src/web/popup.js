const server_url = "http://185.197.75.72:8000/users/get_api";

// Получаем ссылки на оба блока
const apiBlock = document.getElementById("api-block");
const appMainBlock = document.getElementById("app-main");

document.addEventListener("DOMContentLoaded", () => {

    // 💡 ШАГ 1: Скрываем ОБА блока при загрузке DOM, чтобы избежать "мерцания"
    apiBlock.classList.add("hidden");
    appMainBlock.classList.add("hidden");

    chrome.storage.local.get(["api_key", "user_id"], data => {

        if (data.api_key) {
            // Если API нет → показываем ТОЛЬКО ввод
            showApiInput();
        } else {
            // Если API есть → показываем ТОЛЬКО информацию
            appMainBlock.classList.remove("hidden");
            document.getElementById("uid").innerText = data.user_id || "Не получен";
        }

    });

});

function showApiInput() {
    // Эта функция вызывается ТОЛЬКО когда api_key нет.
    // Она удаляет класс .hidden, делая блок #api-block видимым.
    apiBlock.classList.remove("hidden");

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