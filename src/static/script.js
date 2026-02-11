let currentStudyQueue = [];
let currentStudyIndex = 0;
let currentStudyItem = null;
let currentQuizId = null;
let assembleCurrentSentence = [];

document.addEventListener('DOMContentLoaded', () => {
    fetchStats();
});

async function fetchStats() {
    const res = await fetch('/api/user');
    const data = await res.json();
    document.getElementById('stat-level').textContent = data.level;
    document.getElementById('stat-xp').textContent = data.xp;
    document.getElementById('stat-streak').textContent = data.streak;
    if (document.getElementById('stat-gems')) {
        document.getElementById('stat-gems').textContent = data.gems;
    }
}

function showView(viewId) {
    ['dashboard', 'study-view', 'quiz-view', 'map-view', 'shop-view'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.classList.add('hidden');
            el.classList.remove('flex');
        }
    });
    const view = document.getElementById(viewId);
    if (view) {
        view.classList.remove('hidden');
        if (viewId !== 'dashboard') view.classList.add('flex');
    }
}

function returnToDashboard() {
    fetchStats();
    showView('dashboard');
}

// --- Settings ---

async function loadSettings() {
    const res = await fetch('/api/settings');
    const data = await res.json();
    const trackSelect = document.getElementById('setting-track');
    if ([...trackSelect.options].some(o => o.value === data.track)) {
        trackSelect.value = data.track;
    } else {
        if (data.track) trackSelect.value = "General";
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

    const kanji = currentStudyItem.word;
    const reading = currentStudyItem.kana;

    const frontContent = `
        <ruby class="text-6xl font-bold mb-4">${kanji}<rt>${reading}</rt></ruby>
    `;

    // Example sentence check
    const sentenceHtml = currentStudyItem.example_sentence
        ? `<div class="mt-4 p-2 bg-gray-700 rounded text-cyan-200 text-lg italic">"${currentStudyItem.example_sentence}"</div>`
        : '';

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
                    ${sentenceHtml}
                    <div class="mt-4 text-sm text-gray-400">Tags: ${currentStudyItem.tags.join(', ')}</div>
                </div>
            </div>
        </div>
    `;
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

function setupAssembleQuiz(q) {
    const assembleContainer = document.getElementById('quiz-assemble-container');
    const inputContainer = document.getElementById('quiz-input-container');
    const optionsContainer = document.getElementById('quiz-options');

    inputContainer.classList.remove('hidden');
    optionsContainer.classList.add('hidden');
    assembleContainer.classList.remove('hidden');

    const poolArea = document.getElementById('pool-area');
    const assembleArea = document.getElementById('assemble-area');
    poolArea.innerHTML = '';
    assembleArea.innerHTML = '';
    assembleCurrentSentence = [];

    q.options.forEach(word => {
        const btn = document.createElement('button');
        btn.className = "px-4 py-2 bg-cyan-700 rounded-full font-bold text-white hover:scale-105 transition shadow shadow-cyan-500/50 m-1";
        btn.textContent = word;
        btn.onclick = () => {
            if (btn.parentElement === poolArea) {
                poolArea.removeChild(btn);
                assembleArea.appendChild(btn);
                assembleCurrentSentence.push(word);
            } else {
                assembleArea.removeChild(btn);
                poolArea.appendChild(btn);
                const index = assembleCurrentSentence.indexOf(word);
                if (index > -1) assembleCurrentSentence.splice(index, 1);
            }
        };
        poolArea.appendChild(btn);
    });
}

async function loadNextQuestion() {
    const feedback = document.getElementById('quiz-feedback');
    feedback.textContent = '';
    feedback.className = '';

    const inputEl = document.getElementById('quiz-input');
    inputEl.value = '';
    inputEl.classList.remove('hidden');

    const res = await fetch('/api/quiz/vocab');
    if (!res.ok) {
        const err = await res.json();
        alert(err.detail);
        returnToDashboard();
        return;
    }

    const q = await res.json();
    currentQuizId = q.question_id;

    const qEl = document.getElementById('quiz-question');
    if (q.word && q.kana && q.question_text.includes(q.word)) {
        if (q.type === 'input') {
             qEl.innerHTML = `Meaning of: <ruby>${q.word}<rt>${q.kana}</rt></ruby>`;
        } else {
             qEl.textContent = q.question_text;
        }
    } else {
        qEl.textContent = q.question_text;
    }

    const inputContainer = document.getElementById('quiz-input-container');
    const optionsContainer = document.getElementById('quiz-options');
    const assembleContainer = document.getElementById('quiz-assemble-container');

    inputContainer.classList.add('hidden');
    optionsContainer.classList.add('hidden');
    if (assembleContainer) assembleContainer.classList.add('hidden');

    if (q.type === 'multiple_choice') {
        optionsContainer.classList.remove('hidden');
        optionsContainer.innerHTML = '';
        q.options.forEach(opt => {
            const btn = document.createElement('button');
            btn.className = "p-4 bg-gray-700 hover:bg-gray-600 rounded text-xl font-bold transition border border-gray-600";
            btn.textContent = opt;
            btn.onclick = () => submitQuizAnswer(opt);
            optionsContainer.appendChild(btn);
        });
    } else if (q.type === 'assemble') {
        setupAssembleQuiz(q);
        inputContainer.classList.remove('hidden');
        inputEl.classList.add('hidden');
    } else {
        inputContainer.classList.remove('hidden');
        inputEl.classList.remove('hidden');
        inputEl.focus();
    }
}

async function submitQuizAnswer(answer = null) {
    const assembleContainer = document.getElementById('quiz-assemble-container');
    const isAssemble = assembleContainer && !assembleContainer.classList.contains('hidden');

    if (isAssemble) {
        answer = assembleCurrentSentence.join(' ');
    } else if (!answer) {
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
        if (result.gems_awarded > 0) {
            feedback.textContent += " 💎 + " + result.gems_awarded;
        }
        feedback.className = "mt-4 text-xl font-bold h-8 text-green-400 animate-pulse";
        card.classList.add('border-green-500');
        setTimeout(() => card.classList.remove('border-green-500'), 500);

        if (typeof confetti === 'function') {
            confetti({
                particleCount: 50,
                spread: 60,
                origin: { y: 0.7 }
            });
        }

        playAudio(result.correct_answers[0]);
    } else {
        feedback.textContent = `❌ Wrong! Answer: ${result.correct_answers[0]}`;
        feedback.className = "mt-4 text-xl font-bold h-8 text-red-400";
        card.classList.add('animate-shake', 'border-red-500');
        setTimeout(() => card.classList.remove('animate-shake', 'border-red-500'), 500);
    }

    fetchStats();
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

            const meanings = item.meanings.join(', ');

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

// --- Gamification: Map, Shop ---

async function loadCurriculum() {
    const res = await fetch('/api/curriculum');
    const data = await res.json();
    const container = document.getElementById('map-container');
    container.innerHTML = '<div class="absolute w-2 bg-gray-700 h-full -z-10 left-1/2 transform -translate-x-1/2"></div>';

    data.units.forEach((unit, uIdx) => {
        const unitEl = document.createElement('div');
        unitEl.className = `w-full max-w-md bg-gray-800 p-4 rounded-xl border-l-4 border-${unit.color}-500 mb-4 shadow-lg z-0 relative`;
        unitEl.innerHTML = `
            <h3 class="text-xl font-bold text-${unit.color}-400">${unit.title}</h3>
            <p class="text-gray-400 text-sm">${unit.description}</p>
        `;
        container.appendChild(unitEl);

        unit.lessons.forEach((lesson, lIdx) => {
            const node = document.createElement('div');
            const locked = uIdx > 0;
            const statusColor = locked ? "gray" : unit.color;

            node.className = `w-24 h-24 rounded-full bg-gray-900 border-4 border-${statusColor}-500 flex items-center justify-center cursor-pointer hover:scale-110 transition shadow-lg shadow-${statusColor}-500/50 z-10`;
            node.innerHTML = `<div class="text-3xl">${lesson.type === 'boss' ? '⚔️' : '📚'}</div>`;

            if (!locked) {
                node.onclick = () => startLesson(lesson.id);
            } else {
                node.classList.add('opacity-50', 'cursor-not-allowed');
            }

            const label = document.createElement('div');
            label.className = "text-center mt-2 font-bold text-" + statusColor + "-400 bg-gray-900 px-2 rounded";
            label.textContent = lesson.title;

            const wrapper = document.createElement('div');
            wrapper.className = "flex flex-col items-center mb-12";
            wrapper.appendChild(node);
            wrapper.appendChild(label);

            container.appendChild(wrapper);
        });
    });
}

function startLesson(lessonId) {
    alert("Starting Lesson: " + lessonId);
    returnToDashboard();
    startStudy();
}

async function loadShop() {
    const res = await fetch('/api/shop');
    const items = await res.json();
    const container = document.getElementById('shop-container');
    container.innerHTML = '';

    items.forEach(item => {
        const el = document.createElement('div');
        el.className = "bg-gray-800 p-6 rounded-xl border border-yellow-500/30 flex flex-col items-center text-center shadow-lg hover:shadow-yellow-500/20 transition";
        el.innerHTML = `
            <div class="text-6xl mb-4">${item.icon}</div>
            <h3 class="text-2xl font-bold text-white mb-2">${item.name}</h3>
            <p class="text-gray-400 mb-4 h-12">${item.description}</p>
            <button onclick="buyItem('${item.id}', ${item.price})" class="px-6 py-2 bg-yellow-600 rounded-full font-bold text-black hover:bg-yellow-500 w-full flex justify-center items-center gap-2">
                <span>💎 ${item.price}</span>
            </button>
        `;
        container.appendChild(el);
    });
}

async function buyItem(itemId, price) {
    const res = await fetch('/api/shop/buy', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({item_id: itemId})
    });

    if (res.ok) {
        if (typeof confetti === 'function') {
            confetti({
                particleCount: 100,
                spread: 70,
                origin: { y: 0.6 }
            });
        }
        alert("Purchase Successful!");
        fetchStats();
    } else {
        const err = await res.json();
        alert("Error: " + err.detail);
    }
}
