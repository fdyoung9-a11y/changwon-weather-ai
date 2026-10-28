// =====================
// 설정
// =====================
const API_BASE = 'http://localhost:8000';

// =====================
// 시간 표시
// =====================
function updateTime() {
    const now = new Date();
    const timeStr = now.toLocaleString('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('current-time').textContent = timeStr;
}

// =====================
// 날씨 불러오기
// =====================
async function loadWeather() {
    try {
        const response = await fetch(`${API_BASE}/weather/current`);
        const data = await response.json();

        if (data) {
            document.getElementById('temperature').textContent = 
                `${Math.round(data.temperature)}°C`;
            document.getElementById('weather-desc').textContent = 
                data.description || '맑음';
            document.getElementById('humidity').textContent = 
                `${data.humidity}%`;
            document.getElementById('wind-speed').textContent = 
                `${data.wind_speed} m/s`;
            document.getElementById('feels-like').textContent = 
                `${Math.round(data.feels_like)}°C`;
            document.getElementById('visibility').textContent = 
                `${(data.visibility / 1000).toFixed(1)} km`;
        }
    } catch (error) {
        console.error('날씨 로드 실패:', error);
        document.getElementById('weather-desc').textContent = 
            '날씨 정보를 불러올 수 없습니다.';
    }
}

// =====================
// 날씨 기록 불러오기
// =====================
async function loadHistory() {
    const container = document.getElementById('weather-history');
    container.innerHTML = `
        <div class="text-center text-muted py-3">
            <i class="fas fa-spinner fa-spin"></i> 불러오는 중...
        </div>`;

    try {
        const response = await fetch(`${API_BASE}/weather/history?limit=5`);
        const data = await response.json();

        if (data && data.length > 0) {
            container.innerHTML = data.map(item => `
                <div class="history-item">
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="temp">${Math.round(item.temperature)}°C</span>
                        <span class="time">${formatTime(item.timestamp)}</span>
                    </div>
                    <div class="text-muted" style="font-size:0.82rem;">
                        💧 습도 ${item.humidity}% &nbsp;
                        💨 풍속 ${item.wind_speed}m/s
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = `
                <div class="text-center text-muted py-3">
                    기록이 없습니다.
                </div>`;
        }
    } catch (error) {
        console.error('기록 로드 실패:', error);
        container.innerHTML = `
            <div class="text-center text-danger py-3">
                <i class="fas fa-exclamation-circle"></i> 불러오기 실패
            </div>`;
    }
}

// =====================
// 시간 포맷
// =====================
function formatTime(timestamp) {
    if (!timestamp) return '-';
    const date = new Date(timestamp);
    return date.toLocaleString('ko-KR', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// =====================
// AI 채팅
// =====================
async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;

    // 사용자 메시지 표시
    addMessage(message, 'user');
    input.value = '';

    // 로딩 메시지
    const loadingId = addLoadingMessage();

    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();

        // 로딩 제거 후 AI 응답 표시
        removeMessage(loadingId);
        addMessage(data.response || '응답을 받지 못했습니다.', 'bot');

    } catch (error) {
        console.error('채팅 오류:', error);
        removeMessage(loadingId);
        addMessage('죄송합니다. 연결에 문제가 생겼어요. 잠시 후 다시 시도해주세요.', 'bot');
    }
}

// =====================
// 메시지 추가
// =====================
function addMessage(text, type) {
    const container = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = `message ${type === 'bot' ? 'bot-message' : 'user-message'}`;

    if (type === 'bot') {
        div.innerHTML = `<i class="fas fa-robot"></i> ${text}`;
    } else {
        div.innerHTML = `${text} <i class="fas fa-user"></i>`;
    }

    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return div;
}

// =====================
// 로딩 메시지
// =====================
function addLoadingMessage() {
    const container = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = 'message bot-message';
    div.id = 'loading-msg';
    div.innerHTML = `<i class="fas fa-robot"></i> <span class="loading-dots">생각하는 중</span>`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return 'loading-msg';
}

function removeMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// =====================
// 엔터키 처리
// =====================
function handleEnter(event) {
    if (event.key === 'Enter') sendMessage();
}

// =====================
// 초기 실행
// =====================
document.addEventListener('DOMContentLoaded', () => {
    loadWeather();
    loadHistory();
    updateTime();
    setInterval(updateTime, 1000);        // 1초마다 시간 갱신
    setInterval(loadWeather, 5 * 60 * 1000); // 5분마다 날씨 갱신
});