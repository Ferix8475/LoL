document.getElementById('search-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const championName = document.getElementById('champion-name').value;
    const role = document.getElementById('role-select').value;

    fetch('/api/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ championName, role })
    })
    .then(response => response.json())
    .then(data => {
        if (data.exists) {
            window.location.href = '/champion';
        } else {
            document.getElementById('error-message').textContent = 'No data found for the specified champion and role.';
            document.getElementById('error-message').style.display = 'block';
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});