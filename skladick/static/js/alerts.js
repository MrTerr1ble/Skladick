// static/js/alerts.js
function showAlertPopup(data) {
  const div = document.createElement("div");
  div.className = "alert-popup";
  div.style.position = "fixed";
  div.style.bottom = "20px";
  div.style.right = "20px";
  div.style.background = "#fff4f4";
  div.style.border = "1px solid #d64545";
  div.style.borderLeft = "5px solid #d64545";
  div.style.padding = "12px 18px";
  div.style.marginTop = "10px";
  div.style.borderRadius = "8px";
  div.style.boxShadow = "0 2px 8px rgba(0,0,0,0.1)";
  div.style.zIndex = 10000;
  div.innerHTML = `
    <strong>⚠ ${data.item}</strong><br>
    ${data.message}<br>
    Остаток: ${data.qty} ${data.uom} (${data.warehouse}/${data.location})<br>
    <button class="btn" style="margin-top:6px;" onclick="window.location.href='/thresholds/alerts/'">Перейти в Контроль</button>
  `;

  // Добавим звук
  const sound = new Audio("/static/sounds/alert.mp3");
  sound.play().catch(() => {});

  document.body.appendChild(div);
  setTimeout(() => div.remove(), 10000);
}

function connectAlerts() {
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  const socket = new WebSocket(`${protocol}://${window.location.host}/ws/alerts/`);

  socket.onmessage = (e) => {
    const data = JSON.parse(e.data);
    showAlertPopup(data);
  };
  socket.onclose = () => setTimeout(connectAlerts, 5000); // авто-переподключение
}

document.addEventListener("DOMContentLoaded", connectAlerts);
