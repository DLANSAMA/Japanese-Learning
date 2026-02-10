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
    updateStudyProgress();
    showStudyCard();
}

function updateStudyProgress() {
    const percent = (currentStudyIndex / currentStudyQueue.length) * 100;
    document.getElementById('study-progress').style.width = `${percent}%`;
}

function showStudyCard() {
    if (currentStudyIndex >= currentStudyQueue.length) {
        alert("Session Complete!");
        returnToDashboard();
        return;
    }
    updateStudyProgress();

    currentStudyItem = currentStudyQueue[currentStudyIndex];
    const container = document.getElementById('study-card-container');

    // Ruby Text Logic
    const kanji = currentStudyItem.word;
    const reading = currentStudyItem.kana;

    // Removed 'block' class to respect display: ruby
    const frontContent = `
        <ruby class="text-6xl font-bold mb-4">${kanji}<rt>${reading}</rt></ruby>
    `;

    container.innerHTML = `
        <div class="flip-card" onclick="this.classList.toggle('flipped')">
            <div class="flip-card-inner">
                <div class="flip-card-front">
                    ${frontContent}
                    <div class="text-xl text-cyan-400 mt-8">Click to Flip</div>
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
    const feedback = document.getElementById('quiz-feedback');
    feedback.textContent = '';
    feedback.className = '';
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

    // Render Question with Ruby if word data is present
    const qEl = document.getElementById('quiz-question');

    if (q.word && q.kana && q.question_text.includes(q.word)) {
        // Replace the plain word with ruby tag in the question text
        // Need to be careful replacing text content.
        // If question text is "Meaning of: Word (Kana)", we want "Meaning of: <ruby>Word<rt>Kana</rt></ruby>"
        // Backend text format: "Meaning of: Word (Kana)" or just "Word" depending on logic.
        // Let's assume we construct it manually if we have data.

        if (q.type === 'input') {
             // Reconstruct meaningful display
             qEl.innerHTML = `Meaning of: <ruby>${q.word}<rt>${q.kana}</rt></ruby>`;
        } else {
             qEl.textContent = q.question_text;
        }
    } else {
        qEl.textContent = q.question_text;
    }

    const inputContainer = document.getElementById('quiz-input-container');
    const optionsContainer = document.getElementById('quiz-options');

    if (q.type === 'multiple_choice') {
        inputContainer.classList.add('hidden');
        optionsContainer.classList.remove('hidden');
        optionsContainer.innerHTML = '';

        q.options.forEach(opt => {
            const btn = document.createElement('button');
            btn.className = "p-4 bg-gray-700 hover:bg-gray-600 rounded text-xl font-bold transition border border-gray-600";
            btn.textContent = opt;
            btn.onclick = () => submitQuizAnswer(opt);
            optionsContainer.appendChild(btn);
        });
    } else {
        inputContainer.classList.remove('hidden');
        optionsContainer.classList.add('hidden');
        document.getElementById('quiz-input').focus();
    }
}

async function submitQuizAnswer(answer = null) {
    if (!answer) {
        answer = document.getElementById('quiz-input').value;
    }

    const card = document.getElementById('quiz-card');

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
        feedback.className = "mt-4 text-xl font-bold h-8 text-green-400 animate-pulse";
        card.classList.add('border-green-500');
        setTimeout(() => card.classList.remove('border-green-500'), 500);
        playAudio(result.correct_answers[0]);
    } else {
        feedback.textContent = `❌ Wrong! Answer: ${result.correct_answers[0]}`;
        feedback.className = "mt-4 text-xl font-bold h-8 text-red-400";
        // Shake animation
        card.classList.add('animate-shake', 'border-red-500');
        setTimeout(() => card.classList.remove('animate-shake', 'border-red-500'), 500);
    }

    setTimeout(loadNextQuestion, 2000);
}

function playAudio(text) {
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = 'ja-JP';
    window.speechSynthesis.speak(utter);
}
