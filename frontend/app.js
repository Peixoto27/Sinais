// Variáveis globais
let allSignals = [];
let activeAlerts = JSON.parse(localStorage.getItem('sinaisProAlerts') || '[]');
let activeTimeframe = '1d';
let currentSignalsOnScreen = new Map();

// Ícones das moedas
const coinIcons = {
    'BTC/USDT': 'https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@latest/svg/color/btc.svg',
    'ETH/USDT': 'https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@latest/svg/color/eth.svg',
    'XRP/USDT': 'https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@latest/svg/color/xrp.svg',
    'SOL/USDT': 'https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@latest/svg/color/sol.svg',
    'ADA/USDT': 'https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@latest/svg/color/ada.svg',
    'default': 'https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@latest/svg/color/generic.svg'
};

// Login
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('login-button').addEventListener('click', checkPassword);
    document.getElementById('password-input').addEventListener('keyup', e => {
        if (e.key === 'Enter') checkPassword();
    });
});

function checkPassword() {
    const senha = document.getElementById('password-input').value;
    if (senha === "ope1001") {
        document.getElementById('login-screen').style.display = 'none';
        document.getElementById('app').style.display = 'block';
        initializeApp();
    } else {
        alert('Senha incorreta.');
        document.getElementById('password-input').value = '';
    }
}

// Inicialização
function initializeApp() {
    setupEventListeners();
    loadAlertsFromStorage();
    fetchAndDisplaySignals(activeTimeframe);
    setInterval(() => fetchAndDisplaySignals(activeTimeframe), 30000);
}

// Eventos
function setupEventListeners() {
    document.querySelectorAll('.timeframe-selector button').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.timeframe-selector button').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeTimeframe = btn.dataset.timeframe;
            currentSignalsOnScreen.clear();
            document.getElementById('signals-container').innerHTML = '';
            fetchAndDisplaySignals(activeTimeframe);
        });
    });

    document.getElementById('signal-filter').addEventListener('change', applyFilters);
    document.getElementById('refresh-btn').addEventListener('click', () => fetchAndDisplaySignals(activeTimeframe));
    document.getElementById('alerts-btn').addEventListener('click', openAlertsModal);
    document.querySelectorAll('.close').forEach(btn => btn.addEventListener('click', closeModals));
    document.getElementById('add-alert').addEventListener('click', addAlert);
    window.addEventListener('click', e => {
        document.querySelectorAll('.modal').forEach(modal => {
            if (e.target === modal) modal.style.display = 'none';
        });
    });
}

// Fetch e render
async function fetchAndDisplaySignals(timeframe) {
    const url = `https://sinais-production.up.railway.app/signals?timeframe=${timeframe}`;
    const container = document.getElementById('signals-container');

    if (currentSignalsOnScreen.size === 0) {
        container.innerHTML = `<div class="loading"><i class="fas fa-spinner"></i> Analisando timeframe ${timeframe}...</div>`;
    }

    try {
        const res = await fetch(url);
        const signals = await res.json();
        allSignals = signals;
        updateSignalsSmooth(signals);
        updateLastUpdatedTimestamp();
        checkAlerts(signals);
    } catch (e) {
        container.innerHTML = `<div class="error"><i class="fas fa-exclamation-triangle"></i> Erro ao carregar sinais</div>`;
    }
}

// Atualização suave
function updateSignalsSmooth(newSignals) {
    const container = document.getElementById('signals-container');
    if (newSignals.length === 0) {
        container.innerHTML = `<div class="error"><i class="fas fa-info-circle"></i> Nenhum sinal encontrado.</div>`;
        currentSignalsOnScreen.clear();
        return;
    }

    document.querySelector('.loading')?.remove();
    const newMap = new Map();
    newSignals.forEach(signal => {
        if (signal.signal !== 'ERROR') newMap.set(signal.pair, signal);
    });

    newMap.forEach((newSignal, pair) => {
        const card = document.querySelector(`[data-pair="${pair}"]`);
        if (card) {
            const old = currentSignalsOnScreen.get(pair);
            if (hasSignalChanged(old, newSignal)) updateExistingCard(card, newSignal);
        } else {
            const newCard = createSignalCard(newSignal);
            container.appendChild(newCard);
        }
        currentSignalsOnScreen.set(pair, newSignal);
    });

    currentSignalsOnScreen.forEach((_, pair) => {
        if (!newMap.has(pair)) {
            document.querySelector(`[data-pair="${pair}"]`)?.remove();
            currentSignalsOnScreen.delete(pair);
        }
    });
}

function hasSignalChanged(a, b) {
    return !a || a.price !== b.price || a.signal !== b.signal || a.confidence !== b.confidence || JSON.stringify(a.indicators) !== JSON.stringify(b.indicators);
}

// Card com alvo
function createSignalCard(signal) {
    const card = document.createElement('div');
    card.className = 'signal-card';
    card.setAttribute('data-pair', signal.pair);

    let tipo = signal.signal.toUpperCase();
    if (tipo.includes("BUY")) tipo = "BUY";
    else if (tipo.includes("SELL")) tipo = "SELL";
    else tipo = "HOLD";

    const icon = tipo === "BUY" ? "fa-arrow-trend-up" : tipo === "SELL" ? "fa-arrow-trend-down" : "fa-clock";
    const iconUrl = coinIcons[signal.pair] || coinIcons.default;

    const confNum = parseInt(signal.confidence.split('/')[0]);
    const confColor = confNum >= 7 ? "#34c759" : confNum >= 5 ? "#ff9500" : "#ff3b30";
    const alvo = calcularAlvo(signal);

    card.innerHTML = `
        <div class="card-header">
            <div class="coin-info">
                <img src="${iconUrl}" class="coin-icon" />
                <div class="coin-details">
                    <h3>${signal.pair}</h3>
                    <div class="coin-price">$${signal.price}</div>
                    <div class="coin-target">🎯 Alvo: $${alvo.valor} (${alvo.percentual}%)</div>
                </div>
            </div>
            <div class="confidence-badge" style="color:${confColor}; border-color:${confColor};">${signal.confidence}</div>
        </div>
        <div class="signal-display signal-${tipo}">
            <div class="signal-text signal-${tipo}"><i class="fas ${icon}"></i> ${signal.signal}</div>
            <div class="signal-description">${getSignalDescription(signal.signal, confNum)}</div>
        </div>
        <div class="indicators-section">
            <div class="indicators-grid">
                <div class="indicator-item"><span class="indicator-label">RSI</span><span class="indicator-value">${signal.indicators.rsi}</span></div>
                <div class="indicator-item"><span class="indicator-label">MACD</span><span class="indicator-value">${signal.indicators.macd}</span></div>
                <div class="indicator-item"><span class="indicator-label">B. Sup</span><span class="indicator-value">${signal.indicators.bollinger_upper}</span></div>
                <div class="indicator-item"><span class="indicator-label">B. Inf</span><span class="indicator-value">${signal.indicators.bollinger_lower}</span></div>
            </div>
        </div>
    `;
    return card;
}

// Atualização parcial do card
function updateExistingCard(el, s) {
    el.querySelector('.coin-price').textContent = `$${s.price}`;
    const confEl = el.querySelector('.confidence-badge');
    const confNum = parseInt(s.confidence.split('/')[0]);
    const confColor = confNum >= 7 ? "#34c759" : confNum >= 5 ? "#ff9500" : "#ff3b30";
    confEl.textContent = s.confidence;
    confEl.style.color = confColor;
    confEl.style.borderColor = confColor;

    const tipo = s.signal.toUpperCase().includes("BUY") ? "BUY" : s.signal.toUpperCase().includes("SELL") ? "SELL" : "HOLD";
    const icon = tipo === "BUY" ? "fa-arrow-trend-up" : tipo === "SELL" ? "fa-arrow-trend-down" : "fa-clock";
    const alvo = calcularAlvo(s);

    el.querySelector('.signal-display').className = `signal-display signal-${tipo}`;
    el.querySelector('.signal-text').className = `signal-text signal-${tipo}`;
    el.querySelector('.signal-text').innerHTML = `<i class="fas ${icon}"></i> ${s.signal}`;
    el.querySelector('.signal-description').textContent = getSignalDescription(s.signal, confNum);
    el.querySelector('.coin-target').textContent = `🎯 Alvo: $${alvo.valor} (${alvo.percentual}%)`;

    const indicators = el.querySelectorAll('.indicator-value');
    indicators[0].textContent = s.indicators.rsi;
    indicators[1].textContent = s.indicators.macd;
    indicators[2].textContent = s.indicators.bollinger_upper;
    indicators[3].textContent = s.indicators.bollinger_lower;
}

// Lógica alvo por confiança
function calcularAlvo(signal) {
    const preco = signal.price;
    const conf = parseInt(signal.confidence.split('/')[0]);
    let perc = conf >= 8 ? 6 : conf >= 6 ? 4 : conf >= 4 ? 2 : 1;
    let valor = preco;

    if (signal.signal.toUpperCase().includes("BUY")) {
        valor = preco * (1 + perc / 100);
    } else if (signal.signal.toUpperCase().includes("SELL")) {
        valor = preco * (1 - perc / 100);
    }

    return { valor: valor.toFixed(4), percentual: perc };
}

function getSignalDescription(txt, conf) {
    if (txt.includes("BUY")) return conf >= 7 ? "Sinal forte de compra" : "Tendência de alta, aguarde confirmação";
    if (txt.includes("SELL")) return conf >= 7 ? "Sinal forte de venda" : "Tendência de baixa, aguarde confirmação";
    return "Mercado em consolidação";
}

function applyFilters() {
    const filtro = document.getElementById('signal-filter').value;
    const sinais = filtro === 'all' ? allSignals : allSignals.filter(s => s.signal.includes(filtro));
    const container = document.getElementById('signals-container');
    container.innerHTML = '';
    currentSignalsOnScreen.clear();
    sinais.forEach(signal => {
        const card = createSignalCard(signal);
        container.appendChild(card);
        currentSignalsOnScreen.set(signal.pair, signal);
    });
}

function openAlertsModal() {
    document.getElementById('alerts-modal').style.display = 'block';
    displayActiveAlerts();
}

function closeModals() {
    document.querySelectorAll('.modal').forEach(m => m.style.display = 'none');
}

function addAlert() {
    const pair = document.getElementById('alert-pair').value;
    const price = parseFloat(document.getElementById('alert-price').value);
    const condition = document.getElementById('alert-condition').value;

    if (!pair || !price) return alert('Preencha todos os campos.');

    activeAlerts.push({ id: Date.now(), pair, price, condition, created: new Date().toLocaleString() });
    saveAlertsToStorage();
    displayActiveAlerts();
    document.getElementById('alert-pair').value = '';
    document.getElementById('alert-price').value = '';
}

function removeAlert(id) {
    activeAlerts = activeAlerts.filter(a => a.id !== id);
    saveAlertsToStorage();
    displayActiveAlerts();
}

function displayActiveAlerts() {
    const container = document.getElementById('alerts-list');
    if (activeAlerts.length === 0) {
        container.innerHTML = '<p style="text-align:center;color:#777">Nenhum alerta ativo</p>';
        return;
    }
    container.innerHTML = activeAlerts.map(a => `
        <div class="alert-item">
            <div>
                <strong>${a.pair}</strong> ${a.condition === 'above' ? 'acima de' : 'abaixo de'} $${a.price}
                <br><small>${a.created}</small>
            </div>
            <button onclick="removeAlert(${a.id})">Remover</button>
        </div>`).join('');
}

function checkAlerts(signals) {
    activeAlerts.forEach(alert => {
        const signal = signals.find(s => s.pair === alert.pair);
        if (!signal) return;

        const preco = signal.price;
        if ((alert.condition === 'above' && preco >= alert.price) || (alert.condition === 'below' && preco <= alert.price)) {
            showNotification(`Alerta: ${alert.pair} atingiu $${preco}`);
            removeAlert(alert.id);
        }
    });
}

function showNotification(msg) {
    if ("Notification" in window) {
        if (Notification.permission === "granted") {
            new Notification("Sinais Pro", { body: msg });
        } else if (Notification.permission !== "denied") {
            Notification.requestPermission().then(p => {
                if (p === "granted") new Notification("Sinais Pro", { body: msg });
            });
        }
    }
    alert(msg);
}

function saveAlertsToStorage() {
    localStorage.setItem('sinaisProAlerts', JSON.stringify(activeAlerts));
}

function loadAlertsFromStorage() {
    const saved = localStorage.getItem('sinaisProAlerts');
    if (saved) activeAlerts = JSON.parse(saved);
}

function updateLastUpdatedTimestamp() {
    const el = document.getElementById('last-updated-timestamp');
    if (el) el.textContent = `Última atualização: ${new Date().toLocaleTimeString()}`;
}
