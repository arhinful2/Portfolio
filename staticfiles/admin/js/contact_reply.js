// Admin email reply functionality
document.addEventListener('DOMContentLoaded', function() {
    // Show notification
    if (typeof unread_count !== 'undefined' && unread_count > 0) {
        const header = document.querySelector('#content h1');
        if (header) {
            header.innerHTML += ` <span class="badge" style="background:#dc3545;color:white;padding:3px 8px;border-radius:10px;font-size:12px;">
                ${unread_count} unread
            </span>`;
        }
    }
    
    // Add send email button in change form
    const changeForm = document.querySelector('.change-form');
    if (changeForm) {
        const submitRow = document.querySelector('.submit-row');
        if (submitRow) {
            // Add custom send button
            const sendButton = document.createElement('input');
            sendButton.type = 'button';
            sendButton.value = 'Send Reply Email';
            sendButton.className = 'button default';
            sendButton.style.backgroundColor = '#28a745';
            sendButton.style.borderColor = '#28a745';
            sendButton.style.marginRight = '10px';
            
            sendButton.onclick = function() {
                const replyMessage = document.querySelector('#id_reply_message').value;
                const replySubject = document.querySelector('#id_reply_subject').value;
                const email = document.querySelector('#id_email').value;
                
                if (!replyMessage) {
                    alert('Please write a reply message first!');
                    return;
                }
                
                if (!email) {
                    alert('No email address found!');
                    return;
                }
                
                if (confirm(`Send reply to ${email}?\n\nSubject: ${replySubject || 'Re: [Original Subject]'}\n\nMessage: ${replyMessage.substring(0, 100)}...`)) {
                    // Submit the form
                    document.querySelector('input[name="_continue"]').click();
                }
            };
            
            submitRow.insertBefore(sendButton, submitRow.firstChild);
        }
    }
    
    // Global send test email function (for list view)
    window.sendTestEmail = function(messageId) {
        if (confirm('Send test email reply? (Will print to console)')) {
            fetch(`/admin/portfolio/contactmessage/${messageId}/send_test_email/`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(data.message);
                        location.reload();
                    } else {
                        alert('Error: ' + data.message);
                    }
                });
        }
    };
});