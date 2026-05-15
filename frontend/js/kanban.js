Auth.requireAuth();
const user = Auth.getUser();
let teamId = user?.team_id;
let tasks = [];
let members = [];
let currentFilter = 'all';
let dragTaskId = null;
let modalTask = null;
let currentMobileCol = 'TODO';

document.getElementById('userEmail').textContent = user?.email || '';

async function init() {
  if (!teamId) { location.href = '/team.html'; return; }
  try {
    const team = await api.get(`/teams/${teamId}`);
    document.getElementById('teamName').textContent = team.name + ' 팀';
    members = await api.get(`/teams/${teamId}/members`);
    await loadTasks();
  } catch (e) { console.error(e); }
}

async function loadTasks() {
  const q = currentFilter === 'all' ? '' : `?filter=${currentFilter === 'me' ? 'me' : 'unassigned'}`;
  tasks = await api.get(`/teams/${teamId}/tasks${q}`);
  renderBoard();
}

function renderBoard() {
  ['TODO', 'DOING', 'DONE'].forEach(s => {
    const col = tasks.filter(t => t.status === s);
    document.getElementById(`cnt-${s}`).textContent = col.length;
    const container = document.getElementById(`cards-${s}`);
    container.innerHTML = '';
    if (col.length === 0) {
      container.innerHTML = `<div class="text-center py-8 text-gray-400 text-sm border-2 border-dashed border-gray-200 rounded">
        <p>카드 없음</p>${s === 'TODO' ? '<p class="text-teal-500 cursor-pointer mt-1" onclick="startAdd(\'TODO\')">+ 첫 태스크 만들기</p>' : '<p>드래그로 이동</p>'}
      </div>`;
    }
    col.forEach(t => container.appendChild(makeCard(t)));
  });
}

function makeCard(task) {
  const div = document.createElement('div');
  div.className = 'bg-white rounded shadow-sm p-3 cursor-pointer hover:shadow-md transition';
  div.draggable = true;
  div.dataset.id = task.id;
  const assigneeName = task.assignee_id ? (members.find(m => m.id === task.assignee_id)?.email?.split('@')[0] || '?') : null;
  div.innerHTML = `
    <p class="text-sm font-medium mb-1">${escHtml(task.title)}</p>
    <p class="text-xs text-gray-400">#${task.id} · ${assigneeName ? '<span class="text-teal-600">@' + escHtml(assigneeName) + '</span>' : '<span class="text-orange-400">⚠미할당</span>'}</p>
  `;
  div.addEventListener('dragstart', () => { dragTaskId = task.id; div.classList.add('card-dragging'); });
  div.addEventListener('dragend', () => { dragTaskId = null; div.classList.remove('card-dragging'); document.querySelectorAll('.kanban-col').forEach(c => c.classList.remove('col-dragover')); });
  div.addEventListener('click', () => openModal(task));
  return div;
}

async function drop(e, status) {
  e.preventDefault();
  e.currentTarget.closest('.kanban-col').classList.remove('col-dragover');
  if (!dragTaskId) return;
  const task = tasks.find(t => t.id === dragTaskId);
  if (!task || task.status === status) return;
  try {
    await api.patch(`/tasks/${dragTaskId}/status`, { status });
    await loadTasks();
  } catch (err) { alert(err.data?.error?.message || '상태 변경 실패'); }
}

function startAdd(col) {
  ['TODO', 'DOING', 'DONE'].forEach(s => document.getElementById(`add-${s}`).classList.add('hidden'));
  document.getElementById(`add-${col}`).classList.remove('hidden');
  document.getElementById(`add-input-${col}`).focus();
  // 담당자 select 옵션 채우기
  const sel = document.getElementById(`add-assignee-${col}`);
  if (sel && sel.options.length <= 1) {
    sel.innerHTML = `<option value="me">@me</option>` +
      members.map(m => `<option value="${m.id}">${m.email.split('@')[0]}</option>`).join('') +
      `<option value="null">미할당</option>`;
  }
}

async function handleAddKey(e, col) {
  if (e.key === 'Escape') { document.getElementById(`add-${col}`).classList.add('hidden'); return; }
  if (e.key !== 'Enter') return;
  const title = document.getElementById(`add-input-${col}`).value.trim();
  if (!title) return;
  const sel = document.getElementById(`add-assignee-${col}`);
  const selVal = sel?.value;
  const assignee_id = selVal === 'me' ? user?.id : (selVal === 'null' ? null : (parseInt(selVal) || null));
  try {
    await api.post(`/teams/${teamId}/tasks`, { title, assignee_id });
    document.getElementById(`add-input-${col}`).value = '';
    document.getElementById(`add-${col}`).classList.add('hidden');
    await loadTasks();
  } catch (err) { alert(err.data?.error?.message || '태스크 생성 실패'); }
}

function setFilter(f) {
  currentFilter = f;
  ['all', 'me', 'unassigned'].forEach(k => {
    const btn = document.getElementById(`f-${k}`);
    btn.className = k === f
      ? 'filter-btn px-3 py-1 rounded text-sm font-medium bg-gray-800 text-white'
      : 'filter-btn px-3 py-1 rounded text-sm font-medium text-gray-600 hover:bg-gray-100';
  });
  loadTasks();
}

// 모달
function openModal(task) {
  modalTask = { ...task };
  document.getElementById('modal-id').textContent = `#${task.id}`;
  document.getElementById('modal-title').value = task.title;
  const aEmail = task.assignee_id ? (members.find(m => m.id === task.assignee_id)?.email || '?') : '미할당';
  const cEmail = members.find(m => m.id === task.creator_id)?.email || '?';
  document.getElementById('modal-assignee').textContent = aEmail;
  document.getElementById('modal-creator').textContent = cEmail;
  setModalStatus(task.status);
  document.getElementById('modal').classList.remove('hidden');
}

function setModalStatus(s) {
  modalTask.status = s;
  ['TODO', 'DOING', 'DONE'].forEach(k => {
    document.getElementById(`ms-${k}`).className = k === s
      ? 'modal-status px-3 py-1 rounded border text-sm bg-teal-600 text-white border-teal-600'
      : 'modal-status px-3 py-1 rounded border text-sm text-gray-600 border-gray-300 hover:bg-gray-50';
  });
}

function closeModal() { document.getElementById('modal').classList.add('hidden'); modalTask = null; }

async function saveModal() {
  if (!modalTask) return;
  try {
    if (modalTask.title !== document.getElementById('modal-title').value.trim()) {
      modalTask.title = document.getElementById('modal-title').value.trim();
    }
    const orig = tasks.find(t => t.id === modalTask.id);
    if (orig.title !== modalTask.title || orig.assignee_id !== modalTask.assignee_id) {
      await api.put(`/tasks/${modalTask.id}`, { title: modalTask.title, assignee_id: modalTask.assignee_id });
    }
    if (orig.status !== modalTask.status) {
      await api.patch(`/tasks/${modalTask.id}/status`, { status: modalTask.status });
    }
    closeModal();
    await loadTasks();
  } catch (err) { alert(err.data?.error?.message || '저장 실패'); }
}

async function deleteTask() {
  if (!modalTask || !confirm(`'#${modalTask.id} ${modalTask.title}'을 삭제하시겠습니까?\n되돌릴 수 없습니다`)) return;
  try {
    await api.delete(`/tasks/${modalTask.id}`);
    closeModal();
    await loadTasks();
  } catch (err) { alert(err.data?.error?.message || '삭제 실패'); }
}

// 멤버 패널
async function showMembers() {
  const panel = document.getElementById('membersPanel');
  const list = document.getElementById('membersList');
  const isOwner = members.find(m => m.is_owner && m.email === user?.email);

  list.innerHTML = members.map(m => `
    <div class="flex items-center gap-3 py-2 border-b">
      <div class="w-8 h-8 rounded-full bg-teal-600 text-white flex items-center justify-center text-sm font-bold">
        ${m.email[0].toUpperCase()}
      </div>
      <div>
        <p class="text-sm font-medium">${escHtml(m.email)}</p>
        <p class="text-xs ${m.is_owner ? 'text-yellow-600 font-semibold' : 'text-gray-400'}">${m.is_owner ? '★ owner' : 'member'}</p>
      </div>
    </div>
  `).join('');

  if (isOwner) {
    const team = await api.get(`/teams/${teamId}`);
    list.innerHTML += `
      <div class="mt-4 pt-4 border-t">
        <p class="text-xs text-gray-500 mb-2">초대코드</p>
        <div class="flex items-center gap-2 mb-3">
          <span id="currentInviteCode" class="font-mono font-bold text-teal-600 tracking-widest border border-teal-200 rounded px-3 py-1 bg-teal-50">${escHtml(team.invite_code)}</span>
          <button onclick="copyInviteCode()" class="text-xs bg-gray-100 hover:bg-gray-200 px-2 py-1 rounded">📋 복사</button>
        </div>
        <button onclick="regenerateInviteCode()" class="w-full text-sm border border-orange-300 text-orange-600 hover:bg-orange-50 rounded py-1.5 transition">🔄 초대코드 재발급</button>
      </div>
    `;
  }
  panel.classList.remove('hidden');
}

async function copyInviteCode() {
  const code = document.getElementById('currentInviteCode')?.textContent;
  if (code) navigator.clipboard.writeText(code).then(() => alert('복사됨: ' + code));
}

async function regenerateInviteCode() {
  if (!confirm('초대코드를 재발급하면 기존 코드는 즉시 무효화됩니다.\n계속하시겠습니까?')) return;
  try {
    const data = await api.post(`/teams/${teamId}/invite-code`);
    const codeEl = document.getElementById('currentInviteCode');
    if (codeEl) codeEl.textContent = data.invite_code;
    alert('새 초대코드: ' + data.invite_code);
  } catch (err) { alert(err.data?.error?.message || '재발급 실패'); }
}
function closeMembers() { document.getElementById('membersPanel').classList.add('hidden'); }

// 모바일 탭
function showCol(col) {
  currentMobileCol = col;
  ['TODO', 'DOING', 'DONE'].forEach(s => {
    document.getElementById(`col-${s}`).classList.toggle('hidden', s !== col || window.innerWidth >= 768);
    if (window.innerWidth < 768) document.getElementById(`col-${s}`).classList.toggle('hidden', s !== col);
    document.getElementById(`tab-${s}`).className = s === col
      ? 'flex-1 py-2 text-sm font-medium text-teal-600 border-b-2 border-teal-600'
      : 'flex-1 py-2 text-sm font-medium text-gray-500';
  });
}

window.addEventListener('resize', () => {
  if (window.innerWidth >= 768) {
    ['TODO', 'DOING', 'DONE'].forEach(s => document.getElementById(`col-${s}`).classList.remove('hidden'));
  } else {
    showCol(currentMobileCol);
  }
});

function logout() {
  api.post('/auth/logout').finally(() => { Auth.clear(); location.href = '/login.html'; });
}

function escHtml(str) {
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

init();
