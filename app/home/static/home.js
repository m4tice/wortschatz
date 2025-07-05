document.getElementById('signin').addEventListener('click', function(event) {
    event.preventDefault();
    redirect_signin();
});

function redirect_signin(){
    window.location.href = '/auth/signin';
}   