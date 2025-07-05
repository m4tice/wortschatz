document.addEventListener("DOMContentLoaded", function() {
    document.getElementById('button-signin').addEventListener('click', function(event) {
        event.preventDefault(); // Prevent form submission
        const username = document.querySelector('input[type="text"]').value;
        const password = document.querySelector('input[type="password"]').value;
        authenticate(username, password)
    });
});

function authenticate(username, password) {
    console.log("[DEBUG] signin.js: authenticate() called");
    fetch(`/auth/signin/${username}/${password}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => 
        {
            console.log("GUU8HC: " + data['result']);
            if (data['result'] == true) {
                document.cookie = `username=${username}`;
                window.location.href = '/home/private';
            } else {
                alert("Invalid username or password");
            }
        }
    )
}

document.querySelector('.register a').addEventListener('click', function(event) {
    event.preventDefault(); // Prevent default link behavior
    window.location.href = '/auth/registration'; // Redirect to home page
});

document.querySelector('.forget a').addEventListener('click', function(event) {
    event.preventDefault(); // Prevent default link behavior
    window.location.href = '/auth/restore-password'; // Redirect to home page
});