import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { PitchAccent } from './PitchAccent';
import { confirmStudyItem, getStudyItems } from '../api';
import confetti from 'canvas-confetti';
import { useToast } from './ui/Toast';
import { ArrowLeft, Loader2, RefreshCcw } from 'lucide-react';

const Card = ({ item, onNext, isActive }) => {
    const [isFlipped, setIsFlipped] = useState(false);
    const { addToast } = useToast();

    // Reset flip state when item changes
    useEffect(() => {
        setIsFlipped(false);
    }, [item]);

    const handleFlip = useCallback(() => {
        setIsFlipped(prev => !prev);
    }, []);

    const handleConfirm = useCallback(async (e) => {
        e?.stopPropagation();
        try {
            await confirmStudyItem(item.word);
            addToast(`Learned: ${item.word}`, 'success', 2000);
            onNext();
        } catch (err) {
            addToast("Failed to save progress", 'error');
        }
    }, [item, onNext, addToast]);

    // Keyboard shortcuts
    useEffect(() => {
        if (!isActive) return;

        const handleKeyDown = (e) => {
            if (e.code === 'Space') {
                e.preventDefault();
                handleFlip();
            } else if (e.code === 'Enter' && isFlipped) {
                e.preventDefault();
                handleConfirm();
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [isActive, isFlipped, handleFlip, handleConfirm]);

    return (
        <div className="flex flex-col items-center justify-center h-full w-full max-w-md mx-auto perspective-1000 py-10 relative">
            <motion.div
                className="w-full aspect-[3/4] max-h-[550px] bg-white rounded-[2rem] shadow-2xl cursor-pointer relative preserve-3d transition-shadow hover:shadow-crimson/20"
                onClick={handleFlip}
                initial={{ rotateY: 90, opacity: 0 }}
                animate={{ rotateY: isFlipped ? 180 : 0, opacity: 1 }}
                transition={{ type: "spring", stiffness: 260, damping: 20 }}
                style={{ transformStyle: 'preserve-3d' }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
            >
                {/* Front */}
                <div className="absolute inset-0 backface-hidden flex flex-col items-center justify-center p-8 text-center bg-paper rounded-[2rem] border-[3px] border-tatami select-none overflow-hidden" style={{ backfaceVisibility: 'hidden' }}>
                    <div className="absolute top-0 left-0 w-full h-2 bg-crimson/20" />

                    <motion.h2
                        layoutId={`word-${item.word}`}
                        className="text-7xl font-black mb-6 text-charcoal tracking-tight drop-shadow-sm"
                    >
                        {item.word}
                    </motion.h2>

                    <div className="absolute bottom-10 left-0 w-full flex justify-center">
                        <span className="text-xs font-bold uppercase tracking-[0.2em] text-gray-400 bg-white/50 px-4 py-1 rounded-full backdrop-blur-sm border border-tatami animate-pulse">
                            Tap or Space to Flip
                        </span>
                    </div>
                </div>

                {/* Back */}
                <div
                    className="absolute inset-0 backface-hidden flex flex-col items-center justify-center p-8 text-center bg-white rounded-[2rem] border-[3px] border-crimson select-none overflow-hidden"
                    style={{ transform: 'rotateY(180deg)', backfaceVisibility: 'hidden' }}
                >
                    <div className="absolute top-0 left-0 w-full h-2 bg-crimson" />

                    <div className="mb-8 scale-90">
                        <PitchAccent kana={item.kana} pattern={item.pitch_pattern} />
                    </div>

                    <p className="text-lg italic text-gray-500 mb-8 font-serif border-b border-tatami pb-2 px-8">{item.romaji}</p>

                    <div className="flex-1 flex flex-col items-center justify-center w-full">
                         <p className="text-3xl font-black text-crimson mb-4 leading-tight drop-shadow-sm">{item.meaning}</p>
                    </div>

                    {item.example_sentence && (
                        <div className="bg-gray-50 p-5 rounded-xl text-sm italic text-gray-600 w-full mt-auto border border-gray-100 shadow-inner relative">
                            <span className="absolute top-2 left-2 text-2xl opacity-10 text-crimson font-serif">"</span>
                            {item.example_sentence}
                            <span className="absolute bottom-2 right-2 text-2xl opacity-10 text-crimson font-serif">"</span>
                        </div>
                    )}
                </div>
            </motion.div>

            <AnimatePresence>
                {isFlipped && (
                    <motion.div
                        initial={{ opacity: 0, y: 40, scale: 0.8 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 20, scale: 0.9 }}
                        className="absolute bottom-[-20px] w-full flex justify-center z-20"
                    >
                        <button
                            onClick={handleConfirm}
                            className="px-10 py-4 bg-crimson text-white rounded-full font-black text-xl shadow-xl shadow-crimson/40 hover:scale-105 hover:bg-red-600 transition-all flex items-center gap-3 active:scale-95 ring-4 ring-white"
                        >
                            <span>Got it!</span>
                            <div className="bg-white/20 rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold shadow-inner">↵</div>
                        </button>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export const StudySession = ({ onComplete }) => {
    const [items, setItems] = useState([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getStudyItems().then(data => {
            setItems(data);
            setLoading(false);
        }).catch(err => {
            console.error(err);
            setLoading(false);
        });
    }, []);

    // Session Complete Effect
    useEffect(() => {
        if (!loading && items.length > 0 && currentIndex >= items.length) {
            confetti({
                particleCount: 150,
                spread: 70,
                origin: { y: 0.6 },
                colors: ['#BC002D', '#D4AF37', '#FAF7F2']
            });
        }
    }, [currentIndex, items.length, loading]);

    if (loading) return (
        <div className="flex flex-col items-center justify-center h-full gap-4">
            <Loader2 className="animate-spin text-crimson" size={48} />
            <p className="text-gray-400 font-bold tracking-widest uppercase text-sm animate-pulse">Loading Cards...</p>
        </div>
    );

    if (!items || items.length === 0) return (
        <div className="flex flex-col items-center justify-center h-full text-center max-w-md mx-auto">
            <div className="text-6xl mb-6 bg-gray-100 p-8 rounded-full">🍵</div>
            <h2 className="text-3xl font-black text-charcoal mb-2">All caught up!</h2>
            <p className="text-gray-500 mb-8 font-medium">No new items in your queue. Check back later or add more from the dictionary.</p>
            <button onClick={onComplete} className="px-8 py-3 bg-white border-2 border-tatami text-charcoal rounded-xl font-bold hover:bg-gray-50 hover:border-crimson transition-all shadow-sm flex items-center gap-2">
                <ArrowLeft size={20} />
                <span>Return to Dojo</span>
            </button>
        </div>
    );

    if (currentIndex >= items.length) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-center animate-in fade-in zoom-in duration-500 max-w-lg mx-auto">
                <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", stiffness: 200, damping: 15 }}
                    className="mb-8 relative"
                >
                    <div className="absolute inset-0 bg-yellow-400 blur-3xl opacity-20 rounded-full animate-pulse" />
                    <div className="text-9xl relative z-10 drop-shadow-2xl">🎉</div>
                </motion.div>

                <h2 className="text-5xl font-black text-crimson mb-4 italic tracking-tighter">Session Complete!</h2>
                <p className="text-xl mb-12 text-gray-600 font-medium">You learned <span className="font-bold text-charcoal">{items.length}</span> new words today.</p>

                <div className="flex gap-4">
                    <button onClick={onComplete} className="px-8 py-4 bg-charcoal text-white rounded-2xl font-bold hover:bg-black transition-all shadow-xl hover:-translate-y-1 flex items-center gap-2">
                        <span>Return to Dojo</span>
                    </button>
                    <button onClick={() => window.location.reload()} className="px-6 py-4 bg-white border-2 border-tatami text-charcoal rounded-2xl font-bold hover:bg-gray-50 hover:border-crimson transition-all shadow-md hover:-translate-y-1">
                        <RefreshCcw size={24} />
                    </button>
                </div>
            </div>
        );
    }

    const progress = ((currentIndex) / items.length) * 100;

    return (
        <div className="h-full flex flex-col relative max-w-2xl mx-auto">
            <button onClick={onComplete} className="absolute top-0 left-0 p-2 hover:bg-gray-100 rounded-full text-gray-400 hover:text-charcoal transition-colors z-10">
                <ArrowLeft />
            </button>

            <div className="w-full bg-tatami/30 h-3 rounded-full mb-4 overflow-hidden mt-2 relative">
                <motion.div
                    className="bg-crimson h-full rounded-full relative overflow-hidden"
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    transition={{ type: "spring", stiffness: 100, damping: 20 }}
                >
                    <div className="absolute inset-0 bg-white/20 animate-[shimmer_2s_infinite]" />
                </motion.div>
            </div>

            <div className="text-right text-xs font-bold text-gray-400 uppercase tracking-widest mb-4">
                Card {currentIndex + 1} / {items.length}
            </div>

            <div className="flex-1 flex items-center justify-center pb-12">
                <AnimatePresence mode="wait">
                    <motion.div
                        key={currentIndex}
                        initial={{ opacity: 0, x: 100 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -100 }}
                        transition={{ type: "spring", stiffness: 200, damping: 25 }}
                        className="w-full h-full flex items-center justify-center"
                    >
                        <Card
                            item={items[currentIndex]}
                            onNext={() => setCurrentIndex(currentIndex + 1)}
                            isActive={true}
                        />
                    </motion.div>
                </AnimatePresence>
            </div>
        </div>
    );
};
