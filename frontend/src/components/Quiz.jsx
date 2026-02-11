import React, { useState, useEffect } from 'react';
import { getQuizQuestion, submitQuizAnswer } from '../api';
import { clsx } from 'clsx';
import { motion, AnimatePresence } from 'framer-motion';
import confetti from 'canvas-confetti';
import { ArrowLeft, Loader2, CheckCircle2, XCircle } from 'lucide-react';

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
        <div className="flex flex-col items-center max-w-2xl mx-auto w-full pb-20 relative">
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-xs font-black text-gray-400 mb-8 uppercase tracking-[0.2em] border border-gray-200 px-3 py-1 rounded-full backdrop-blur-sm bg-white/50"
            >
                {question.type.replace('_', ' ')}
            </motion.div>

            <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ type: "spring", stiffness: 200, damping: 20 }}
                className="text-4xl font-black text-charcoal mb-12 text-center leading-relaxed"
            >
                {question.word ? (
                    <span>
                        Meaning of: <br/>
                        <span className="text-7xl text-crimson inline-block my-6 tracking-tighter drop-shadow-sm">{question.word}</span>
                        {question.kana && <div className="text-2xl text-gray-400 font-medium font-serif italic tracking-wider">{question.kana}</div>}
                    </span>
                ) : (
                    question.question_text
                )}
            </motion.div>

            {question.type === 'multiple_choice' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full px-4">
                    {question.options.map((opt, i) => (
                        <motion.button
                            key={opt}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: i * 0.1 }}
                            onClick={() => setSelected(opt)}
                            className={clsx(
                                "p-6 rounded-2xl border-2 text-xl font-bold transition-all shadow-sm hover:-translate-y-1 active:scale-95 text-left relative overflow-hidden group",
                                selected === opt ? "border-crimson bg-crimson text-white shadow-lg shadow-crimson/30 scale-[1.02]" : "border-gray-100 bg-white text-charcoal hover:border-crimson/30"
                            )}
                        >
                            <span className="relative z-10">{opt}</span>
                            {selected === opt && (
                                <motion.div
                                    layoutId="selectedChoice"
                                    className="absolute inset-0 bg-gradient-to-r from-crimson to-red-600"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                />
                            )}
                        </motion.button>
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
                        className="w-full p-6 text-3xl font-bold border-b-4 border-tatami bg-transparent focus:border-crimson focus:outline-none text-center placeholder-gray-300 transition-colors"
                        onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
                        autoFocus
                    />
                </div>
            )}

            {question.type === 'assemble' && (
                <div className="w-full space-y-8 px-4">
                    <div className="min-h-[100px] p-8 bg-white rounded-3xl border-2 border-dashed border-gray-300 flex flex-wrap gap-3 items-center justify-center shadow-inner relative transition-colors hover:border-crimson/30">
                        <AnimatePresence>
                            {assembled.map((word, idx) => (
                                <motion.button
                                    layoutId={`token-${word}`}
                                    key={`${word}-${idx}`}
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    exit={{ scale: 0 }}
                                    onClick={() => {
                                        setAssembled(prev => prev.filter((_, i) => i !== idx));
                                        setPool(prev => [...prev, word]);
                                    }}
                                    className="px-5 py-3 bg-crimson text-white rounded-xl font-bold hover:scale-105 transition-transform shadow-md border-b-4 border-red-800"
                                >
                                    {word}
                                </motion.button>
                            ))}
                        </AnimatePresence>
                        {assembled.length === 0 && <span className="absolute text-gray-400 italic font-medium animate-pulse">Tap blocks below to build</span>}
                    </div>
                    <div className="flex flex-wrap gap-3 justify-center">
                        <AnimatePresence>
                            {pool.map((word, idx) => (
                                <motion.button
                                    layoutId={`token-${word}`}
                                    key={`${word}-${idx}`}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, scale: 0.5 }}
                                    onClick={() => {
                                        setPool(prev => prev.filter((_, i) => i !== idx));
                                        setAssembled(prev => [...prev, word]);
                                    }}
                                    className="px-5 py-3 bg-white border-b-4 border-gray-200 text-charcoal rounded-xl font-bold hover:bg-gray-50 hover:border-gray-300 transition-all active:translate-y-1 active:border-b-0 active:mt-1 shadow-sm"
                                >
                                    {word}
                                </motion.button>
                            ))}
                        </AnimatePresence>
                    </div>
                </div>
            )}

            <button
                onClick={handleSubmit}
                className="mt-16 px-16 py-5 bg-charcoal text-white rounded-full font-black text-xl shadow-xl hover:bg-black transition-all hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 ring-4 ring-transparent hover:ring-gray-200"
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
            if (res.correct) {
                confetti({
                    particleCount: 100,
                    spread: 60,
                    origin: { y: 0.8 },
                    colors: ['#22c55e', '#ffffff'] // Green/White
                });
            }
        } catch (err) {
            console.error(err);
            alert("Failed to submit answer.");
        }
    };

    if (loading) return <div className="flex justify-center items-center h-full"><Loader2 className="animate-spin text-crimson" size={48} /></div>;

    if (result) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-center animate-in fade-in zoom-in duration-300 max-w-lg mx-auto">
                <motion.div
                    initial={{ scale: 0, rotate: -45 }}
                    animate={{ scale: 1, rotate: 0 }}
                    transition={{ type: "spring", stiffness: 200, damping: 15 }}
                    className={clsx("text-9xl mb-8 filter drop-shadow-2xl", result.correct ? "" : "")}
                >
                    {result.correct ? <CheckCircle2 size={120} className="text-green-500" /> : <XCircle size={120} className="text-red-500" />}
                </motion.div>

                <h2 className={clsx("text-5xl font-black mb-4 tracking-tighter italic uppercase", result.correct ? "text-green-600" : "text-red-500")}>
                    {result.correct ? "Correct!" : "Wrong!"}
                </h2>

                {!result.correct && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mb-8 p-6 bg-red-50 rounded-2xl border-l-4 border-red-500 w-full shadow-sm text-left"
                    >
                        <p className="text-red-400 mb-2 font-bold text-xs uppercase tracking-widest">Correct Answer</p>
                        <p className="text-4xl font-black text-charcoal">{result.correct_answers[0]}</p>
                    </motion.div>
                )}

                {result.explanation && (
                    <div className="bg-paper p-6 rounded-2xl border border-tatami mb-8 w-full italic text-gray-600 font-serif leading-relaxed text-lg shadow-sm">
                        "{result.explanation}"
                    </div>
                )}

                <div className="flex gap-4 mb-12">
                     <div className="px-6 py-3 bg-gradient-to-br from-yellow-100 to-yellow-50 text-yellow-700 rounded-xl font-black flex items-center gap-2 border border-yellow-200 shadow-sm">
                        <span>✨ +{result.xp_gained} XP</span>
                     </div>
                     {result.gems_awarded > 0 && (
                        <div className="px-6 py-3 bg-gradient-to-br from-purple-100 to-purple-50 text-purple-700 rounded-xl font-black flex items-center gap-2 border border-purple-200 shadow-sm">
                            <span>💎 +{result.gems_awarded}</span>
                        </div>
                     )}
                </div>

                <div className="flex gap-4 w-full">
                    <button onClick={onExit} className="flex-1 py-4 text-gray-400 font-bold hover:bg-gray-100 rounded-2xl transition-colors">
                        Quit
                    </button>
                    <button
                        onClick={loadQuestion}
                        className="flex-[2] py-4 bg-charcoal text-white rounded-2xl font-bold text-lg shadow-xl hover:scale-[1.02] transition-transform flex items-center justify-center gap-2 active:scale-95"
                    >
                        Next Question <span className="text-white/50">→</span>
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="h-full flex flex-col max-w-2xl mx-auto">
            <button onClick={onExit} className="self-start mb-8 text-gray-400 hover:text-charcoal font-bold flex items-center gap-2 transition-colors px-4 py-2 hover:bg-gray-100 rounded-full">
                <ArrowLeft size={20} />
                <span>Quit</span>
            </button>
            <div className="flex-1 flex items-center justify-center">
                <AnimatePresence mode="wait">
                    <motion.div
                        key={question?.question_id}
                        initial={{ opacity: 0, x: 50 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -50 }}
                        transition={{ duration: 0.3 }}
                        className="w-full"
                    >
                        <Question question={question} onAnswer={handleAnswer} />
                    </motion.div>
                </AnimatePresence>
            </div>
        </div>
    );
};
