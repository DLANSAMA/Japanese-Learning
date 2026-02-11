import React, { useState, useEffect } from 'react';
import { Layout } from './components/Layout';
import { Dashboard } from './components/Dashboard';
import { StudySession } from './components/StudyCard';
import { Quiz } from './components/Quiz';
import { Map } from './components/Map';
import { Shop } from './components/Shop';
import { Dictionary } from './components/Dictionary';
import { SettingsModal } from './components/SettingsModal';

// Placeholder components to be implemented later
const Placeholder = ({ title }) => (
    <div className="flex flex-col items-center justify-center h-full text-gray-400 animate-pulse">
        <h2 className="text-4xl font-black mb-4 text-tatami">{title}</h2>
        <p>Under Construction 🚧</p>
    </div>
);

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [userStats, setUserStats] = useState(null);
  const [showSettings, setShowSettings] = useState(false);

  const fetchStats = async () => {
      try {
        const res = await fetch('/api/user');
        if (res.ok) {
            const data = await res.json();
            setUserStats(data);
        }
      } catch (err) {
        console.error("Failed to fetch stats", err);
        // Fallback for development/offline
        setUserStats({ level: 1, xp: 0, streak: 0, hearts: 5, gems: 0 });
      }
  };

  useEffect(() => {
    fetchStats();
  }, [currentView]); // Re-fetch stats when view changes (e.g. after quiz)

  const handleViewChange = (view) => {
      if (view === 'settings') {
          setShowSettings(true);
      } else {
          setCurrentView(view);
      }
  };

  const renderContent = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard
                    userStats={userStats}
                    onStartStudy={() => setCurrentView('study')}
                    onStartQuiz={() => setCurrentView('quiz')}
                />;
      case 'map':
        return <Map onStartLesson={() => setCurrentView('study')} />;
      case 'study':
        return <StudySession onComplete={() => setCurrentView('dashboard')} />;
      case 'quiz':
          return <Quiz onExit={() => setCurrentView('dashboard')} />;
      case 'shop':
        return <Shop />;
      case 'dictionary':
        return <Dictionary />;
      default:
        return <Dashboard userStats={userStats} />;
    }
  };

  return (
    <Layout currentView={currentView} onViewChange={handleViewChange}>
      {renderContent()}
      {showSettings && <SettingsModal onClose={() => setShowSettings(false)} />}
    </Layout>
  );
}

export default App;
