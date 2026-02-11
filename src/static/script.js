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

// --- Dictionary Search ---

async function searchDictionary() {
    const query = document.getElementById('search-input').value.trim();
    if (!query) return;

    const res = await fetch(`/api/dictionary/search?q=${encodeURIComponent(query)}`);
    const results = await res.json();

    const resultsContainer = document.getElementById('dictionary-results');
    resultsContainer.innerHTML = '';

    if (results.length === 0) {
        resultsContainer.innerHTML = '<div class="text-center text-gray-400">No results found.</div>';
    } else {
        results.forEach(item => {
            const el = document.createElement('div');
            el.className = "bg-gray-800 p-4 rounded-lg border border-gray-700 flex justify-between items-center";

            // Format meanings
            const meanings = item.meanings.join(', ');

            // Encode item data for the button
            // We need to be careful with quotes in JSON string when putting it in HTML attribute
            // Using a safer way: store data in a temporary map or just pass fields
            // Simpler: pass fields if simple, or use encoded JSON.
            // Let's use a click handler assignment to avoid quote escaping hell in HTML string.

            el.innerHTML = `
                <div>
                    <div class="text-xl font-bold text-cyan-300">
                        ${item.word} <span class="text-sm text-gray-400">(${item.kana})</span>
                    </div>
                    <div class="text-gray-300 mt-1">${meanings}</div>
                </div>
            `;

            const btn = document.createElement('button');
            btn.className = "ml-4 px-4 py-2 bg-green-600 rounded hover:bg-green-500 font-bold shadow-lg shadow-green-500/30 whitespace-nowrap";
            btn.textContent = "+ Study";
            btn.onclick = () => addToStudy(item);

            el.appendChild(btn);
            resultsContainer.appendChild(el);
        });
    }

    document.getElementById('dictionary-modal').classList.remove('hidden');
}

function closeDictionaryModal() {
    document.getElementById('dictionary-modal').classList.add('hidden');
}

async function addToStudy(item) {
    const res = await fetch('/api/dictionary/add', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            word: item.word,
            kana: item.kana,
            meanings: item.meanings
        })
    });

    if (res.ok) {
        alert(`Added ${item.word} to your study list!`);
    } else {
        const err = await res.json();
        alert(`Error: ${err.detail}`);
    }
}

// --- Settings ---

async function loadSettings() {
    const res = await fetch('/api/settings');
    const data = await res.json();
    // Ensure the value exists in dropdown options
    const trackSelect = document.getElementById('setting-track');
    if ([...trackSelect.options].some(o => o.value === data.track)) {
        trackSelect.value = data.track;
    } else {
        // Fallback or add dynamically?
        // Usually it should match one of the hardcoded options
        // If not, maybe set to General
        if (data.track) trackSelect.value = "General"; // Default fallback
    }

    document.getElementById('setting-theme').value = data.theme || "default";
}

function openSettings() {
    loadSettings();
    document.getElementById('settings-modal').classList.remove('hidden');
}

function closeSettings() {
    document.getElementById('settings-modal').classList.add('hidden');
}

async function saveSettings() {
    const track = document.getElementById('setting-track').value;
    const theme = document.getElementById('setting-theme').value;

    const res = await fetch('/api/settings', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({track: track, theme: theme})
    });

    if (res.ok) {
        alert("Settings Saved! New study sessions will use the " + track + " track.");
        closeSettings();
    } else {
        alert("Error saving settings");
    }
}
