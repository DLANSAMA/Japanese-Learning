import React, { useState, useEffect } from 'react';
import { getSettings, updateSettings } from '../api';
import { X, Save, Loader2 } from 'lucide-react';

export const SettingsModal = ({ onClose }) => {
    const [settings, setSettings] = useState({ track: 'General', theme: 'default' });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

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
            alert("Settings Saved!");
            onClose();
        } catch (err) {
            alert("Failed to save settings");
        } finally {
            setSaving(false);
        }
    };

    if (loading) return <div className="flex justify-center items-center h-full"><Loader2 className="animate-spin text-crimson" size={32} /></div>;

    return (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 backdrop-blur-sm animate-in fade-in duration-300">
            <div className="bg-white w-full max-w-md rounded-3xl p-8 shadow-2xl relative animate-in zoom-in-95 duration-300">
                <button onClick={onClose} className="absolute top-4 right-4 p-2 hover:bg-gray-100 rounded-full transition-colors text-gray-400 hover:text-charcoal">
                    <X />
                </button>

                <h2 className="text-3xl font-black text-charcoal mb-8 uppercase italic tracking-tighter">Settings</h2>

                <div className="space-y-8">
                    <div>
                        <label className="block text-sm font-bold text-gray-500 uppercase tracking-wider mb-3">Learning Track</label>
                        <div className="relative">
                            <select
                                value={settings.track}
                                onChange={(e) => setSettings({...settings, track: e.target.value})}
                                className="w-full p-4 rounded-xl border-2 border-tatami bg-paper font-bold text-lg focus:border-crimson outline-none appearance-none cursor-pointer hover:border-crimson/50 transition-colors"
                            >
                                <option value="General">General (Standard)</option>
                                <option value="Anime">Anime (Pop Culture)</option>
                                <option value="Business">Business (Formal)</option>
                                <option value="Travel">Travel (Survival)</option>
                            </select>
                            <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">▼</div>
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-bold text-gray-500 uppercase tracking-wider mb-3">Theme</label>
                        <div className="relative">
                            <select
                                value={settings.theme}
                                onChange={(e) => setSettings({...settings, theme: e.target.value})}
                                className="w-full p-4 rounded-xl border-2 border-tatami bg-paper font-bold text-lg focus:border-crimson outline-none appearance-none cursor-pointer hover:border-crimson/50 transition-colors"
                            >
                                <option value="default">Kizuna (Default)</option>
                                <option value="dark">Dark Mode</option>
                                <option value="cyberpunk">Cyberpunk</option>
                                <option value="edo">Edo Period</option>
                            </select>
                            <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">▼</div>
                        </div>
                    </div>

                    <button
                        onClick={handleSave}
                        disabled={saving}
                        className="w-full py-4 bg-crimson text-white rounded-xl font-bold shadow-lg shadow-crimson/30 hover:scale-[1.02] transition-transform flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {saving ? <Loader2 className="animate-spin" /> : <Save size={20} />}
                        <span>Save Changes</span>
                    </button>
                </div>
            </div>
        </div>
    );
};
