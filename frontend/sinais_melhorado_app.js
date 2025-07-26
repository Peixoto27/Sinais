// Variáveis globais
let allSignals = [];
let activeAlerts = JSON.parse(localStorage.getItem('sinaisProAlerts') || '[]');
let activeTimeframe = '1d';

// Ícones das moedas
const coinIcons = {
    'BTC/USDT': 'https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@1a63530be6e374711a8554f31b17e4cb92c25669/svg/color/btc.svg',
    'ETH/USDT': 'https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@1a63530be6e374711a8554f31b17e4cb92c25669/svg/color/eth.svg',
    'XRP/USDT': 'https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@1a63530be6e374711a8554f31b17e4cb92c25669/svg/color/xrp.svg',
    'SOL/USDT': 'https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@1a63530be6e374711a8554f31b17e4cb92c25669/svg/color/sol.svg',
    'ADA/USDT': 'https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@1a63530be6e374711a8554f31b17e4cb92c25669/svg/color/ada.svg',
    'default': 'https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@1a63530be6e374711a8554f31b17e4cb92c25669/svg/color/generic.svg'
};

// Inicialização quando a página carrega
document.addEventListener('DOMContentLoaded', () => {
    const loginButton = document.getElementById('login-button');
    const passwordInput = document.getElementById('password-input');

    if (loginButton) {
        loginButton.addEventListener('click', checkPassword);
    }
    if (passwordInput) {
        passwordInput.addEventListener('keyup', (event) => {
            if (event.key === 'Enter') checkPassword();
        });
    }
});

// Função de login
function checkPassword() {
    const correctPassword = "ope1001";
    const enteredPassword = document.getElementById('password-input').value;

    if (enteredPassword === correctPassword) {
        document.getElementById('login-screen').style.display = 'none';
        document.getElementById('app').style.display = 'block';
        initializeApp();
    } else {
        alert('Senha incorreta.');
        document.getElementById('password-input').value = '';
    }
}


// Inicialização da aplicação
function initializeApp() {
    setupEventListeners();
    loadAlertsFromStorage();
    fetchAndDisplaySignals(activeTimeframe);
    
    // Atualização automática a cada 30 segundos
    setInterval(() => {
        fetchAndDisplaySignals(activeTimeframe);
    }, 30000);
}

// Configuração dos event listeners
function setupEventListeners() {
    // Timeframe buttons
    const timeframeButtons = document.querySelectorAll('.timeframe-selector button');
    timeframeButtons.forEach(button => {
        button.addEventListener('click', () => {
            timeframeButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            activeTimeframe = button.dataset.timeframe;
            fetchAndDisplaySignals(activeTimeframe);
        });
    });

    // Filter
    const signalFilter = document.getElementById('signal-filter');
    if (signalFilter) {
        signalFilter.addEventListener('change', applyFilters);
    }

    // Buttons
    const refreshBtn = document.getElementById('refresh-btn');
    const alertsBtn = document.getElementById('alerts-btn');
    
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => fetchAndDisplaySignals(activeTimeframe));
    }
    if (alertsBtn) {
        alertsBtn.addEventListener('click', openAlertsModal);
    }

    // Modal close buttons
    document.querySelectorAll('.close').forEach(closeBtn => {
        closeBtn.addEventListener('click', closeModals);
    });

    // Add alert button
    const addAlertBtn = document.getElementById('add-alert');
    if (addAlertBtn) {
        addAlertBtn.addEventListener('click', addAlert);
    }

    // Close modal when clicking outside
    window.addEventListener('click', (event) => {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    });
}

// Buscar e exibir sinais
async function fetchAndDisplaySignals(timeframe) {
    const apiUrl = `https://sinais-production.up.railway.app/signals?timeframe=${timeframe}`;
    const container = document.getElementById('signals-container');
    
    // Mostrar loading
    container.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner"></i>
            Analisando timeframe ${timeframe}...
        </div>
    `;

    try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
            throw new Error(`Erro na API: ${response.statusText}`);
        }
        
        const signals = await response.json();
        allSignals = signals;
        
        displaySignals(signals);
        updateLastUpdatedTimestamp();
        checkAlerts(signals);
        
    } catch (error) {
        console.error("Erro ao buscar sinais:", error);
        container.innerHTML = `
            <div class="error">
                <i class="fas fa-exclamation-triangle"></i>
                Erro ao carregar sinais: ${error.message}
            </div>
        `;
    }
}

// Exibir sinais na interface
function displaySignals(signals) {
    const container = document.getElementById('signals-container');
    container.innerHTML = '';

    if (signals.length === 0) {
        container.innerHTML = `
            <div class="error">
                <i class="fas fa-info-circle"></i>
                Nenhum sinal encontrado para este timeframe.
            </div>
        `;
        return;
    }

    signals.forEach(signal => {
        if (signal.signal === 'ERROR') return;

        const card = createSignalCard(signal);
        container.appendChild(card);
    });
}

// Criar card de sinal
function createSignalCard(signal) {
    const card = document.createElement('div');
    card.className = 'signal-card';

    const signalType = signal.signal.split(' ')[0]; // BUY, SELL, HOLD
    const iconUrl = coinIcons[signal.pair] || coinIcons['default'];
    
    // Determinar ícone do sinal
    let signalIcon = 'fa-clock';
    if (signalType === 'BUY') signalIcon = 'fa-arrow-trend-up';
    else if (signalType === 'SELL') signalIcon = 'fa-arrow-trend-down';

    // Determinar cor da confiança
    const confidenceNum = parseInt(signal.confidence.split('/')[0]);
    let confidenceColor = '#666666';
    if (confidenceNum >= 7) confidenceColor = '#34c759';
    else if (confidenceNum >= 5) confidenceColor = '#ff9500';
    else confidenceColor = '#ff3b30';

    card.innerHTML = `
        <div class="card-header">
            <div class="coin-info">
                <img src="${iconUrl}" alt="${signal.pair}" class="coin-icon">
                <div class="coin-details">
                    <h3>${signal.pair}</h3>
                    <div class="coin-price">$${signal.price}</div>
                </div>
            </div>
            <div class="confidence-badge" style="color: ${confidenceColor}; border-color: ${confidenceColor};">
                ${signal.confidence}
            </div>
        </div>

        <div class="signal-display signal-${signalType}">
            <div class="signal-text signal-${signalType}">
                <i class="fas ${signalIcon}"></i>
                ${signal.signal}
            </div>
            <div class="signal-description">
                ${getSignalDescription(signal.signal, confidenceNum)}
            </div>
        </div>

        <div class="indicators-section">
            <div class="indicators-grid">
                <div class="indicator-item">
                    <span class="indicator-label">RSI</span>
                    <span class="indicator-value">${signal.indicators.rsi}</span>
                </div>
                <div class="indicator-item">
                    <span class="indicator-label">MACD</span>
                    <span class="indicator-value">${signal.indicators.macd}</span>
                </div>
                <div class="indicator-item">
                    <span class="indicator-label">B. Sup</span>
                    <span class="indicator-value">${signal.indicators.bollinger_upper}</span>
                </div>
                <div class="indicator-item">
                    <span class="indicator-label">B. Inf</span>
                    <span class="indicator-value">${signal.indicators.bollinger_lower}</span>
                </div>
            </div>
        </div>
    `;

    return card;
}

// Obter descrição do sinal
function getSignalDescription(signalText, confidence) {
    if (signalText.includes('BUY')) {
        if (confidence >= 7) return 'Sinal forte de compra confirmado por múltiplos indicadores';
        return 'Tendência de alta detectada, aguardando confirmação';
    } else if (signalText.includes('SELL')) {
        if (confidence >= 7) return 'Sinal forte de venda confirmado por múltiplos indicadores';
        return 'Tendência de baixa detectada, aguardando confirmação';
    } else {
        return 'Mercado em consolidação, aguardando movimento definido';
    }
}

// Aplicar filtros
function applyFilters() {
    const signalFilter = document.getElementById('signal-filter').value;
    
    let filteredSignals = allSignals;
    
    if (signalFilter !== 'all') {
        filteredSignals = allSignals.filter(signal => 
            signal.signal.includes(signalFilter)
        );
    }
    
    displaySignals(filteredSignals);
}

// Abrir modal de alertas
function openAlertsModal() {
    document.getElementById('alerts-modal').style.display = 'block';
    displayActiveAlerts();
}

// Fechar modais
function closeModals() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.style.display = 'none';
    });
}

// Adicionar alerta
function addAlert() {
    const pair = document.getElementById('alert-pair').value;
    const price = parseFloat(document.getElementById('alert-price').value);
    const condition = document.getElementById('alert-condition').value;

    if (!pair || !price) {
        alert('Por favor, preencha todos os campos.');
        return;
    }

    const alert = {
        id: Date.now(),
        pair: pair,
        price: price,
        condition: condition,
        created: new Date().toLocaleString()
    };

    activeAlerts.push(alert);
    saveAlertsToStorage();
    displayActiveAlerts();

    // Limpar formulário
    document.getElementById('alert-pair').value = '';
    document.getElementById('alert-price').value = '';
}

// Remover alerta
function removeAlert(alertId) {
    activeAlerts = activeAlerts.filter(alert => alert.id !== alertId);
    saveAlertsToStorage();
    displayActiveAlerts();
}

// Exibir alertas ativos
function displayActiveAlerts() {
    const container = document.getElementById('alerts-list');
    
    if (activeAlerts.length === 0) {
        container.innerHTML = '<p style="color: #666; text-align: center;">Nenhum alerta ativo</p>';
        return;
    }

    container.innerHTML = activeAlerts.map(alert => `
        <div class="alert-item">
            <div>
                <strong>${alert.pair}</strong> ${alert.condition === 'above' ? 'acima de' : 'abaixo de'} $${alert.price}
                <br><small style="color: #666;">Criado em: ${alert.created}</small>
            </div>
            <button onclick="removeAlert(${alert.id})">Remover</button>
        </div>
    `).join('');
}

// Verificar alertas
function checkAlerts(signals) {
    activeAlerts.forEach(alert => {
        const signal = signals.find(s => s.pair === alert.pair);
        if (!signal) return;

        const currentPrice = signal.price;
        let triggered = false;

        if (alert.condition === 'above' && currentPrice >= alert.price) {
            triggered = true;
        } else if (alert.condition === 'below' && currentPrice <= alert.price) {
            triggered = true;
        }

        if (triggered) {
            showNotification(`Alerta: ${alert.pair} ${alert.condition === 'above' ? 'acima de' : 'abaixo de'} $${alert.price}!`);
            removeAlert(alert.id);
        }
    });
}

// Mostrar notificação
function showNotification(message) {
    // Verificar se o navegador suporta notificações
    if ('Notification' in window) {
        if (Notification.permission === 'granted') {
            new Notification('Sinais Pro', { body: message });
        } else if (Notification.permission !== 'denied') {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    new Notification('Sinais Pro', { body: message });
                }
            });
        }
    }
    
    // Fallback: alert
    alert(message);
}

// Salvar alertas no localStorage
function saveAlertsToStorage() {
    localStorage.setItem('sinaisProAlerts', JSON.stringify(activeAlerts));
}

// Carregar alertas do localStorage
function loadAlertsFromStorage() {
    const stored = localStorage.getItem('sinaisProAlerts');
    if (stored) {
        activeAlerts = JSON.parse(stored);
    }
}

// Atualizar timestamp da última atualização
function updateLastUpdatedTimestamp() {
    const timestamp = document.getElementById('last-updated-timestamp');
    if (timestamp) {
        const now = new Date();
        timestamp.textContent = `Última atualização: ${now.toLocaleTimeString()}`;
    }
}

// Solicitar permissão para notificações quando a app inicializa
function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
}
