Auth.requireAuth();
const user = Auth.getUser();
const teamId = user?.team_id;
let lastTimestamp = null;
let pollTimer = null;
let isOffline = false;

if (!teamId) { location.href = '/team.html'; }

async function init() {
  try {
    const team = await api.get(`/teams/${teamId}`);
    document.getElementById('teamName').textContent = team.name + ' 팀 · 채팅';
    await loadMessages(true);
    startPolling();
  } catch (e) { console.error(e); }
}

async function loadMessages(initial = false) {
  try {
    const url = initial || !lastTimestamp ? `/teams/${teamId}/messages` : `/teams/${teamId}/messages?since=${lastTimestamp}`;
    const msgs = await api.get(url);
    if (!msgs) return;
    if (initial) {
      document.getElementById('messages').innerHTML = '';
      msgs.forEach(appendMessage);
    } else {
      msgs.forEach(appendMessage);
    }
    if (msgs.length > 0) {
      lastTimestamp = msgs[msgs.length - 1].created_at;
      scrollBottom();
    }
    if (isOffline) { setOnline(); }
  } catch (e) {
    setOffline();
  }
}

function appendMessage(msg) {
  const container = document.getElementById('messages');
  const isMe = msg.user_id === user?.id;
  const time = new Date(msg.created_at).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
  const div = document.createElement('div');
  div.dataset.id = msg.id;
  div.className = `flex ${isMe ? 'justify-end' : 'justify-start'}`;
  div.innerHTML = `
    <div class="max-w-xs md:max-w-md group relative">
      ${!isMe ? `<p class="text-xs text-gray-500 mb-1">${escHtml(msg.user_email)} · ${time}</p>` : `<p class="text-xs text-gray-400 mb-1 text-right">${time}</p>`}
      <div class="flex items-start gap-2 ${isMe ? 'flex-row-reverse' : ''}">
        <div class="px-3 py-2 rounded-lg text-sm whitespace-pre-wrap break-words ${isMe ? 'bg-teal-600 text-white' : 'bg-white border border-gray-200 text-gray-800'}">
          ${escHtml(msg.content)}
        </div>
        ${isMe ? `<button onclick="deleteMsg(${msg.id}, this.closest('[data-id]'))" class="opacity-0 group-hover:opacity-100 transition text-gray-400 hover:text-red-500 text-sm mt-1">🗑</button>` : ''}
      </div>
    </div>
  `;
  if (container.children.length === 0) {
    container.innerHTML = '';
  }
  container.appendChild(div);
}

async function deleteMsg(id, el) {
  try {
    await api.delete(`/messages/${id}`);
    el?.remove();
  } catch (err) { alert(err.data?.error?.message || '삭제 실패'); }
}

async function sendMessage() {
  const input = document.getElementById('msgInput');
  const content = input.value.trim();
  if (!content || content.length > 1000) return;
  const btn = document.getElementById('sendBtn');
  btn.disabled = true;
  try {
    const msg = await api.post(`/teams/${teamId}/messages`, { content });
    input.value = '';
    document.getElementById('charCount').textContent = '0 / 1000';
    if (msg) appendMessage(msg);
    lastTimestamp = msg.created_at;
    scrollBottom();
  } catch (err) {
    alert(err.data?.error?.message || '전송 실패');
  } finally { btn.disabled = false; }
}

function onInput() {
  const val = document.getElementById('msgInput').value;
  const len = val.length;
  const countEl = document.getElementById('charCount');
  const overEl = document.getElementById('overLimit');
  const btn = document.getElementById('sendBtn');
  countEl.textContent = `${len} / 1000`;
  if (len > 1000) {
    countEl.className = 'text-xs text-red-500 font-bold';
    overEl.textContent = `${len - 1000}자 초과`;
    overEl.classList.remove('hidden');
    btn.disabled = true;
  } else {
    countEl.className = 'text-xs text-gray-400';
    overEl.classList.add('hidden');
    btn.disabled = false;
  }
}

function onKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
}

function startPolling() {
  pollTimer = setInterval(() => loadMessages(false), 5000);
}

function setOffline() {
  isOffline = true;
  document.getElementById('pollStatus').textContent = '⚠ 연결 끊김 · 재시도 중';
  document.getElementById('pollStatus').className = 'text-xs text-red-500';
}

function setOnline() {
  isOffline = false;
  document.getElementById('pollStatus').textContent = '● 5초마다 새로고침';
  document.getElementById('pollStatus').className = 'text-xs text-teal-500';
}

function scrollBottom() {
  const el = document.getElementById('messages');
  el.scrollTop = el.scrollHeight;
}

function logout() {
  clearInterval(pollTimer);
  api.post('/auth/logout').finally(() => { Auth.clear(); location.href = '/login.html'; });
}

function escHtml(str) {
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

init();
