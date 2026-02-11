import React, { useState } from 'react';
import { searchDictionary, addToDictionary } from '../api';
import { Search, Loader2, Plus, Check } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useToast } from './ui/Toast';

export const Dictionary = () => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [adding, setAdding] = useState(null);
    const { addToast } = useToast();

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;
        setLoading(true);
        try {
            const res = await searchDictionary(query);
            setResults(res);
        } catch (err) {
            console.error(err);
            addToast("Search failed", 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleAdd = async (item) => {
        setAdding(item.word);
        try {
            await addToDictionary(item.word, item.kana, item.meanings);
            addToast(`Added ${item.word} to study list!`, 'success');
        } catch (err) {
            addToast(err.response?.data?.detail || "Failed to add word", 'error');
        } finally {
            setAdding(null);
        }
    };

    const resultVariants = {
        hidden: { opacity: 0, y: 20 },
        visible: i => ({
            opacity: 1,
            y: 0,
            transition: { delay: i * 0.05 }
        })
    };

    return (
        <div className="max-w-4xl mx-auto h-full flex flex-col pb-20">
            <motion.h1
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="text-5xl font-black text-charcoal mb-10 uppercase italic tracking-tighter drop-shadow-sm"
            >
                Dictionary
            </motion.h1>

            <motion.form
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                onSubmit={handleSearch}
                className="relative mb-12"
            >
                <div className="absolute inset-0 bg-crimson/5 rounded-2xl transform rotate-1 scale-105 opacity-0 group-hover:opacity-100 transition-opacity" />
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search English or Japanese..."
                    className="w-full p-6 pl-16 rounded-2xl border-4 border-tatami focus:border-crimson focus:outline-none shadow-inner text-xl font-bold bg-white transition-colors placeholder-gray-300"
                />
                <Search className="absolute left-6 top-1/2 -translate-y-1/2 text-gray-400" size={28} strokeWidth={2.5} />
                <button
                    type="submit"
                    disabled={loading}
                    className="absolute right-4 top-1/2 -translate-y-1/2 bg-charcoal text-white px-6 py-3 rounded-xl font-bold hover:bg-black transition-colors disabled:opacity-50 shadow-lg hover:shadow-xl active:scale-95 transform"
                >
                    {loading ? <Loader2 className="animate-spin" /> : 'Search'}
                </button>
            </motion.form>

            <div className="flex-1 overflow-auto space-y-4 pr-2 custom-scrollbar">
                {results.length === 0 && !loading && (
                    <div className="flex flex-col items-center justify-center text-gray-300 font-medium py-20 animate-pulse">
                        <Search size={64} className="mb-4 opacity-20" />
                        <p className="text-xl font-bold uppercase tracking-widest opacity-50">Jisho Search</p>
                    </div>
                )}

                {loading && (
                     <div className="space-y-4">
                        {[1, 2, 3].map(i => (
                            <div key={i} className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm animate-pulse flex justify-between items-center">
                                <div className="space-y-3 w-2/3">
                                    <div className="h-8 bg-gray-100 rounded w-1/3" />
                                    <div className="h-4 bg-gray-100 rounded w-full" />
                                </div>
                                <div className="w-12 h-12 bg-gray-100 rounded-xl" />
                            </div>
                        ))}
                     </div>
                )}

                <AnimatePresence>
                    {results.map((item, idx) => (
                        <motion.div
                            key={`${item.word}-${idx}`}
                            custom={idx}
                            variants={resultVariants}
                            initial="hidden"
                            animate="visible"
                            exit={{ opacity: 0, x: -20 }}
                            className="bg-white p-6 rounded-2xl border border-tatami shadow-sm flex justify-between items-center hover:border-crimson/30 hover:shadow-md transition-all group"
                        >
                            <div>
                                <div className="flex items-baseline gap-3 mb-2">
                                    <span className="text-3xl font-black text-crimson tracking-tight">{item.word}</span>
                                    <span className="text-lg text-gray-400 font-serif italic">({item.kana})</span>
                                    {item.pos && <span className="text-[10px] bg-gray-100 px-2 py-1 rounded text-gray-500 uppercase font-bold tracking-wider border border-gray-200">{item.pos}</span>}
                                </div>
                                <div className="text-gray-600 font-medium leading-relaxed">
                                    {item.meanings.join(', ')}
                                </div>
                            </div>

                            <motion.button
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.9 }}
                                onClick={() => handleAdd(item)}
                                disabled={adding === item.word}
                                className={clsx(
                                    "ml-6 p-4 rounded-xl transition-all border-2",
                                    adding === item.word ? "bg-gray-100 border-gray-200 text-gray-400" : "bg-green-50 text-green-600 border-green-100 hover:bg-green-100 hover:border-green-300 shadow-sm hover:shadow-green-200"
                                )}
                            >
                                {adding === item.word ? <Loader2 className="animate-spin" /> : <Plus strokeWidth={3} />}
                            </motion.button>
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>
        </div>
    );
};
