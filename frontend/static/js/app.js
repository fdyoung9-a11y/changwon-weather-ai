// =====================
// 설정
// =====================
const API_BASE = 'http://localhost:8000';
let currentSessionId = null;   // 지금 대화방 이름표 (없으면 새 대화)
let allConversations = [];     // 서버에서 불러온 대화 기록 전체

// =====================
// 시간 표시
// =====================
function updateTime() {
    const now = new Date();
    document.getElementById('current-time').textContent = now.toLocaleString('ko-KR', {
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
}

function formatTime(timestamp) {
    if (!timestamp) return '-';
    return new Date(timestamp).toLocaleString('ko-KR', {
        month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit'
    });
}

// =====================
// 안전하게 글자 표시하기 (보안)
// =====================
function escapeHtml(text) {
    return String(text)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

// AI 답변 서식: **굵게** → 굵은 글씨, 줄바꿈 → <br>
function formatText(text) {
    return escapeHtml(text)
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
}

// =====================
// 📊 데이터 요약
// =====================
async function loadSummary() {
    try {
        const res = await fetch(`${API_BASE}/summary`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const s = await res.json();

        document.getElementById('sum-avg').textContent = `${s.metrics.average_temp}°C`;
        document.getElementById('sum-period').textContent = s.period;
        document.getElementById('sum-count').textContent = `${s.count}개월`;
        document.getElementById('sum-max').textContent = `${s.metrics.highest_temp}°C`;
        document.getElementById('sum-min').textContent = `${s.metrics.lowest_temp}°C`;
        document.getElementById('sum-trend').textContent = `📈 추세: ${s.trend}`;
    } catch (error) {
        console.error('요약 로드 실패:', error);
        document.getElementById('sum-trend').textContent =
            '요약을 불러올 수 없습니다. 서버가 켜져 있는지 확인하세요.';
    }
}

// =====================
// 💬 AI 채팅
// =====================
async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    input.value = '';
    const loading = addMessage('생각하는 중...', 'bot');

    try {
        const res = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            // 대화방 이름표를 같이 보내야 같은 대화로 이어져요
            body: JSON.stringify({ message: message, conversation_id: currentSessionId })
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        loading.remove();
        addMessage(data.response || '응답을 받지 못했습니다.', 'bot');

        currentSessionId = data.conversation_id;   // 서버가 준 이름표 기억하기
        loadConversations();                       // 대화 기록 목록 새로고침
    } catch (error) {
        console.error('채팅 오류:', error);
        loading.remove();
        addMessage('죄송합니다. 연결에 문제가 생겼어요. 잠시 후 다시 시도해주세요.', 'bot');
    }
}

function addMessage(text, type) {
    const container = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = `message ${type === 'bot' ? 'bot-message' : 'user-message'}`;

    if (type === 'bot') {
        div.innerHTML = `<i class="fas fa-robot"></i> ${formatText(text)}`;
    } else {
        div.innerHTML = `${escapeHtml(text)} <i class="fas fa-user"></i>`;
    }

    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return div;
}

// 새 대화 시작
function newChat() {
    currentSessionId = null;
    document.getElementById('chat-messages').innerHTML = '';
    addMessage('안녕하세요! 창원 날씨 AI입니다. 2000년부터 쌓인 창원 기온 데이터를 바탕으로 답해 드려요. 😊', 'bot');
    renderConversations();
}

function handleEnter(event) {
    // isComposing: 한글 입력 중 Enter가 두 번 눌리는 문제 방지
    if (event.key === 'Enter' && !event.isComposing) sendMessage();
}

// =====================
// 🕘 대화 기록
// =====================
async function loadConversations() {
    try {
        const res = await fetch(`${API_BASE}/conversations/`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        allConversations = data.data || [];
        renderConversations();
    } catch (error) {
        console.error('대화 기록 로드 실패:', error);
        document.getElementById('conv-list').innerHTML =
            '<div class="text-center text-danger py-3">불러오기 실패</div>';
    }
}

function renderConversations() {
    const box = document.getElementById('conv-list');

    // 같은 대화방(session_id)끼리 묶기
    const groups = {};
    allConversations.forEach(c => {
        const key = c.session_id || c.id;
        if (!groups[key]) groups[key] = [];
        groups[key].push(c);
    });
    const sessions = Object.entries(groups);   // 서버가 최신순으로 주므로 첫 번째가 가장 최근

    if (sessions.length === 0) {
        box.innerHTML = '<div class="text-center text-muted py-3">저장된 대화가 없습니다.</div>';
        return;
    }

    box.innerHTML = sessions.map(([key, items]) => {
        const first = items[items.length - 1];                 // 가장 오래된 = 첫 질문
        const active = key === currentSessionId ? ' border-primary' : '';
        return `
            <div class="border rounded p-2 mb-2${active}" style="cursor:pointer"
                 onclick="openSession('${escapeHtml(key)}')">
                <div class="fw-semibold text-truncate">${escapeHtml(first.user_message)}</div>
                <div class="text-muted small">${formatTime(items[0].created_at)} · 질문 ${items.length}개</div>
            </div>`;
    }).join('');
}

// 대화 기록 클릭 → 채팅창에 다시 불러오기
function openSession(key) {
    const items = allConversations
        .filter(c => (c.session_id || c.id) === key)
        .sort((a, b) => a.created_at.localeCompare(b.created_at));   // 오래된 순

    currentSessionId = key;   // 이어서 질문하면 같은 대화방에 저장돼요
    document.getElementById('chat-messages').innerHTML = '';
    items.forEach(c => {
        addMessage(c.user_message, 'user');
        addMessage(c.bot_response, 'bot');
    });
    renderConversations();
}

// =====================
// 🗂 데이터 관리
// =====================
function showDataMsg(text, type) {
    const el = document.getElementById('data-msg');
    el.className = `small mt-2 text-${type}`;
    el.textContent = text;
}

async function loadWeatherData() {
    const tbody = document.getElementById('data-table');
    try {
        const res = await fetch(`${API_BASE}/`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        // 최신 연-월이 위로 오도록 정렬
        const rows = (data.data || []).sort((a, b) => (b.year - a.year) || (b.month - a.month));
        if (rows.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">데이터가 없습니다.</td></tr>';
            return;
        }

        const show = (v, unit) => (v === null || v === undefined) ? '-' : `${v}${unit}`;
        tbody.innerHTML = rows.map(r => `
            <tr>
                <td>${r.year}-${String(r.month).padStart(2, '0')}</td>
                <td>${show(r.avg_temp, '°C')}</td>
                <td>${show(r.max_temp, '°C')}</td>
                <td>${show(r.min_temp, '°C')}</td>
                <td>${show(r.rainfall, 'mm')}</td>
                <td>
                    <button class="btn btn-sm btn-outline-danger"
                            onclick="deleteWeather(${r.year}, ${r.month})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>`).join('');
    } catch (error) {
        console.error('데이터 로드 실패:', error);
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">불러오기 실패</td></tr>';
    }
}

async function addWeather() {
    // 빈칸이면 null, 아니면 숫자로 바꾸기
    const num = id => {
        const v = document.getElementById(id).value;
        return v === '' ? null : Number(v);
    };
    const year = num('in-year');
    const month = num('in-month');
    const avg = num('in-avg');

    // 입력값 검사
    if (year === null || month === null || avg === null) {
        showDataMsg('연도, 월, 평균기온은 꼭 입력해야 해요.', 'danger');
        return;
    }
    if (!Number.isInteger(year) || year < 1900 || year > 2100) {
        showDataMsg('연도는 1900~2100 사이의 정수로 입력해 주세요.', 'danger');
        return;
    }
    if (!Number.isInteger(month) || month < 1 || month > 12) {
        showDataMsg('월은 1~12 사이의 정수로 입력해 주세요.', 'danger');
        return;
    }

    const body = {
        year, month, avg_temp: avg,
        max_temp: num('in-max'), min_temp: num('in-min'), rainfall: num('in-rain')
    };

    try {
        const res = await fetch(`${API_BASE}/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const data = await res.json();
        if (!res.ok) {
            showDataMsg(typeof data.detail === 'string' ? data.detail : '추가에 실패했어요.', 'danger');
            return;
        }
        showDataMsg(`${year}년 ${month}월 데이터를 추가했어요.`, 'success');
        ['in-year', 'in-month', 'in-avg', 'in-max', 'in-min', 'in-rain']
            .forEach(id => document.getElementById(id).value = '');
        loadWeatherData();
        loadSummary();   // 요약도 새로 계산
    } catch (error) {
        console.error('추가 오류:', error);
        showDataMsg('서버에 연결할 수 없어요.', 'danger');
    }
}

async function deleteWeather(year, month) {
    if (!confirm(`${year}년 ${month}월 데이터를 삭제할까요?`)) return;
    try {
        const res = await fetch(`${API_BASE}/${year}/${month}`, { method: 'DELETE' });
        const data = await res.json();
        if (!res.ok) {
            showDataMsg(typeof data.detail === 'string' ? data.detail : '삭제에 실패했어요.', 'danger');
            return;
        }
        showDataMsg(`${year}년 ${month}월 데이터를 삭제했어요.`, 'success');
        loadWeatherData();
        loadSummary();
    } catch (error) {
        console.error('삭제 오류:', error);
        showDataMsg('서버에 연결할 수 없어요.', 'danger');
    }
}

// =====================
// 처음 실행
// =====================
document.addEventListener('DOMContentLoaded', () => {
    updateTime();
    setInterval(updateTime, 1000);
    newChat();
    loadSummary();
    loadConversations();
    loadWeatherData();
});