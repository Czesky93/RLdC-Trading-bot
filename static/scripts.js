
function register() {
    const username = document.getElementById("register-username").value;
    const password = document.getElementById("register-password").value;
    fetch("/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    }).then(res => res.json()).then(data => alert(data.message));
}

function login() {
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;
    fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    }).then(res => res.json()).then(data => alert(data.message));
}

function connectBinance() {
    const apiKey = document.getElementById("api-key").value;
    const apiSecret = document.getElementById("api-secret").value;
    fetch("/connect_binance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ api_key: apiKey, api_secret: apiSecret }),
    }).then(res => res.json()).then(data => alert(data.message));
}

function getLogs() {
    fetch("/logs").then(res => res.json()).then(data => {
        const logsContainer = document.getElementById("logs-container");
        logsContainer.innerHTML = data.logs.map(log => `<p>${log}</p>`).join("");
    });
}
