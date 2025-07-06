document.getElementById('btn-register').addEventListener('click', function(event) {
    event.preventDefault(); // Prevent form submission
    const username = document.querySelector('input[type="text"]').value;
    const password = document.querySelector('input[type="password"]').value;
    registerClicked(username, password)
});

function registerClicked(username, password) {
    fetch(`/auth/registration/${username}/${password}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => 
        {
            if (data['result'] == true) {
                // Registration successful, redirect to private page
                // Server-side session is already set by login_user() call
                console.log("Registration successful, redirecting...");
                window.location.href = '/home/private';
            } else {
                alert("Invalid username or password");
            }
        }
    )
    .catch(error => {
        console.error('Error:', error);
        alert("An error occurred during registration.");
    });
}
