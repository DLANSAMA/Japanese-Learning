import React, { createContext, useContext, useState, useEffect } from 'react';
import { getSettings, updateSettings as apiUpdateSettings } from '../api';

const SettingsContext = createContext();

export const useSettings = () => {
    const context = useContext(SettingsContext);
    if (!context) {
        throw new Error('useSettings must be used within a SettingsProvider');
    }
    return context;
};

export const SettingsProvider = ({ children }) => {
    const [settings, setSettings] = useState({
        track: 'General',
        theme: 'default',
        displayMode: 'kanji',
        showRomaji: true
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getSettings().then(data => {
            setSettings({
                track: data.track,
                theme: data.theme,
                displayMode: data.display_mode || 'kanji',
                showRomaji: data.show_romaji !== undefined ? data.show_romaji : true
            });
            setLoading(false);
        }).catch(err => {
            console.error("Failed to load settings", err);
            setLoading(false);
        });
    }, []);

    useEffect(() => {
        const themes = ['default', 'dark', 'cyberpunk', 'edo'];
        document.documentElement.classList.remove(...themes);

        if (settings.theme && settings.theme !== 'default') {
            document.documentElement.classList.add(settings.theme);
        }
    }, [settings.theme]);

    const updateSettings = async (newSettings) => {
        const updated = { ...settings, ...newSettings };
        setSettings(updated);

        try {
            await apiUpdateSettings(
                updated.track,
                updated.theme,
                updated.displayMode,
                updated.showRomaji
            );
        } catch (err) {
            console.error("Failed to save settings", err);
            // Optionally revert here
        }
    };

    return (
        <SettingsContext.Provider value={{ settings, updateSettings, loading }}>
            {children}
        </SettingsContext.Provider>
    );
};
