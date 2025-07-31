// Quiz JavaScript functionality
class QuizApp {
    constructor() {
        this.apiUrl = '/wortschatz/session'; // Updated to match Flask blueprint URL structure
        this.questionElement = document.getElementById('question-text');
        this.answerInput = document.querySelector('.div-answer input');
        this.checkButton = document.getElementById('check-btn');
        this.healthFill = document.querySelector('.health-fill');
        this.healthText = document.querySelector('.health-text');
        this.currentQuestion = null;
        this.questions = []; // Store questions locally
        this.currentQuestionIndex = 0;
        this.health = 100; // Start with full health
        this.isGameOver = false; // Track game over state
        
        this.init();
    }
    
    init() {
        // Load questions from window.sessionData if available
        if (window.sessionData && window.sessionData.questions) {
            // sessionData.questions is now an object/dictionary, extract keys
            this.questions = Object.keys(window.sessionData.questions);
            this.currentQuestionIndex = 0;
            console.log('Loaded questions from sessionData:', this.questions);
            console.log('Full sessionData:', window.sessionData);
        } else {
            console.warn('No session data found, loading with default parameters');
            // If no session data, reload page with default parameters
            this.loadWithDefaults();
            return;
        }
        
        this.loadQuestion();
        this.setupEventListeners();
        this.updateHealthBar();
    }
    
    loadWithDefaults() {
        // Reload the page with default parameters if none were provided
        const currentUrl = new URL(window.location);
        const hasQuestions = currentUrl.searchParams.has('questions');
        const hasTopic = currentUrl.searchParams.has('topic');
        
        if (!hasQuestions && !hasTopic) {
            // Add default parameters and reload
            currentUrl.searchParams.set('questions', '10');
            currentUrl.searchParams.set('topic', 'random');
            console.log('Reloading with default parameters:', currentUrl.toString());
            window.location.href = currentUrl.toString();
        } else {
            // Parameters exist but no data loaded, show error
            this.displayError('Failed to load session data despite having parameters');
        }
    }
    
    updateHealthBar() {
        this.healthFill.style.width = `${this.health}%`;
        this.healthText.textContent = `Health: ${this.health}%`;
        
        // Change color based on health level
        if (this.health > 70) {
            this.healthFill.style.background = 'linear-gradient(90deg, #44aa44 0%, #66bb66 100%)';
        } else if (this.health > 30) {
            this.healthFill.style.background = 'linear-gradient(90deg, #ffaa00 0%, #ffcc44 100%)';
        } else {
            this.healthFill.style.background = 'linear-gradient(90deg, #ff4444 0%, #ff6666 100%)';
        }
    }
    
    decreaseHealth(amount = 10) {
        console.log(`Decreasing health by ${amount}. Current health: ${this.health}`);
        this.health = Math.max(0, this.health - amount);
        console.log(`New health: ${this.health}`);
        this.updateHealthBar();
    }
    
    increaseHealth(amount = 10) {
        this.health = Math.min(100, this.health + amount);
        this.updateHealthBar();
    }
    
    gameOver() {
        console.log('GAME OVER! Health reached 0');
        const notification = document.querySelector('.div-notification');
        notification.innerHTML = `
            <div style="font-weight: bold; margin-bottom: 5px; color: #ff4444;">
                💀 Game Over!
            </div>
            <div style="font-size: 14px; color: #666;">
                Your health reached 0. Click CHECK button or here to restart.
            </div>
        `;
        notification.style.backgroundColor = '#ffe6e6';
        notification.style.border = '2px solid #ff4444';
        notification.style.padding = '15px';
        notification.style.borderRadius = '8px';
        notification.style.textAlign = 'center';
        notification.style.cursor = 'pointer';
        
        // Create restart function
        const restartGame = () => {
            console.log('Restarting game...');
            this.health = 100;
            this.currentQuestionIndex = 0; // Reset to first question
            this.updateHealthBar();
            this.clearNotification();
            this.answerInput.disabled = false; // Re-enable input
            this.answerInput.value = ''; // Clear input
            this.loadQuestion();
            notification.onclick = null;
            
            // Remove the special game over event listener from button
            this.checkButton.removeEventListener('click', restartGame);
            this.isGameOver = false;
        };
        
        // Add restart functionality to notification
        notification.onclick = restartGame;
        
        // Add restart functionality to CHECK button
        this.checkButton.addEventListener('click', restartGame);
        this.checkButton.disabled = false; // Enable the button for restart
        this.checkButton.textContent = 'RESTART'; // Change button text
        this.answerInput.disabled = true; // Disable input
        this.isGameOver = true; // Flag to track game over state
    }
    
    setupEventListeners() {
        // Add event listener for answer input (Enter key)
        this.answerInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.submitAnswer();
            }
        });
        
        // Add event listener for check button
        this.checkButton.addEventListener('click', () => {
            this.submitAnswer();
        });
        
        // Enable/disable button based on input
        this.answerInput.addEventListener('input', () => {
            this.checkButton.disabled = !this.answerInput.value.trim();
        });
        
        // Initially disable button if no input
        this.checkButton.disabled = true;
    }
    
    async loadQuestion() {
        try {
            this.questionElement.textContent = 'Loading question...';
            this.checkButton.disabled = true;
            this.checkButton.textContent = 'CHECK'; // Reset button text
            
            // Check if we have questions available
            if (this.questions.length === 0) {
                throw new Error('No questions available');
            }
            
            // Check if we've reached the end of questions
            if (this.currentQuestionIndex >= this.questions.length) {
                this.currentQuestionIndex = 0; // Loop back to start
            }
            
            // Get current question
            const questionKey = this.questions[this.currentQuestionIndex];
            console.log('Debug loadQuestion:');
            console.log('- currentQuestionIndex:', this.currentQuestionIndex);
            console.log('- questions array:', this.questions);
            console.log('- questionKey:', questionKey);
            console.log('- typeof questionKey:', typeof questionKey);
            
            this.currentQuestion = {
                word: questionKey,
                data: window.sessionData.questions[questionKey]
            };
            
            console.log('- currentQuestion:', this.currentQuestion);
            
            // Display the question asking for German translation
            const questionText = `"${questionKey}"`;
            this.displayQuestion(questionText);
            
        } catch (error) {
            console.error('Error loading question:', error);
            
            // Display error in the UI
            this.displayError(`Failed to load question: ${error.message}`);
        }
        
        // Always re-enable button state management after loading
        setTimeout(() => {
            this.checkButton.disabled = !this.answerInput.value.trim();
        }, 100);
    }
    
    displayQuestion(questionText) {
        this.questionElement.textContent = questionText;
    }
    
    displayError(errorMessage) {
        // Display error in the notification area
        const notification = document.querySelector('.div-notification');
        
        // Determine error type and customize message
        let errorTitle = '⚠️ Error';
        let additionalInfo = 'Using offline mode with sample questions...';
        
        if (errorMessage.includes('Failed to fetch') || errorMessage.includes('Network request failed')) {
            errorTitle = '🌐 Network Error';
            additionalInfo = 'Check your internet connection. Using offline questions...';
        } else if (errorMessage.includes('HTTP error! status: 500') || errorMessage.includes('HTTP error! status: 503')) {
            errorTitle = '🔧 Server Error';
            additionalInfo = 'API server is temporarily down. Using offline questions...';
        } else if (errorMessage.includes('HTTP error! status: 404')) {
            errorTitle = '🔍 API Not Found';
            additionalInfo = 'API endpoint not available. Using offline questions...';
        }
        
        notification.innerHTML = `
            <div style="font-weight: bold; margin-bottom: 5px; color: #721c24;">
                ${errorTitle}
            </div>
            <div style="font-size: 14px; color: #721c24;">
                ${errorMessage}
            </div>
            <div style="font-size: 12px; color: #666; margin-top: 8px;">
                ${additionalInfo}
            </div>
        `;
        
        notification.style.backgroundColor = '#f8d7da';
        notification.style.color = '#721c24';
        notification.style.border = '2px solid #f5c6cb';
        notification.style.padding = '15px';
        notification.style.borderRadius = '8px';
        notification.style.textAlign = 'center';
        
    }
    
    getCorrectAnswerMessage() {
        if (!this.currentQuestion || !this.currentQuestion.data) {
            return "Incorrect! Try again.";
        }
        
        const questionData = this.currentQuestion.data;
        const germanWord = questionData.de;
        const gender = questionData.gender;
        
        // Get the correct article
        let article = "das"; // default
        if (gender === "masculine" || gender === "male") {
            article = "der";
        } else if (gender === "feminine" || gender === "female") {
            article = "die";
        }
        
        const correctAnswer = `${article} ${germanWord}`;
        
        return `The correct answer is: "${correctAnswer}"`;
    }
    
    async submitAnswer() {
        // Don't process answers if game is over (button is being used for restart)
        if (this.isGameOver) {
            return; // The restart functionality is handled by the event listener in gameOver()
        }
        
        const userAnswer = this.answerInput.value.trim();
        
        if (!userAnswer) {
            alert('Please enter an answer');
            return;
        }
        
        console.log('Submitting answer for question:', this.currentQuestion.word);
        console.log('Available questions:', this.questions);
        
        try {
            // Send answer to Flask validation endpoint
            const validationUrl = `${this.apiUrl}/validate?question=${encodeURIComponent(this.currentQuestion.word)}&answer=${encodeURIComponent(userAnswer)}`;
            console.log('Validation URL:', validationUrl);
            const response = await fetch(validationUrl);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            // Convert the result format to match what handleAnswerResult expects
            const formattedResult = {
                correct: result.result === true,
                message: result.result === true ? 
                    "Richtig! Gut gemacht!" : 
                    this.getCorrectAnswerMessage()
            };
            
            this.handleAnswerResult(formattedResult);
            
        } catch (error) {
            console.error('Error submitting answer:', error);
            
            // Display error in the UI
            this.displayError(`Failed to submit answer: ${error.message}`);
            
        }
    }
    
    handleAnswerResult(result) {
        console.log('Handling answer result:', result);

        // Update health based on answer
        if (result.correct) {
            this.increaseHealth(); // Small health boost for correct answers
            console.log('Answer correct, loading next question in 1 second...');
        } else {
            this.decreaseHealth(10); // Significant health loss for wrong answers
            console.log('Answer incorrect, re-enabling button in 1 second...');
        }

        // Check if game is over after health change
        if (this.health <= 0) {
            console.log('Health is 0, triggering game over...');
            this.gameOver();
            return; // Exit early, don't continue with normal flow
        }

        // Display result in notification area
        const notification = document.querySelector('.div-notification');
        
        // Clear any existing content and show the result
        const statusText = result.correct ? '✓ Correct!' : '✗ Incorrect!';
        const displayText = `${statusText}\n${result.message}`;
        
        notification.innerHTML = `
            <div style="font-weight: bold; white-space: pre-line;">
                ${displayText}
            </div>
        `;
        
        notification.style.backgroundColor = result.correct ? '#d4edda' : '#f8d7da';
        notification.style.color = result.correct ? '#155724' : '#721c24';
        notification.style.border = `2px solid ${result.correct ? '#c3e6cb' : '#f5c6cb'}`;
        notification.style.padding = '15px';
        notification.style.borderRadius = '8px';
        notification.style.textAlign = 'center';
        
        // Disable the check button temporarily
        this.checkButton.disabled = true;

        // Load next question after showing the correct answer
        setTimeout(() => {
            console.log('Loading next question now...');
            this.answerInput.value = '';
            // this.clearNotification();
            this.currentQuestionIndex++; // Move to next question
            this.loadQuestion();
        }, 1000);

    }
    
    clearNotification() {
        const notification = document.querySelector('.div-notification');
        notification.innerHTML = '';
        notification.style.backgroundColor = '';
        notification.style.color = '';
        notification.style.border = '';
        notification.style.padding = '';
        notification.style.textAlign = '';
    }
}

// Initialize the quiz app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new QuizApp();
});

