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
            background: #ffcc00;
            border: none;
            padding: 5px 10px;
            margin-left: 6px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
        `;

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
            padding: 18px;
            border-radius: 10px;
            width: 300px;
            z-index: 999999;
            display: none;
            color: white;
            font-size: 15px;
        `;

        modal.innerHTML = `
            <h2 style="margin:0 0 10px">AutoPrice Settings</h2>

            <label style="display:flex;align-items:center;">
                <input type="checkbox" id="enable_${i}" style="margin-right:8px;">
                Включить авторепрайс
            </label>

            <p style="margin:10px 0 4px;">Минимальная цена (стоп-лосс):</p>
            <input id="min_${i}" type="number" step="0.01" min="0" style="
                width:100%;padding:5px;border-radius:6px;border:none;
            ">

            <p style="margin:10px 0 4px;">Интервал проверки (сек):</p>
            <input id="interval_${i}" type="number" value="30" min="5" style="
                width:100%;padding:5px;border-radius:6px;border:none;
            ">

            <button id="save_${i}" style="
                margin-top:10px;width:100%;padding:7px;
                background:#ffcc00;color:black;font-weight:bold;
                border-radius:6px;border:none;cursor:pointer;
            ">Сохранить</button>

            <button id="close_${i}" style="
                margin-top:6px;width:100%;padding:6px;
                background:#333;color:white;border:none;
                border-radius:6px;cursor:pointer;
            ">Закрыть</button>
        `;

        document.body.appendChild(modal);

        // Открытие
        btn.addEventListener("click", () => modal.style.display = "block");

        // Закрытие
        modal.querySelector(`#close_${i}`).onclick = () => {
            modal.style.display = "none";
        };

        // Логика сохранения
        modal.querySelector(`#save_${i}`).onclick = () => {
            const enabled = modal.querySelector(`#enable_${i}`).checked;
            const min = modal.querySelector(`#min_${i}`).value;
            const interval = modal.querySelector(`#interval_${i}`).value;

            console.log(`📌 ITEM #${i}`, { enabled, min, interval });

            modal.style.display = "none"; // можно убрать если хочешь оставлять открытым
        };
    });
}

// Запуск с ожиданием загрузки контента
setTimeout(initEnhancer, 1500);
setInterval(initEnhancer, 2000);
