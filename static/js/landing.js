// Clock functionality
function updateClock() {
    const now = new Date();

    // Analog clock
    const hours = now.getHours() % 12;
    const minutes = now.getMinutes();
    const seconds = now.getSeconds();

    const hourDeg = (hours * 30) + (minutes * 0.5);
    const minuteDeg = minutes * 6;
    const secondDeg = seconds * 6;

    const hourHand = document.getElementById('hourHand');
    const minuteHand = document.getElementById('minuteHand');
    const secondHand = document.getElementById('secondHand');

    if (hourHand) hourHand.style.transform = `rotate(${hourDeg}deg)`;
    if (minuteHand) minuteHand.style.transform = `rotate(${minuteDeg}deg)`;
    if (secondHand) secondHand.style.transform = `rotate(${secondDeg}deg)`;

    // Digital clock
    const timeStr = now.toLocaleTimeString('ko-KR', { hour12: false });
    const dateStr = now.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    }).replace(/\. /g, '/').replace('.', '');

    const digitalClock = document.getElementById('digitalClock');
    const dateDisplay = document.getElementById('dateDisplay');

    if (digitalClock) digitalClock.textContent = timeStr;
    if (dateDisplay) dateDisplay.textContent = dateStr;
}

// Initialize clock
setInterval(updateClock, 1000);
updateClock();

// Model selection tracking
let selectedModel = 'SGR_S1';

document.querySelectorAll('input[name="model"]').forEach(radio => {
    radio.addEventListener('change', (e) => {
        selectedModel = e.target.value;
        console.log('Selected model:', selectedModel);
    });
});

// Proceed to main app
function proceedToApp() {

    // Visual Feedback
    const btn = document.querySelector('.cta-button');
    if (btn) {
        btn.innerHTML = '<span>잠시만 기다려주세요...</span>'; // Wait a moment
        btn.style.opacity = '0.9';
        btn.style.cursor = 'wait';
    }

    if (!selectedModel) {
        // Show toast notification
        showToast('⚠️ 분석 모형을 선택해주세요', 'warning');
        if (btn) {
            btn.innerHTML = '<span>분석 시작하기</span>';
            btn.style.opacity = '1';
            btn.style.cursor = 'pointer';
        }
        return;
    }

    // Store selected model in sessionStorage
    sessionStorage.setItem('selectedModel', selectedModel);

    // Redirect to main app
    window.location.href = '/app?model=' + selectedModel;
}

// Toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = 'toast glass';
    toast.style.cssText = `
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        padding: 1.2rem 2rem;
        background: ${type === 'warning' ? 'rgba(245, 158, 11, 0.9)' : 'rgba(99, 102, 241, 0.9)'};
        color: white;
        border-radius: 12px;
        font-weight: 600;
        z-index: 10000;
        animation: slideIn 0.3s ease;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    `;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
