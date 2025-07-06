document.addEventListener("DOMContentLoaded", function() {
    // Login button handler
    const loginButton = document.getElementById('btn-login');
    console.log("[DEBUG] Login button found:", loginButton); // Debug log
    
    if (loginButton) {
        loginButton.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent form submission
            const username = document.querySelector('input[type="text"]').value;
            const password = document.querySelector('input[type="password"]').value;
            authenticate(username, password);
        });
    } else {
        console.error("[ERROR] Could not find login button with id 'btn-login'");
    }
    

    // Register link handler
    const registerLink = document.querySelector('.register-link');
    console.log("[DEBUG] Register link found:", registerLink); // Debug log
    
    if (registerLink) {
        registerLink.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent default link behavior
            window.location.href = '/auth/registration'; // Redirect to registration page
        });
    } else {
        console.error("[ERROR] Could not find register link with class 'register-link'");
    }


    // Forgot password link handler
    const forgotLink = document.querySelector('.cont-forget a');
    console.log("[DEBUG] Forgot password link found:", forgotLink); // Debug log
    
    if (forgotLink) {
        forgotLink.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent default link behavior
            window.location.href = '/auth/restore-password'; // Redirect to restore password page
        });
    } else {
        console.error("[ERROR] Could not find forgot password link");
    }
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
                // Authentication successful, redirect to private page
                // Server-side session is already set by login_user() call
                console.log("[INFO] Authentication successful, redirecting...");
                window.location.href = '/home/private';
            } else {
                alert("[INFO] Invalid username or password");
            }
        }
    )
    .catch(error => {
        console.error("[ERROR] Authentication failed:", error);
        alert("[ERROR] An error occurred during authentication");
    });
}