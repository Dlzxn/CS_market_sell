const SERVER_URL = "http://localhost:8000/api/update";

// Создаём UI-блок под карточкой
function addRepriceUI(card) {
    // проверяем, чтобы UI не дублировался
    if (card.nextElementSibling && card.nextElementSibling.classList.contains("reprice-ui-wrapper")) return;

    const wrapper = document.createElement("div");
    wrapper.className = "reprice-ui-wrapper";
    wrapper.style.margin = "4px 0 12px 0";  // немного пространства
    wrapper.style.background = "#2a2a40";
    wrapper.style.padding = "6px";
    wrapper.style.borderRadius = "5px";
    wrapper.style.display = "flex";
    wrapper.style.flexDirection = "column";
    wrapper.style.gap = "6px";

    // Переключатель репрайса
    const switchLabel = document.createElement("label");
    switchLabel.style.display = "flex";
    switchLabel.style.alignItems = "center";
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.style.marginRight = "6px";
    switchLabel.appendChild(checkbox);
    switchLabel.appendChild(document.createTextNode("Вкл/Выкл репрайс"));

    // Поле стоп-цены
    const stopInput = document.createElement("input");
    stopInput.type = "number";
    stopInput.min = "0";
    stopInput.step = "0.01";
    stopInput.placeholder = "Минимальная цена (стоп-цена)";
    stopInput.style.padding = "4px";
    stopInput.style.borderRadius = "4px";
    stopInput.style.border = "none";
    stopInput.style.width = "100%";

    // Кнопка подтвердить
    const btn = document.createElement("button");
    btn.textContent = "Подтвердить";
    btn.style.padding = "6px";
    btn.style.background = "#f5a623";
    btn.style.color = "#1e1e2f";
    btn.style.border = "none";
    btn.style.borderRadius = "4px";
    btn.style.cursor = "pointer";

    btn.addEventListener("click", async (e) => {
        e.stopPropagation(); // ОЧЕНЬ ВАЖНО! чтобы не сработал click карточки
        const productNameElem = card.querySelector(".name");
        const productName = productNameElem ? productNameElem.textContent.trim() : "Unknown";
        const data = {
            product: productName,
            enabled: checkbox.checked,
            stopPrice: parseFloat(stopInput.value) || 0
        };

        try {
            const res = await fetch(SERVER_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
            if (res.ok) {
                btn.textContent = "Отправлено ✔";
                setTimeout(() => { btn.textContent = "Подтвердить"; }, 1500);
            } else {
                btn.textContent = "Ошибка ❌";
            }
        } catch (err) {
            console.error(err);
            btn.textContent = "Ошибка ❌";
        }
    });

    wrapper.appendChild(switchLabel);
    wrapper.appendChild(stopInput);
    wrapper.appendChild(btn);

    // Вставляем после карточки
    card.parentNode.insertBefore(wrapper, card.nextSibling);
}

// Функция обхода карточек
function scanCards() {
    const cards = document.querySelectorAll("div.left");
    cards.forEach(addRepriceUI);
}

// MutationObserver для динамически подгружаемых товаров
const observer = new MutationObserver(scanCards);
observer.observe(document.body, { childList: true, subtree: true });

// Запуск один раз
scanCards();
