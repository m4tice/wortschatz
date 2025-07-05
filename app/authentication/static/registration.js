document.getElementById('button-register').addEventListener('click', function(event) {
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
            console.log("GUU8HC: " + data['result']);
            if (data['result'] == true) {
                document.cookie = `username=${username}`;
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

document.querySelector('.login a').addEventListener('click', function(event) {
    event.preventDefault(); // Prevent default link behavior
    window.location.href = '/auth/signin'; // Redirect to home page
});