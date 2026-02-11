import React, { useState, useEffect } from 'react';
import { getShopItems, buyShopItem } from '../api';
import { ShoppingBag, Loader2 } from 'lucide-react';
import { clsx } from 'clsx';

export const Shop = () => {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [buying, setBuying] = useState(null);

    useEffect(() => {
        getShopItems().then(data => {
            setItems(data);
            setLoading(false);
        }).catch(err => {
            console.error(err);
            setLoading(false);
        });
    }, []);

    const handleBuy = async (id, price) => {
        if (!confirm(`Buy for ${price} Gems?`)) return;
        setBuying(id);
        try {
            await buyShopItem(id);
            alert("Purchase Successful! 🎉");
            // Ideally trigger a global user stats refresh via callback or context
        } catch (err) {
            alert(err.response?.data?.detail || "Purchase failed");
        } finally {
            setBuying(null);
        }
    };

    if (loading) return <div className="flex justify-center items-center h-full"><Loader2 className="animate-spin text-crimson" size={48} /></div>;

    return (
        <div className="max-w-5xl mx-auto animate-in fade-in zoom-in duration-500">
            <div className="flex items-center gap-4 mb-12 border-b border-tatami pb-6">
                <div className="p-4 bg-crimson/10 rounded-full text-crimson">
                    <ShoppingBag size={40} strokeWidth={2.5} />
                </div>
                <div>
                    <h1 className="text-4xl font-black text-charcoal uppercase italic tracking-tighter">Market</h1>
                    <p className="text-gray-500 font-medium">Spend your hard-earned gems.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {items.map(item => (
                    <div key={item.id} className="bg-white p-8 rounded-3xl border border-tatami shadow-lg flex flex-col items-center text-center hover:-translate-y-2 transition-transform duration-300 relative group">
                        <div className="absolute top-4 right-4 text-xs font-bold bg-gray-100 px-2 py-1 rounded text-gray-400 uppercase tracking-widest">{item.type}</div>

                        <div className="text-8xl mb-6 transform group-hover:scale-110 transition-transform duration-300 drop-shadow-lg filter">{item.icon}</div>

                        <h3 className="text-2xl font-black text-charcoal mb-3 leading-tight">{item.name}</h3>
                        <p className="text-gray-500 mb-8 flex-1 font-medium">{item.description}</p>

                        <button
                            onClick={() => handleBuy(item.id, item.price)}
                            disabled={buying === item.id}
                            className="w-full py-4 bg-yellow-500 text-white rounded-xl font-black shadow-lg shadow-yellow-500/30 hover:bg-yellow-400 transition-all flex items-center justify-center gap-2 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {buying === item.id ? <Loader2 className="animate-spin" /> : (
                                <>
                                    <span className="text-xl">💎</span>
                                    <span className="text-xl">{item.price}</span>
                                </>
                            )}
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};
