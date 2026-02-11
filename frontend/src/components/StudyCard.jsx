import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { PitchAccent } from './PitchAccent';
import { confirmStudyItem, getStudyItems } from '../api';

const Card = ({ item, onNext }) => {
    const [isFlipped, setIsFlipped] = useState(false);

    const handleConfirm = async (e) => {
        e.stopPropagation();
        await confirmStudyItem(item.word);
        setIsFlipped(false); // Reset for next card (though key change handles it too)
        onNext();
    };

    return (
        <div className="flex flex-col items-center justify-center h-full w-full max-w-md mx-auto perspective-1000">
            <motion.div
                className="w-full aspect-[3/4] max-h-[600px] bg-white rounded-3xl shadow-xl cursor-pointer relative preserve-3d transition-all duration-500"
                onClick={() => setIsFlipped(!isFlipped)}
                initial={{ rotateY: 0 }}
                animate={{ rotateY: isFlipped ? 180 : 0 }}
                transition={{ duration: 0.6 }}
                style={{ transformStyle: 'preserve-3d' }}
            >
                {/* Front */}
                <div className="absolute inset-0 backface-hidden flex flex-col items-center justify-center p-8 text-center bg-paper rounded-3xl border-2 border-tatami" style={{ backfaceVisibility: 'hidden' }}>
                    <h2 className="text-6xl font-black mb-4 text-charcoal select-none">{item.word}</h2>
                    {/* Optional: Show kana if kanji is hard? Usually hidden */}
                    <p className="text-gray-400 mt-12 animate-pulse font-bold uppercase tracking-widest text-xs">Tap to Flip</p>
                </div>

                {/* Back */}
                <div className="absolute inset-0 backface-hidden flex flex-col items-center justify-center p-8 text-center bg-white rounded-3xl border-2 border-crimson" style={{ transform: 'rotateY(180deg)', backfaceVisibility: 'hidden' }}>
                    <div className="mb-6 scale-90">
                        <PitchAccent kana={item.kana} pattern={item.pitch_pattern} />
                    </div>
                    {/* <p className="text-2xl font-bold text-charcoal mb-1">{item.kana}</p> */}
                    <p className="text-lg italic text-gray-500 mb-6 font-serif">{item.romaji}</p>
                    <div className="flex-1 flex items-center justify-center">
                         <p className="text-3xl font-black text-crimson mb-4 leading-tight">{item.meaning}</p>
                    </div>

                    {item.example_sentence && (
                        <div className="bg-gray-50 p-4 rounded-xl text-sm italic text-gray-600 w-full mt-4 border border-gray-100">
                            "{item.example_sentence}"
                        </div>
                    )}
                </div>
            </motion.div>

            <AnimatePresence>
                {isFlipped && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 20 }}
                        className="absolute bottom-[-80px] w-full flex justify-center"
                    >
                        <button
                            onClick={handleConfirm}
                            className="px-8 py-4 bg-crimson text-white rounded-full font-bold text-xl shadow-lg shadow-crimson/40 hover:scale-105 transition-transform flex items-center gap-2"
                        >
                            <span>Got it!</span>
                            <span className="bg-white/20 rounded-full w-6 h-6 flex items-center justify-center text-sm">→</span>
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

    if (loading) return <div className="flex items-center justify-center h-full"><div className="animate-spin text-4xl">⛩️</div></div>;

    if (!items || items.length === 0) return (
        <div className="flex flex-col items-center justify-center h-full text-center">
            <h2 className="text-2xl font-bold text-gray-500">No new items to study!</h2>
            <button onClick={onComplete} className="mt-4 text-crimson font-bold underline">Go Back</button>
        </div>
    );

    if (currentIndex >= items.length) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-center animate-in fade-in zoom-in">
                <div className="text-6xl mb-4">🎉</div>
                <h2 className="text-4xl font-black text-crimson mb-4">Session Complete!</h2>
                <p className="text-xl mb-8 text-gray-600">You learned {items.length} new words.</p>
                <button onClick={onComplete} className="px-8 py-3 bg-charcoal text-white rounded-xl font-bold hover:bg-black transition-colors">Return to Dojo</button>
            </div>
        );
    }

    return (
        <div className="h-full flex flex-col">
            <div className="w-full bg-gray-200 h-2 rounded-full mb-8 overflow-hidden">
                <div
                    className="bg-crimson h-full transition-all duration-500"
                    style={{ width: `${((currentIndex) / items.length) * 100}%` }}
                />
            </div>
            <div className="flex-1 flex items-center justify-center pb-20">
                <Card
                    key={currentIndex} // Key change forces remount for fresh state
                    item={items[currentIndex]}
                    onNext={() => setCurrentIndex(currentIndex + 1)}
                />
            </div>
        </div>
    );
};
