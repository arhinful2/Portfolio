// Admin notification and actions
document.addEventListener('DOMContentLoaded', function() {
    // Add notification badge if unread messages exist
    const header = document.querySelector('#content h1');
    if (header && header.textContent.includes('Contact messages')) {
        // Add custom style
        const style = document.createElement('style');
        style.textContent = `
            .notification-badge {
                background: #dc3545;
                color: white;
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 12px;
                margin-left: 10px;
                display: inline-block;
            }
            .quick-action-btn {
                background: #28a745;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                cursor: pointer;
                font-size: 12px;
            }
        `;
        document.head.appendChild(style);
    }
    
    // Quick reply function
    window.sendTestEmail = function(messageId) {
        if (confirm('Send test reply email? (Will print to console)')) {
            fetch(`/admin/custom_admin/send_test_email/${messageId}/`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✓ ' + data.message);
                    // Reload after 1 second
                    setTimeout(() => location.reload(), 1000);
                } else {
                    alert('❌ ' + data.message);
                }
            })
            .catch(error => {
                alert('❌ Error: ' + error);
            });
        }
    };
});