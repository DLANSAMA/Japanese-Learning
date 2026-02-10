let currentStudyQueue = [];
let currentStudyIndex = 0;
let currentStudyItem = null;
let currentQuizId = null;

document.addEventListener('DOMContentLoaded', () => {
    fetchStats();
});

async function fetchStats() {
    const res = await fetch('/api/user');
    const data = await res.json();
    document.getElementById('stat-level').textContent = data.level;
    document.getElementById('stat-xp').textContent = data.xp;
    document.getElementById('stat-streak').textContent = data.streak;
}

function showView(viewId) {
    ['dashboard', 'study-view', 'quiz-view'].forEach(id => {
        document.getElementById(id).classList.add('hidden');
        document.getElementById(id).classList.remove('flex');
    });
    const view = document.getElementById(viewId);
    view.classList.remove('hidden');
    if (viewId !== 'dashboard') view.classList.add('flex');
}

function returnToDashboard() {
    fetchStats();
    showView('dashboard');
}

// --- Study Mode ---

async function startStudy() {
    const res = await fetch('/api/study');
    currentStudyQueue = await res.json();
    currentStudyIndex = 0;

    if (currentStudyQueue.length === 0) {
        alert("No new items to learn for this track!");
        return;
    }

    showView('study-view');
    showStudyCard();
}

function showStudyCard() {
    if (currentStudyIndex >= currentStudyQueue.length) {
        alert("Session Complete!");
        returnToDashboard();
        return;
    }

    currentStudyItem = currentStudyQueue[currentStudyIndex];
    const container = document.getElementById('study-card-container');

    container.innerHTML = `
        <div class="flip-card" onclick="this.classList.toggle('flipped')">
            <div class="flip-card-inner">
                <div class="flip-card-front">
                    <div class="text-6xl font-bold mb-4">${currentStudyItem.word}</div>
                    <div class="text-xl text-cyan-400">Click to Flip</div>
                </div>
                <div class="flip-card-back">
                    <div class="text-3xl font-bold mb-2">${currentStudyItem.kana}</div>
                    <div class="text-xl italic mb-4">${currentStudyItem.romaji}</div>
                    <div class="text-2xl text-yellow-300 font-bold">${currentStudyItem.meaning}</div>
                    <div class="mt-4 text-sm text-gray-400">Tags: ${currentStudyItem.tags.join(', ')}</div>
                </div>
            </div>
        </div>
    `;

    // Auto play audio on show?
    // playAudio(currentStudyItem.word);
}

async function confirmStudyItem() {
    await fetch('/api/study/confirm', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({word: currentStudyItem.word})
    });

    currentStudyIndex++;
    showStudyCard();
}

// --- Quiz Mode ---

async function startQuiz() {
    showView('quiz-view');
    loadNextQuestion();
}

async function loadNextQuestion() {
    document.getElementById('quiz-feedback').textContent = '';
    document.getElementById('quiz-input').value = '';

    const res = await fetch('/api/quiz/vocab');
    if (!res.ok) {
        const err = await res.json();
        alert(err.detail);
        returnToDashboard();
        return;
    }

    const q = await res.json();
    currentQuizId = q.question_id;

    document.getElementById('quiz-question').textContent = q.question_text;

    const inputContainer = document.getElementById('quiz-input-container');
    const optionsContainer = document.getElementById('quiz-options');

    if (q.type === 'multiple_choice') {
        inputContainer.classList.add('hidden');
        optionsContainer.classList.remove('hidden');
        optionsContainer.innerHTML = '';

        q.options.forEach(opt => {
            const btn = document.createElement('button');
            btn.className = "p-4 bg-gray-700 hover:bg-gray-600 rounded text-xl font-bold transition";
            btn.textContent = opt;
            btn.onclick = () => submitQuizAnswer(opt);
            optionsContainer.appendChild(btn);
        });
    } else {
        inputContainer.classList.remove('hidden');
        optionsContainer.classList.add('hidden');
    }
}

async function submitQuizAnswer(answer = null) {
    if (!answer) {
        answer = document.getElementById('quiz-input').value;
    }

    const res = await fetch('/api/quiz/answer', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            question_id: currentQuizId,
            answer: answer
        })
    });

    const result = await res.json();
    const feedback = document.getElementById('quiz-feedback');

    if (result.correct) {
        feedback.textContent = "✅ Correct! + " + result.xp_gained + " XP";
        feedback.className = "mt-4 text-xl font-bold h-8 text-green-400";
        playAudio(result.correct_answers[0]); // simplistic TTS trigger
    } else {
        feedback.textContent = `❌ Wrong! Answer: ${result.correct_answers[0]}`;
        feedback.className = "mt-4 text-xl font-bold h-8 text-red-400";
    }

    setTimeout(loadNextQuestion, 2000);
}

function playAudio(text) {
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = 'ja-JP';
    window.speechSynthesis.speak(utter);
}
