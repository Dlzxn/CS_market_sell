function initEnhancer() {
    const items = document.querySelectorAll('.horizontal-item');

    items.forEach((item, i) => {
        if (item.querySelector('.auto-reprice-btn')) return;

        const actions = item.querySelector('.lots-buttons, .item-buttons, .buttons, .actions');
        if (!actions) return;

        // ===== Получаем ID скина =====
        const link = item.querySelector('a.name.ng-star-inserted');
        if (!link) return;
        const href = link.getAttribute('href');
        const idMatch = href.match(/id=(\d+)/);
        if (!idMatch) return;
        const skin_id = idMatch[1];

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

        // ===== ОТКРЫТИЕ / ЗАКРЫТИЕ МОДАЛКИ =====
        btn.addEventListener("click", () => modal.style.display = "block");
        modal.querySelector(`#close_${i}`).onclick = () => modal.style.display = "none";
        window.addEventListener('click', (e) => { if (e.target === modal) modal.style.display = "none"; });

        // ===== СОХРАНЕНИЕ НА СЕРВЕР =====
        async function getUserId() {
            return new Promise(resolve => {
                chrome.storage.local.get(['user_id'], (result) => resolve(result.user_id));
            });
        }

        modal.querySelector(`#save_${i}`).onclick = async () => {
            const enabled = modal.querySelector(`#enable_${i}`).checked;
            const min = parseFloat(modal.querySelector(`#min_${i}`).value);

            const user_id = await getUserId();
            if (!user_id) {
                alert("User ID не найден!");
                return;
            }

            try {
                const response = await fetch('https://salesinovbot1488.ru/users/update_skin', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id, skin_id, enabled, min })
                });
                const data = await response.json();

                if (data.status) {
                    alert(`Скин ${skin_id} успешно обновлён!`);
                } else {
                    alert(`Ошибка обновления скина ${skin_id}: ${data.error || 'неизвестная ошибка'}`);
                }
            } catch (err) {
                alert("Ошибка сети: " + err);
            }

            modal.style.display = "none";
        };
    });
}

// Запуск
setTimeout(initEnhancer, 1500);
setInterval(initEnhancer, 2000);
