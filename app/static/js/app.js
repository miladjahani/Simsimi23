/* Milijon Railway Panel - JavaScript */

async function apiCall(url, method = 'GET', body = null) {
    const opts = {
        method,
        headers: { 'Content-Type': 'application/json' },
    };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(url, opts);
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || `HTTP ${res.status}`);
    }
    return res.json();
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function copyToClipboard(text, btnElement) {
    navigator.clipboard.writeText(text).then(() => {
        if (btnElement) {
            const orig = btnElement.textContent;
            btnElement.textContent = 'کپی شد';
            btnElement.classList.add('copied');
            setTimeout(() => {
                btnElement.textContent = orig;
                btnElement.classList.remove('copied');
            }, 2000);
        }
        showToast('کپی شد');
    });
}

function formatBytes(bytes) {
    if (bytes === 0 || !bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(dateStr) {
    if (!dateStr) return 'نامحدود';
    const d = new Date(dateStr);
    return d.toLocaleDateString('fa-IR');
}

function timeAgo(dateStr) {
    if (!dateStr) return 'هرگز';
    const diff = Date.now() - new Date(dateStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'همین الان';
    if (mins < 60) return `${mins} دقیقه پیش`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours} ساعت پیش`;
    const days = Math.floor(hours / 24);
    return `${days} روز پیش`;
}

function openModal(id) {
    document.getElementById(id).style.display = 'flex';
}

function closeModal(id) {
    document.getElementById(id).style.display = 'none';
}

function confirmDelete(message) {
    return window.confirm(message);
}

// Close modal on overlay click
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) {
        e.target.style.display = 'none';
    }
});
