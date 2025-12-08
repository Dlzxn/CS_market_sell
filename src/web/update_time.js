// Переменные, используемые в settings.js
const UPDATE_URL = "http://127.0.0.1:8000/users/updates_time";

// Добавляем слушатель событий после загрузки DOM
document.addEventListener("DOMContentLoaded", () => {

    const saveButton = document.getElementById("settings-save-btn");

    if (saveButton) {
        saveButton.onclick = handleSettingsSave;
    }

    // Проверка минимального значения при изменении
    const intervalInput = document.getElementById("check-interval-input");
    if (intervalInput) {
        intervalInput.onchange = () => {
            const value = parseInt(intervalInput.value);
            // Если введено число меньше 15, устанавливаем 15
            if (value < 15) {
                intervalInput.value = 15;
            }
        };
    }
});


function handleSettingsSave() {

    const intervalInput = document.getElementById("check-interval-input");
    const saveStatusSpan = document.getElementById("save-status");

    // 1. Получаем значение и проверяем лимиты
    const checkInterval = parseInt(intervalInput.value);

    if (isNaN(checkInterval) || checkInterval < 15) {
        alert("Интервал проверки должен быть не менее 15 секунд.");
        return;
    }

    // 2. Получаем user_id для отправки
    chrome.storage.local.get("user_id", data => {

        const userId = data.user_id;
        alert(userId)
        if (!userId) {
            alert("Ошибка: ID пользователя не найден. Авторизуйтесь снова.");
            return;
        }

        // 3. Отправка POST-запроса на сервер
        fetch(UPDATE_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                user_id: userId,
                // Отправляем одно фиксированное значение
                check_interval: checkInterval
            })
        })
        .then(res => {
             if (!res.ok) {
                throw new Error(`Server responded with status ${res.status}`);
            }
            return res.json();
        })
        .then(result => {
            if (result.status === true) {
                // Успех: показываем статус сохранения
                if (saveStatusSpan) {
                    saveStatusSpan.innerText = "Настройки сохранены!";
                    saveStatusSpan.style.display = "block";
                    setTimeout(() => {
                        saveStatusSpan.style.display = "none";
                    }, 3000);
                }
            } else {
                alert(`Ошибка сервера: ${result.message || "Не удалось сохранить настройки"}`);
            }
        })
        .catch(error => {
            console.error("Fetch error:", error);
            alert(`Ошибка соединения: ${error.message}`);
        });

    });
}