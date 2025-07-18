function composeEmail() {
    const modal = document.getElementById('emailModal');
    const loading = document.getElementById('emailLoading');
    const form = document.getElementById('emailForm');
    modal.style.display = 'block';
    loading.style.display = 'block';
    form.style.display = 'none';

    fetch('email/compose-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
        .then(res => res.json())
        .then(data => {
            loading.style.display = 'none';
            form.style.display = 'block';
            if (data.success) {
                document.getElementById('emailContent').value = data.email_content;
            } else {
                alert('Error: ' + data.error);
                closeModal();
            }
        })
        .catch(err => {
            loading.style.display = 'none';
            alert('Error: ' + err);
            closeModal();
        });
}

function closeModal() {
    document.getElementById('emailModal').style.display = 'none';
}

function saveEmail() {
    const content = document.getElementById('emailContent').value;
    if (!content.trim()) return alert('Please enter email content');
    fetch('email/save-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email_content: content })
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                closeModal();
                alert('Email saved successfully!');
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(err => alert('Error: ' + err));
}

function sendEmails() {
    if (!confirm('Are you sure you want to send emails to all participants?')) return;
    const sendBtn = document.getElementById('sendEmailsBtn');
    const originalText = sendBtn.textContent;
    sendBtn.textContent = 'Sending...';
    sendBtn.disabled = true;
    fetch('email/send-emails', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
        .then(async res => {
            if (res.status === 401) {
                const data = await res.json();
                if (data.auth_url) {
                    window.open(data.auth_url, '_blank');
                    alert('Authentication required. Please authenticate with Google in the new tab, then refresh this page.');
                } else {
                    alert('Authentication required. Please authenticate again.');
                }
                sendBtn.textContent = originalText;
                sendBtn.disabled = false;
                return;
            }
            return res.json();
        })
        .then(data => {
            if (!data) return;
            sendBtn.textContent = originalText;
            sendBtn.disabled = false;
            if (data.success) {
                alert(`Sent ${data.sent_count} emails. ${data.failed_count} failed.`);
                location.reload();
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(err => {
            sendBtn.textContent = originalText;
            sendBtn.disabled = false;
            alert('Error: ' + err);
        });
}

function checkAuthStatus() {
    fetch('/auth/status')
        .then(res => res.json())
        .then(data => {
            const composeBtn = document.querySelector('.compose-btn');
            const authBtn = document.getElementById('authBtn');
            const sendBtn = document.getElementById('sendEmailsBtn');

            if (data.authenticated) {
                composeBtn.disabled = false;
                authBtn.disabled = true;
                sendBtn.disabled = false;
                // Hide any auth required messages
                const authMessages = document.querySelectorAll('.success-message');
                authMessages.forEach(msg => {
                    if (msg.textContent.includes('Authentication required')) {
                        msg.style.display = 'none';
                    }
                });
            } else {
                composeBtn.disabled = true;
                authBtn.disabled = false;
                sendBtn.disabled = true;
            }
        })
        .catch(err => console.error('Error checking auth status:', err));
}

// Close modal when clicking outside of it
window.onclick = function (e) {
    const modal = document.getElementById('emailModal');
    if (e.target === modal) closeModal();
};

// Ensure authentication form always opens /start-auth in a new tab
const authForm = document.getElementById('authForm');
if (authForm) {
    authForm.addEventListener('submit', function (e) {
        e.preventDefault();
        window.open('/auth/start_auth', '_blank');
        // Start checking auth status periodically
        startAuthStatusCheck();
    });
}

// Check auth status periodically when authentication might be in progress
let authCheckInterval = null;

function startAuthStatusCheck() {
    if (authCheckInterval) {
        clearInterval(authCheckInterval);
    }

    authCheckInterval = setInterval(() => {
        checkAuthStatus();
    }, 2000); // Check every 2 seconds

    // Stop checking after 5 minutes
    setTimeout(() => {
        if (authCheckInterval) {
            clearInterval(authCheckInterval);
            authCheckInterval = null;
        }
    }, 300000);
}

// Check auth status on page load
document.addEventListener('DOMContentLoaded', function () {
    checkAuthStatus();
});

