function initEnhancer() {
    const items = document.querySelectorAll('.horizontal-item');

    items.forEach((item, i) => {
        // Проверка, чтобы не создать кнопку повторно
        if (item.querySelector('.auto-reprice-btn')) return;

        // Находим блок кнопок
        const actions = item.querySelector('.lots-buttons, .item-buttons, .buttons, .actions');
        if (!actions) return;

        // ===== КНОПКА =====
        const btn = document.createElement('button');
        btn.innerText = "AutoPrice";
        btn.className = "auto-reprice-btn";
        btn.style.cssText = `
            background: linear-gradient(135deg, #ffcc00, #ff6600);
            border: none;
            padding: 6px 12px;
            margin-left: 6px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            color: #000;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        `;
        btn.onmouseover = () => btn.style.transform = "scale(1.05)";
        btn.onmouseleave = () => btn.style.transform = "scale(1)";

        actions.appendChild(btn);

        // ===== МОДАЛКА =====
        const modal = document.createElement('div');
        modal.className = "auto-reprice-modal";
        modal.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #1f1f2e;
            border: 2px solid #ffcc00;
            padding: 20px;
            border-radius: 12px;
            width: 320px;
            z-index: 999999;
            display: none;
            color: white;
            font-size: 15px;
            box-shadow: 0 0 15px rgba(0,0,0,0.6);
            animation: fadeIn 0.3s ease;
        `;

        modal.innerHTML = `
            <h2 style="margin:0 0 12px; text-align:center;">AutoPrice Settings</h2>

            <label style="display:flex;align-items:center;margin-bottom:10px;">
                <input type="checkbox" id="enable_${i}" style="margin-right:8px;">
                Включить авторепрайс
            </label>

            <p style="margin:0 0 4px;">Минимальная цена (стоп-лосс):</p>
            <input id="min_${i}" type="number" step="0.01" min="0" style="
                width:100%;padding:6px;border-radius:6px;border:none;margin-bottom:12px;
            ">

            <button id="save_${i}" style="
                width:100%;padding:8px;
                background: linear-gradient(135deg, #00ffcc, #0066ff);
                color:black;font-weight:bold;
                border-radius:6px;border:none;cursor:pointer;
                margin-bottom:6px;
                transition: transform 0.2s ease;
            ">Сохранить</button>

            <button id="close_${i}" style="
                width:100%;padding:8px;
                background:#333;color:white;border:none;
                border-radius:6px;cursor:pointer;
                transition: transform 0.2s ease;
            ">Закрыть</button>
        `;

        document.body.appendChild(modal);

        // ===== ОТКРЫТИЕ МОДАЛКИ =====
        btn.addEventListener("click", () => modal.style.display = "block");

        // ===== ЗАКРЫТИЕ МОДАЛКИ =====
        modal.querySelector(`#close_${i}`).onclick = () => {
            modal.style.display = "none";
        };

        // Закрытие при клике вне модалки
        window.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = "none";
            }
        });

        // ===== СОХРАНЕНИЕ НА СЕРВЕР =====
        async function getUserId() {
            return new Promise(resolve => {
                chrome.storage.local.get(['user_id'], (result) => resolve(result.user_id));
            });
        }

        modal.querySelector(`#save_${i}`).onclick = async () => {
            const enabled = modal.querySelector(`#enable_${i}`).checked;
            const min = parseFloat(modal.querySelector(`#min_${i}`).value);
            const skin_id = parseInt(item.dataset.id);

            const user_id = await getUserId();
            if (!user_id) {
                alert("User ID не найден!");
                return;
            }

            try {
                const response = await fetch('http://localhost:8000/save_settings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id,
                        skin_id,
                        enabled,
                        min
                    })
                });
                const data = await response.json();
                if (data.status) {
                    alert("Настройки успешно сохранены!");
                } else {
                    alert("Ошибка при сохранении на сервере");
                }
            } catch (err) {
                alert("Ошибка сети: " + err);
            }

            modal.style.display = "none";
        };
    });
}

// Запуск с ожиданием загрузки контента
setTimeout(initEnhancer, 1500);
setInterval(initEnhancer, 2000);
