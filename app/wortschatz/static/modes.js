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
                redirect_session(subMode, "random");
            }
            else if (mode.includes('level') && subMode) {
                console.log(`Level button clicked with ${subMode} questions`);
                redirect_session(10, subMode);
            }
            else if (mode.includes('topic')) {
                if (topic !== '') {
                    console.log(`Topic button clicked with topic: ${topic}`);
                    redirect_session(10, topic);
                }
                else {
                    console.log('Topic button clicked but no topic provided');
                }
            }
            else if (btnId.includes('practice')) {
                console.log('Practice button clicked');
                redirect_session(6, 'random');
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

function redirect_session(questions, topic) {
    const url = `/wortschatz/session?questions=${questions}&topic=${topic}`;
    window.location.href = url;
}
