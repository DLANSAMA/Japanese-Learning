import React from 'react';
import { Trophy, Star, Zap, Heart, Gem } from 'lucide-react';
import { cn } from './Layout'; // reuse cn

const colorMap = {
    yellow: "border-yellow-500 bg-yellow-100 text-yellow-600",
    blue: "border-blue-500 bg-blue-100 text-blue-600",
    orange: "border-orange-500 bg-orange-100 text-orange-600",
    red: "border-red-500 bg-red-100 text-red-600",
    purple: "border-purple-500 bg-purple-100 text-purple-600",
};

const StatCard = ({ icon: Icon, label, value, color }) => (
  <div className={cn("flex flex-col items-center bg-white p-4 rounded-xl shadow-md border-b-4 transition-transform hover:-translate-y-1", colorMap[color])}>
    <div className="p-2 rounded-full bg-white/50 mb-2">
      <Icon size={24} />
    </div>
    <div className="text-2xl font-black text-gray-800">{value}</div>
    <div className="text-xs text-gray-600 font-bold uppercase">{label}</div>
  </div>
);

export const Dashboard = ({ userStats, onStartStudy, onStartQuiz }) => {
  if (!userStats) return <div className="p-8 text-center animate-pulse text-gray-400 font-bold">Loading Dojo...</div>;

  return (
    <div className="space-y-8 animate-in fade-in zoom-in duration-500">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-black text-charcoal mb-2 uppercase italic tracking-tighter">Dojo</h1>
          <p className="text-gray-500 font-medium">Welcome back, warrior.</p>
        </div>
        <div className="flex gap-4">
             <div className="w-12 h-12 bg-gray-200 rounded-full border-2 border-white shadow-lg flex items-center justify-center text-2xl">
                🥋
             </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <StatCard icon={Trophy} label="Level" value={userStats.level} color="yellow" />
        <StatCard icon={Star} label="XP" value={userStats.xp} color="blue" />
        <StatCard icon={Zap} label="Streak" value={userStats.streak} color="orange" />
        <StatCard icon={Heart} label="Hearts" value={userStats.hearts} color="red" />
        <StatCard icon={Gem} label="Gems" value={userStats.gems} color="purple" />
      </div>

      {/* Main Actions */}
      <div className="grid md:grid-cols-2 gap-6">
        <button
            onClick={onStartStudy}
            className="group relative overflow-hidden bg-crimson text-white p-8 rounded-2xl shadow-xl shadow-crimson/20 hover:scale-[1.02] transition-transform text-left"
        >
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                <div className="text-9xl font-black">学</div>
            </div>
            <h2 className="text-3xl font-black mb-2 italic uppercase">Study</h2>
            <p className="opacity-90 font-medium">Learn new words and grammar.</p>
        </button>

        <button
            onClick={onStartQuiz}
            className="group relative overflow-hidden bg-charcoal text-white p-8 rounded-2xl shadow-xl hover:scale-[1.02] transition-transform text-left"
        >
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                <div className="text-9xl font-black">試</div>
            </div>
             <h2 className="text-3xl font-black mb-2 italic uppercase">Quiz</h2>
             <p className="opacity-90 font-medium">Review your knowledge.</p>
        </button>
      </div>
    </div>
  );
};
