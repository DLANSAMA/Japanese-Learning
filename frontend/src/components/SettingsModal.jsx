import React, { useState, useEffect } from 'react';
import { getSettings, updateSettings } from '../api';
import { X, Save, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useToast } from './ui/Toast';

export const SettingsModal = ({ onClose }) => {
    const [settings, setSettings] = useState({ track: 'General', theme: 'default' });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const { addToast } = useToast();

    useEffect(() => {
        getSettings().then(data => {
            setSettings(data);
            setLoading(false);
        }).catch(err => {
            console.error("Failed to load settings", err);
            setLoading(false);
        });
    }, []);

    const handleSave = async () => {
        setSaving(true);
        try {
            await updateSettings(settings.track, settings.theme);
            addToast("Settings Saved!", 'success');
            onClose();
        } catch (err) {
            addToast("Failed to save settings", 'error');
        } finally {
            setSaving(false);
        }
    };

    if (loading) return null;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/60 z-[100] flex items-center justify-center p-4 backdrop-blur-md"
            >
                <motion.div
                    initial={{ scale: 0.9, y: 20 }}
                    animate={{ scale: 1, y: 0 }}
                    exit={{ scale: 0.9, y: 20 }}
                    className="bg-white w-full max-w-lg rounded-[2rem] p-10 shadow-2xl relative border-4 border-tatami"
                >
                    <button
                        onClick={onClose}
                        className="absolute top-6 right-6 p-2 bg-gray-100 rounded-full hover:bg-crimson hover:text-white transition-all shadow-sm"
                    >
                        <X size={20} strokeWidth={2.5} />
                    </button>

                    <h2 className="text-4xl font-black text-charcoal mb-10 uppercase italic tracking-tighter drop-shadow-sm">Settings</h2>

                    <div className="space-y-8">
                        <div>
                            <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-3">Learning Track</label>
                            <div className="relative group">
                                <select
                                    value={settings.track}
                                    onChange={(e) => setSettings({...settings, track: e.target.value})}
                                    className="w-full p-5 rounded-2xl border-2 border-tatami bg-paper font-bold text-xl focus:border-crimson outline-none appearance-none cursor-pointer hover:border-crimson/50 transition-colors shadow-inner"
                                >
                                    <option value="General">General (Standard)</option>
                                    <option value="Anime">Anime (Pop Culture)</option>
                                    <option value="Business">Business (Formal)</option>
                                    <option value="Travel">Travel (Survival)</option>
                                </select>
                                <div className="absolute right-6 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400 group-hover:text-crimson transition-colors text-xs font-bold">▼</div>
                            </div>
                        </div>

                        <div>
                            <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-3">Theme</label>
                            <div className="relative group">
                                <select
                                    value={settings.theme}
                                    onChange={(e) => setSettings({...settings, theme: e.target.value})}
                                    className="w-full p-5 rounded-2xl border-2 border-tatami bg-paper font-bold text-xl focus:border-crimson outline-none appearance-none cursor-pointer hover:border-crimson/50 transition-colors shadow-inner"
                                >
                                    <option value="default">Kizuna (Default)</option>
                                    <option value="dark">Dark Mode</option>
                                    <option value="cyberpunk">Cyberpunk</option>
                                    <option value="edo">Edo Period</option>
                                </select>
                                <div className="absolute right-6 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400 group-hover:text-crimson transition-colors text-xs font-bold">▼</div>
                            </div>
                        </div>

                        <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={handleSave}
                            disabled={saving}
                            className="w-full py-5 bg-crimson text-white rounded-2xl font-black text-xl shadow-xl shadow-crimson/30 hover:bg-red-700 transition-all flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed mt-4"
                        >
                            {saving ? <Loader2 className="animate-spin" /> : <Save size={24} strokeWidth={2.5} />}
                            <span>Save Changes</span>
                        </motion.button>
                    </div>
                </motion.div>
            </motion.div>
        </AnimatePresence>
    );
};
