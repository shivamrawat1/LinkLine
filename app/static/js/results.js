function composeEmail() {
    const modal = document.getElementById('emailModal');
    const loading = document.getElementById('emailLoading');
    const form = document.getElementById('emailForm');
    modal.style.display = 'block';
    loading.style.display = 'block';
    form.style.display = 'none';

    fetch('/compose-email', {
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
    fetch('/save-email', {
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
    fetch('/send-emails', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
        .then(res => res.json())
        .then(data => {
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

window.onclick = function (e) {
    const modal = document.getElementById('emailModal');
    if (e.target === modal) closeModal();
}; 