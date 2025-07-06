document.getElementById('btn-login').addEventListener('click', function(event) {
    event.preventDefault();
    redirect_login();
});

function redirect_login(){
    window.location.href = '/auth/signin';
}   