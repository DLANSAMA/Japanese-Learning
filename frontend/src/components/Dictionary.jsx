import React, { useState } from 'react';
import { searchDictionary, addToDictionary } from '../api';
import { Search, Loader2, Plus, Check } from 'lucide-react';

export const Dictionary = () => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [adding, setAdding] = useState(null);

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;
        setLoading(true);
        try {
            const res = await searchDictionary(query);
            setResults(res);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleAdd = async (item) => {
        setAdding(item.word);
        try {
            await addToDictionary(item.word, item.kana, item.meanings);
            alert(`Added ${item.word} to study list!`);
        } catch (err) {
            alert(err.response?.data?.detail || "Failed to add word");
        } finally {
            setAdding(null);
        }
    };

    return (
        <div className="max-w-4xl mx-auto h-full flex flex-col animate-in fade-in zoom-in duration-500">
            <h1 className="text-4xl font-black text-charcoal mb-8 uppercase italic tracking-tighter">Dictionary</h1>

            <form onSubmit={handleSearch} className="relative mb-8">
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search English or Japanese..."
                    className="w-full p-4 pl-12 rounded-xl border-2 border-tatami focus:border-crimson focus:outline-none shadow-inner text-lg font-bold"
                />
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
                <button type="submit" disabled={loading} className="absolute right-2 top-1/2 -translate-y-1/2 bg-charcoal text-white px-4 py-2 rounded-lg font-bold hover:bg-black transition-colors disabled:opacity-50">
                    {loading ? <Loader2 className="animate-spin" /> : 'Search'}
                </button>
            </form>

            <div className="flex-1 overflow-auto space-y-4 pb-20 custom-scrollbar">
                {results.length === 0 && !loading && (
                    <div className="text-center text-gray-400 mt-10 font-medium">Type a word to search the Jisho.</div>
                )}

                {results.map((item, idx) => (
                    <div key={`${item.word}-${idx}`} className="bg-white p-6 rounded-xl border border-tatami shadow-sm flex justify-between items-center hover:border-crimson/30 transition-colors">
                        <div>
                            <div className="flex items-baseline gap-2 mb-1">
                                <span className="text-2xl font-black text-crimson">{item.word}</span>
                                <span className="text-gray-500 font-medium">({item.kana})</span>
                                {item.pos && <span className="text-xs bg-gray-100 px-2 py-1 rounded text-gray-500 uppercase font-bold tracking-wider">{item.pos}</span>}
                            </div>
                            <div className="text-gray-700 font-medium">
                                {item.meanings.join(', ')}
                            </div>
                        </div>

                        <button
                            onClick={() => handleAdd(item)}
                            disabled={adding === item.word}
                            className="ml-4 p-3 bg-green-50 text-green-600 rounded-xl hover:bg-green-100 transition-colors border border-green-200"
                        >
                            {adding === item.word ? <Loader2 className="animate-spin" /> : <Plus />}
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};
