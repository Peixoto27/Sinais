document.addEventListener('DOMContentLoaded', () => {
    const loginButton = document.getElementById('login-button');
    const passwordInput = document.getElementById('password-input');

    loginButton.addEventListener('click', checkPassword);
    passwordInput.addEventListener('keyup', (event) => {
        if (event.key === 'Enter') checkPassword();
    });
});

function checkPassword() {
    const correctPassword = "ope1001"; // Sua nova senha
    const enteredPassword = document.getElementById('password-input').value;

    if (enteredPassword === correctPassword) {
        document.getElementById('login-screen').style.display = 'none';
        document.getElementById('app').style.display = 'block';
        initializeApp();
    } else {
        alert('Senha incorreta.');
    }
}

function initializeApp() {
    const timeframeButtons = document.querySelectorAll('.timeframe-selector button');
    let activeTimeframe = '1d';

    timeframeButtons.forEach(button => {
        button.addEventListener('click', () => {
            timeframeButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            activeTimeframe = button.dataset.timeframe;
            fetchAndDisplaySignals(activeTimeframe);
        });
    });

    fetchAndDisplaySignals(activeTimeframe);
}

const coinIcons = {
    'BTC/USDT': 'https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@1a63530be6e374711a8554f31b17e4cb92c25669/svg/color/btc.svg',
    'ETH/USDT': 'https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@1a63530be6e374711a8554f31b17e4cb92c25669/svg/color/eth.svg',
    'XRP/USDT': 'https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@1a63530be6e374711a8554f31b17e4cb92c25669/svg/color/xrp.svg',
    'SOL/USDT': 'https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@1a63530be6e374711a8554f31b17e4cb92c25669/svg/color/sol.svg',
    'ADA/USDT': 'https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@1a63530be6e374711a8554f31b17e4cb92c25669/svg/color/ada.svg',
    'default': 'https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@1a63530be6e374711a8554f31b17e4cb92c25669/svg/color/generic.svg'
};

async function fetchAndDisplaySignals(timeframe ) {
    // IMPORTANTE: Substitua pela URL do seu novo backend na Railway
    const apiUrl = `https://SEU-NOVO-BACKEND-URL.up.railway.app/signals?timeframe=${timeframe}`;
    const container = document.getElementById('signals-container' );
    container.innerHTML = `<p>Analisando timeframe ${timeframe}...</p>`;

    try {
        const response = await fetch(apiUrl);
        const signals = await response.json();
        container.innerHTML = '';

        signals.forEach(signal => {
            if (signal.signal === 'ERROR') return;

            const card = document.createElement('div');
            card.className = 'card';

            const signalType = signal.signal.split(' ')[0]; // Pega só BUY, SELL ou HOLD

            card.innerHTML = `
                <div class="card-header">
                    <img src="${coinIcons[signal.pair] || coinIcons['default']}" alt="${signal.pair}" class="coin-icon">
                    <div>
                        <h3>${signal.pair}</h3>
                        <p style="margin:0; color: #a0a0a0;">${signal.price}</p>
                    </div>
                </div>
                <div class="signal-box signal-${signalType}">
                    <p class="signal-text">${signal.signal}</p>
                    <p class="confidence">Confiança: ${signal.confidence}</p>
                </div>
                <div class="indicators">
                    <p><strong>RSI:</strong> <span>${signal.indicators.rsi}</span></p>
                    <p><strong>MACD:</strong> <span>${signal.indicators.macd}</span></p>
                    <p><strong>B. Sup:</strong> <span>${signal.indicators.bollinger_upper}</span></p>
                    <p><strong>B. Inf:</strong> <span>${signal.indicators.bollinger_lower}</span></p>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        container.innerHTML = `<p>Erro ao carregar sinais: ${error.message}</p>`;
        console.error(error);
    }
}
