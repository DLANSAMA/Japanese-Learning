import React from 'react';
import { Trophy, Star, Zap, Heart, Gem } from 'lucide-react';
import { cn } from './Layout';
import { motion } from 'framer-motion';

const colorMap = {
    yellow: "border-yellow-500 bg-yellow-50 text-yellow-600 shadow-yellow-200",
    blue: "border-blue-500 bg-blue-50 text-blue-600 shadow-blue-200",
    orange: "border-orange-500 bg-orange-50 text-orange-600 shadow-orange-200",
    red: "border-red-500 bg-red-50 text-red-600 shadow-red-200",
    purple: "border-purple-500 bg-purple-50 text-purple-600 shadow-purple-200",
};

const StatCard = ({ icon: Icon, label, value, color, delay }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: delay * 0.1, duration: 0.4 }}
    className={cn(
        "flex flex-col items-center p-4 rounded-2xl shadow-lg border-b-4 transition-all hover:-translate-y-1 hover:shadow-xl",
        colorMap[color]
    )}
  >
    <div className="p-3 rounded-full bg-white/60 mb-2 shadow-inner">
      <Icon size={24} strokeWidth={2.5} />
    </div>
    <div className="text-3xl font-black tracking-tight">{value}</div>
    <div className="text-[10px] font-bold uppercase tracking-widest opacity-80">{label}</div>
  </motion.div>
);

const SkeletonCard = () => (
    <div className="flex flex-col items-center p-4 rounded-2xl bg-gray-100 animate-pulse border-b-4 border-gray-200 h-32 justify-center">
        <div className="w-10 h-10 bg-gray-200 rounded-full mb-2"></div>
        <div className="w-16 h-8 bg-gray-200 rounded mb-1"></div>
        <div className="w-12 h-3 bg-gray-200 rounded"></div>
    </div>
);

export const Dashboard = ({ userStats, onStartStudy, onStartQuiz }) => {
  const isLoading = !userStats;

  return (
    <div className="space-y-10 pb-20">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="flex justify-between items-center"
      >
        <div>
          <h1 className="text-5xl font-black text-charcoal mb-2 uppercase italic tracking-tighter drop-shadow-sm">Dojo</h1>
          <p className="text-gray-500 font-medium text-lg">Welcome back, warrior.</p>
        </div>
        <motion.div
            whileHover={{ scale: 1.1, rotate: 10 }}
            className="w-16 h-16 bg-white rounded-full border-4 border-tatami shadow-xl flex items-center justify-center text-3xl cursor-pointer"
        >
            🥋
        </motion.div>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {isLoading ? (
            Array(5).fill(0).map((_, i) => <SkeletonCard key={i} />)
        ) : (
            <>
                <StatCard icon={Trophy} label="Level" value={userStats.level} color="yellow" delay={1} />
                <StatCard icon={Star} label="XP" value={userStats.xp} color="blue" delay={2} />
                <StatCard icon={Zap} label="Streak" value={userStats.streak} color="orange" delay={3} />
                <StatCard icon={Heart} label="Hearts" value={userStats.hearts} color="red" delay={4} />
                <StatCard icon={Gem} label="Gems" value={userStats.gems} color="purple" delay={5} />
            </>
        )}
      </div>

      {/* Main Actions */}
      <div className="grid md:grid-cols-2 gap-6">
        <motion.button
            onClick={onStartStudy}
            whileHover={{ scale: 1.02, y: -4 }}
            whileTap={{ scale: 0.98 }}
            className="group relative overflow-hidden bg-gradient-to-br from-crimson to-red-700 text-white p-8 rounded-3xl shadow-xl shadow-crimson/30 text-left border border-white/10"
        >
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-all duration-500 group-hover:scale-110 group-hover:rotate-12">
                <div className="text-9xl font-black select-none">学</div>
            </div>
            <div className="relative z-10">
                <h2 className="text-4xl font-black mb-2 italic uppercase tracking-tighter">Study</h2>
                <p className="opacity-90 font-medium text-lg text-red-100">Learn new words and grammar.</p>
                <div className="mt-8 inline-flex items-center gap-2 bg-white/20 px-4 py-2 rounded-full font-bold text-sm backdrop-blur-sm group-hover:bg-white/30 transition-colors">
                    <span>Enter Dojo</span>
                    <span>→</span>
                </div>
            </div>
        </motion.button>

        <motion.button
            onClick={onStartQuiz}
            whileHover={{ scale: 1.02, y: -4 }}
            whileTap={{ scale: 0.98 }}
            className="group relative overflow-hidden bg-gradient-to-br from-charcoal to-gray-900 text-white p-8 rounded-3xl shadow-xl shadow-gray-900/30 text-left border border-white/10"
        >
             <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-all duration-500 group-hover:scale-110 group-hover:-rotate-12">
                <div className="text-9xl font-black select-none">試</div>
            </div>
            <div className="relative z-10">
                 <h2 className="text-4xl font-black mb-2 italic uppercase tracking-tighter">Quiz</h2>
                 <p className="opacity-90 font-medium text-lg text-gray-300">Review your knowledge.</p>
                 <div className="mt-8 inline-flex items-center gap-2 bg-white/10 px-4 py-2 rounded-full font-bold text-sm backdrop-blur-sm group-hover:bg-white/20 transition-colors">
                    <span>Start Battle</span>
                    <span>⚔️</span>
                </div>
            </div>
        </motion.button>
      </div>
    </div>
  );
};
