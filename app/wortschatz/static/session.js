document.addEventListener("DOMContentLoaded", function () {
    main();
});

function main() {
    answerInput = document.getElementById("answer");
    validateButton = document.getElementById("btn-validate");
    validateButton.addEventListener("click", validateAnswer);
}

function validateAnswer() {
    const question = document.querySelector("h1").innerText;
    const answer = answerInput.value;

    console.log(`Validating answer for question: ${question}, answer: ${answer}`);

    fetch(`session/validate?question=${encodeURIComponent(question)}&answer=${encodeURIComponent(answer)}`)
        .then(response => response.json())
        .then(data => {
            if (data.result) {
                alert("Correct!");
            } else {
                alert("Incorrect!");
            }
        });
}
