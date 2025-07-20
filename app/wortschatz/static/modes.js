document.addEventListener("DOMContentLoaded", function() {
    redirect_logout();

    buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            const btnId = String(this.getAttribute('id'));
            const details = btnId.split('-');

            const mode = details[1];
            const subMode = details.length > 2 ? details[2] : '';
            const topic = document.getElementById('card-input-topic').value;

            if (mode.includes('daily') && subMode) {
                console.log(`Daily button clicked with ${subMode} questions`);
            }
            else if (mode.includes('level') && subMode) {
                console.log(`Level button clicked with ${subMode} questions`);
            }
            else if (mode.includes('topic')) {
                if (topic !== '') {
                    console.log(`Topic button clicked with topic: ${topic}`);
                }
                else {
                    console.log('Topic button clicked but no topic provided');
                }
            }
            else if (btnId.includes('practice')) {
                console.log('Practice button clicked');
            }
            else {
                console.log(`Button with ID ${btnId} clicked`);
            }
        });
    });
});

function redirect_logout(){
    document.getElementById('btn-logout').addEventListener('click', function(event) {
        event.preventDefault();
        window.location.href = '/auth/logout';
    });
}
