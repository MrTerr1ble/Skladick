// Показывает всплывающее уведомление
let alertElements = []; // храним ссылки на все активные алерты

function showAlertPopup(a) {
  const div = document.createElement("div");
  div.className = "alert-popup";
  div.style.position = "fixed";
  div.style.right = "20px";
  div.style.background = "#fff4f4";
  div.style.border = "1px solid #d64545";
  div.style.borderLeft = "5px solid #d64545";
  div.style.padding = "12px 18px";
  div.style.borderRadius = "8px";
  div.style.boxShadow = "0 2px 8px rgba(0,0,0,0.1)";
  div.style.zIndex = 10000;
  div.style.maxWidth = "350px";
  div.style.width = "100%";
  div.style.transition = "bottom 0.3s ease"; // плавная анимация

  const location = a.location && a.location !== "—" ? a.location : "—";
  const message = a.message ? `${a.message}<br>` : "";
  const severityColor = {
    INFO: "#0e4aa8",
    WARN: "#f0ad4e",
    CRIT: "#d64545",
  }[a.severity_code] || "#d64545";

  div.innerHTML = `
    <strong>⚠ ${a.item}</strong><br>
    ${message}
    Остаток: ${a.current_qty} ${a.uom} (${a.warehouse}/${location})<br>
    <span style="color:${severityColor};font-weight:600;">${a.severity}</span><br>
    <button class="btn" style="margin-top:6px;" onclick="window.location.href='/thresholds/alerts/'">Перейти в Контроль</button>
  `;

  // Добавляем алерт в массив и обновляем позиции
  alertElements.push(div);
  document.body.appendChild(div);

  // Обновляем позиции всех алертов
  updateAlertPositions();

  setTimeout(() => {
    // Удаляем алерт из массива и из DOM
    const index = alertElements.indexOf(div);
    if (index > -1) {
      alertElements.splice(index, 1);
    }
    div.remove();

    // Обновляем позиции оставшихся алертов
    updateAlertPositions();
  }, 10000);
}

// Обновляет позиции всех видимых алертов
function updateAlertPositions() {
  const alertHeight = 160; // высота алерта + отступ
  alertElements.forEach((alert, index) => {
    alert.style.bottom = `${20 + index * alertHeight}px`;
  });
}

// Периодически проверяет новые алерты
let lastAlertIds = new Set();

async function checkAlerts() {
  try {
    const r = await fetch("/thresholds/alerts/api/", {
      credentials: "same-origin",
      headers: { Accept: "application/json" },
    });

    if (!r.ok) {
      throw new Error(`HTTP ${r.status}`);
    }

    const alerts = await r.json();

    for (const a of alerts) {
      if (!lastAlertIds.has(a.id)) {
        showAlertPopup(a);
        lastAlertIds.add(a.id);
      }
    }

    if (lastAlertIds.size > 100) {
      const keep = new Set(alerts.map((a) => a.id));
      for (const id of lastAlertIds) {
        if (!keep.has(id)) {
          lastAlertIds.delete(id);
        }
      }
    }
  } catch (err) {
    console.error("Ошибка проверки алертов:", err);
  }
}

// каждые 15 секунд
setInterval(checkAlerts, 15000);
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", checkAlerts, { once: true });
} else {
  checkAlerts();
}