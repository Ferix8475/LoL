/* 
    Script to handle input from the search bar, handle inputs that don't exist, as well as handle closing the error message pop-up
*/


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
            window.location.href = data.redirect_url;
        } else {
            document.getElementById('error-message').textContent = 'No data found for the specified champion and role (Click to Close Notification)';
            document.getElementById('error-message').style.display = 'block';
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const errorMessage = document.getElementById('error-message');

    errorMessage.addEventListener('click', function () {
        errorMessage.style.display = 'none';
    });
});