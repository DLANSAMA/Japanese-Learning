import React, { useState, useEffect } from 'react';
import { getShopItems, buyShopItem } from '../api';
import { ShoppingBag, Loader2, Check } from 'lucide-react';
import { clsx } from 'clsx';
import { motion, AnimatePresence } from 'framer-motion';
import { useToast } from './ui/Toast';
import confetti from 'canvas-confetti';

export const Shop = () => {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [buying, setBuying] = useState(null);
    const { addToast } = useToast();

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
            addToast("Purchase Successful! 🎉", 'success');
            confetti({
                particleCount: 80,
                spread: 60,
                origin: { y: 0.7 },
                colors: ['#FFD700', '#FFA500']
            });
            // Update UI state to reflect ownership (optimistic or re-fetch)
            setItems(prev => prev.map(i => i.id === id ? { ...i, owned: true } : i));
        } catch (err) {
            addToast(err.response?.data?.detail || "Purchase failed", 'error');
        } finally {
            setBuying(null);
        }
    };

    if (loading) return <div className="flex justify-center items-center h-full"><Loader2 className="animate-spin text-crimson" size={48} /></div>;

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: { staggerChildren: 0.1 }
        }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 20 },
        visible: { opacity: 1, y: 0 }
    };

    return (
        <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="max-w-6xl mx-auto pb-20"
        >
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-6 mb-16 border-b border-tatami pb-8"
            >
                <div className="p-5 bg-gradient-to-br from-crimson to-red-600 rounded-3xl text-white shadow-lg shadow-crimson/30 rotate-3 hover:rotate-6 transition-transform">
                    <ShoppingBag size={48} strokeWidth={2} />
                </div>
                <div>
                    <h1 className="text-5xl font-black text-charcoal uppercase italic tracking-tighter drop-shadow-sm">Market</h1>
                    <p className="text-gray-500 font-medium text-lg mt-2">Upgrade your experience.</p>
                </div>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {items.map(item => (
                    <motion.div
                        variants={itemVariants}
                        key={item.id}
                        className="bg-white p-8 rounded-[2rem] border border-tatami shadow-lg flex flex-col items-center text-center hover:-translate-y-2 hover:shadow-xl transition-all duration-300 relative group overflow-hidden"
                    >
                        <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-transparent via-crimson to-transparent opacity-0 group-hover:opacity-50 transition-opacity" />

                        <div className="absolute top-6 right-6 text-[10px] font-bold bg-gray-100 px-3 py-1 rounded-full text-gray-400 uppercase tracking-widest border border-gray-200">{item.type}</div>

                        <div className="text-8xl mb-8 transform group-hover:scale-110 transition-transform duration-500 drop-shadow-2xl filter mt-4">{item.icon}</div>

                        <h3 className="text-3xl font-black text-charcoal mb-4 leading-tight tracking-tight">{item.name}</h3>
                        <p className="text-gray-500 mb-10 flex-1 font-medium leading-relaxed px-4">{item.description}</p>

                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => handleBuy(item.id, item.price)}
                            disabled={buying === item.id || item.owned} // Assuming API returns owned status, else handle locally
                            className={clsx(
                                "w-full py-5 rounded-2xl font-black shadow-lg flex items-center justify-center gap-3 transition-all",
                                item.owned ? "bg-gray-100 text-gray-400 cursor-default shadow-none border-2 border-gray-200" :
                                "bg-gradient-to-br from-yellow-400 to-yellow-500 text-white shadow-yellow-500/30 hover:shadow-yellow-500/50"
                            )}
                        >
                            {buying === item.id ? <Loader2 className="animate-spin" /> : item.owned ? (
                                <>
                                    <Check size={24} />
                                    <span className="text-lg">Owned</span>
                                </>
                            ) : (
                                <>
                                    <span className="text-2xl">💎</span>
                                    <span className="text-xl">{item.price}</span>
                                </>
                            )}
                        </motion.button>
                    </motion.div>
                ))}
            </div>
        </motion.div>
    );
};
