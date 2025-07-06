document.addEventListener('DOMContentLoaded', function() {
    
    // Login button handler
    const loginRef = document.getElementById('login');
    
    if (loginRef) {
        loginRef.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent form submission
            redirect_login(); // Redirect to login page
        });
    } else {
        console.error("[ERROR] Could not find login button with id 'login'");
    }

    // Signup button handler
    const signupButton = document.getElementById('btn-signup');
    if (signupButton) {
        signupButton.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent form submission
            redirect_signup(); // Redirect to signup page
        });
    } else {
        console.error("[ERROR] Could not find signup button with id 'btn-signup'");
    }

});


function redirect_login(){
    window.location.href = '/auth/login';
}

function redirect_signup(){
    window.location.href = '/auth/registration';
}