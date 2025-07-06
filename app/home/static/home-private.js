document.addEventListener("DOMContentLoaded", function() {
    document.getElementById('btn-logout').addEventListener('click', function(event) {
    event.preventDefault();
    redirect_logout();
    });
});

function redirect_logout(){
    window.location.href = '/auth/signout';
}
