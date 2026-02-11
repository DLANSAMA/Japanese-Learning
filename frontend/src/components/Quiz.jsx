import React, { useState, useEffect } from 'react';
import { getQuizQuestion, submitQuizAnswer } from '../api';
import { clsx } from 'clsx';

const Question = ({ question, onAnswer }) => {
    const [input, setInput] = useState('');
    const [selected, setSelected] = useState(null);
    const [assembled, setAssembled] = useState([]);
    const [pool, setPool] = useState(question.options || []);

    useEffect(() => {
        setInput('');
        setSelected(null);
        setAssembled([]);
        setPool(question.options || []);
    }, [question]);

    const handleSubmit = () => {
        let ans = input;
        if (question.type === 'multiple_choice') ans = selected;
        if (question.type === 'assemble') ans = assembled.join(' ');

        if (!ans) return;
        onAnswer(ans);
    };

    return (
        <div className="flex flex-col items-center max-w-2xl mx-auto w-full">
            <div className="text-xs font-black text-gray-400 mb-6 uppercase tracking-[0.2em] border border-gray-200 px-3 py-1 rounded-full">{question.type.replace('_', ' ')}</div>

            <div className="text-3xl font-black text-charcoal mb-10 text-center leading-relaxed">
                {question.word ? (
                    <span>
                        Meaning of: <br/>
                        <span className="text-6xl text-crimson inline-block my-4">{question.word}</span>
                        {question.kana && <div className="text-xl text-gray-400 font-medium">{question.kana}</div>}
                    </span>
                ) : (
                    question.question_text
                )}
            </div>

            {question.type === 'multiple_choice' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full px-4">
                    {question.options.map((opt) => (
                        <button
                            key={opt}
                            onClick={() => setSelected(opt)}
                            className={clsx(
                                "p-6 rounded-2xl border-2 text-xl font-bold transition-all shadow-sm hover:-translate-y-1 active:scale-95",
                                selected === opt ? "border-crimson bg-crimson text-white shadow-lg shadow-crimson/30" : "border-gray-100 bg-white text-charcoal hover:border-crimson/30"
                            )}
                        >
                            {opt}
                        </button>
                    ))}
                </div>
            )}

            {question.type === 'input' && (
                <div className="w-full px-8">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type the meaning..."
                        className="w-full p-6 text-2xl font-bold border-2 border-tatami rounded-2xl focus:border-crimson focus:ring-4 focus:ring-crimson/10 focus:outline-none shadow-inner bg-white text-center"
                        onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
                        autoFocus
                    />
                </div>
            )}

            {question.type === 'assemble' && (
                <div className="w-full space-y-6 px-4">
                    <div className="min-h-[80px] p-6 bg-white rounded-2xl border-2 border-dashed border-gray-300 flex flex-wrap gap-2 items-center justify-center shadow-inner">
                        {assembled.map((word, idx) => (
                            <button
                                key={`${word}-${idx}`}
                                onClick={() => {
                                    setAssembled(prev => prev.filter((_, i) => i !== idx));
                                    setPool(prev => [...prev, word]);
                                }}
                                className="px-4 py-2 bg-crimson text-white rounded-full font-bold hover:scale-105 transition-transform shadow-md"
                            >
                                {word}
                            </button>
                        ))}
                        {assembled.length === 0 && <span className="text-gray-400 italic font-medium">Tap words below to build sentence</span>}
                    </div>
                    <div className="flex flex-wrap gap-3 justify-center">
                        {pool.map((word, idx) => (
                            <button
                                key={`${word}-${idx}`}
                                onClick={() => {
                                    setPool(prev => prev.filter((_, i) => i !== idx));
                                    setAssembled(prev => [...prev, word]);
                                }}
                                className="px-4 py-2 bg-white border-2 border-gray-100 shadow-sm rounded-full font-bold text-gray-600 hover:bg-gray-50 hover:border-gray-300 transition-all active:scale-95"
                            >
                                {word}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            <button
                onClick={handleSubmit}
                className="mt-12 px-12 py-4 bg-charcoal text-white rounded-full font-black text-xl shadow-xl hover:bg-black transition-transform active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={
                    (question.type === 'multiple_choice' && !selected) ||
                    (question.type === 'input' && !input) ||
                    (question.type === 'assemble' && assembled.length === 0)
                }
            >
                Submit Answer
            </button>
        </div>
    );
};

export const Quiz = ({ onExit }) => {
    const [question, setQuestion] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(true);

    const loadQuestion = () => {
        setLoading(true);
        setResult(null);
        getQuizQuestion().then(q => {
            setQuestion(q);
            setLoading(false);
        }).catch(err => {
            console.error(err);
            if (err.response && err.response.status === 404) {
                 alert("No learned items to review! Go to Study Mode first.");
            } else {
                 alert("Error loading quiz.");
            }
            onExit();
        });
    };

    useEffect(() => {
        loadQuestion();
    }, []);

    const handleAnswer = async (ans) => {
        try {
            const res = await submitQuizAnswer(question.question_id, ans);
            setResult(res);
        } catch (err) {
            console.error(err);
            alert("Failed to submit answer.");
        }
    };

    if (loading) return <div className="flex justify-center items-center h-full"><div className="animate-spin text-4xl">⚔️</div></div>;

    if (result) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-center animate-in fade-in zoom-in duration-300">
                <div className={clsx("text-8xl mb-6", result.correct ? "animate-bounce" : "animate-shake")}>
                    {result.correct ? '✅' : '❌'}
                </div>
                <h2 className={clsx("text-4xl font-black mb-2", result.correct ? "text-green-600" : "text-red-500")}>
                    {result.correct ? "Correct!" : "Wrong!"}
                </h2>
                {!result.correct && (
                    <div className="mb-6 p-4 bg-red-50 rounded-xl border border-red-100">
                        <p className="text-red-400 mb-1 font-bold text-xs uppercase tracking-widest">Correct Answer</p>
                        <p className="text-3xl font-black text-charcoal">{result.correct_answers[0]}</p>
                    </div>
                )}

                {result.explanation && (
                    <div className="bg-paper p-6 rounded-xl border border-tatami mb-8 max-w-md italic text-gray-600 font-serif leading-relaxed">
                        "{result.explanation}"
                    </div>
                )}

                <div className="flex gap-4 mb-8">
                     <div className="px-4 py-2 bg-yellow-100 text-yellow-700 rounded-lg font-bold flex items-center gap-2 border border-yellow-200">
                        <span>✨ +{result.xp_gained} XP</span>
                     </div>
                     {result.gems_awarded > 0 && (
                        <div className="px-4 py-2 bg-purple-100 text-purple-700 rounded-lg font-bold flex items-center gap-2 border border-purple-200">
                            <span>💎 +{result.gems_awarded}</span>
                        </div>
                     )}
                </div>

                <button
                    onClick={loadQuestion}
                    className="mt-4 px-10 py-4 bg-crimson text-white rounded-full font-bold text-lg shadow-xl shadow-crimson/30 hover:scale-105 transition-transform flex items-center gap-2"
                >
                    Next Question <span className="text-white/50">→</span>
                </button>
            </div>
        );
    }

    return (
        <div className="h-full flex flex-col">
            <button onClick={onExit} className="self-start mb-8 text-gray-400 hover:text-charcoal font-bold flex items-center gap-2 transition-colors">
                <span>←</span> Quit
            </button>
            <Question question={question} onAnswer={handleAnswer} />
        </div>
    );
};
