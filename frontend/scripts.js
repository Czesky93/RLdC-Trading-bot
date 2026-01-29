const ranges = {
  "24h": { roi: 3.89, capital: 379, volatility: 2.38, buy: 6, sell: 3 },
  "7d": { roi: 5.22, capital: 412, volatility: 2.95, buy: 12, sell: 5 },
  "30d": { roi: 8.11, capital: 502, volatility: 3.21, buy: 18, sell: 7 }
};

const formatNumber = (value, decimals = 2) => value.toFixed(decimals);

const updateMetrics = (rangeKey) => {
  const data = ranges[rangeKey];
  if (!data) {
    return;
  }

  document.querySelector("[data-value='roi']").textContent = formatNumber(data.roi);
  document.querySelector("[data-value='capital']").textContent = data.capital;
  document.querySelector("[data-value='volatility']").textContent = formatNumber(data.volatility);

  const footer = document.querySelector(".card-footer");
  footer.children[0].querySelector("strong").textContent = data.buy;
  footer.children[1].querySelector("strong").textContent = data.sell;
};

const setRingProgress = (element, value) => {
  const safeValue = Math.min(100, Math.max(0, value));
  const degrees = safeValue * 3.6;
  element.style.background = `conic-gradient(var(--accent) ${degrees}deg, rgba(255, 255, 255, 0.08) ${degrees}deg)`;
};

const setProgressBar = (element, value) => {
  element.style.width = `${value}%`;
};

const initializeTabs = () => {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((button) => button.classList.remove("is-active"));
      tab.classList.add("is-active");
      updateMetrics(tab.dataset.range);
    });
  });
};

const initializeRings = () => {
  document.querySelectorAll("[data-ring]").forEach((ring) => {
    setRingProgress(ring, Number(ring.dataset.ring));
  });
};

const initializeProgress = () => {
  const progressBar = document.querySelector(".progress-bar");
  if (progressBar) {
    const progressValue = Number(progressBar.dataset.progress);
    setProgressBar(progressBar, progressValue);
  }
};

const randomizeTicker = () => {
  const rows = document.querySelectorAll("[data-ticker] .ticker-row");
  rows.forEach((row) => {
    const value = (Math.random() * 4 - 2).toFixed(2);
    const display = `${value > 0 ? "+" : ""}${value}%`;
    const label = row.querySelector("span:last-child");
    label.textContent = display;
    label.classList.toggle("pos", value >= 0);
    label.classList.toggle("neg", value < 0);
  });
};

initializeTabs();
initializeRings();
initializeProgress();
updateMetrics("24h");
setInterval(randomizeTicker, 4000);
