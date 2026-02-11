import React from 'react';
import { LayoutDashboard, Map as MapIcon, BookOpen, ShoppingBag, Settings, Menu, Search } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { motion, AnimatePresence } from 'framer-motion';

export const cn = (...inputs) => twMerge(clsx(inputs));

const NavItem = ({ id, icon: Icon, label, active, onClick, mobile }) => (
  <button
    onClick={onClick}
    className={cn(
      "relative flex items-center gap-3 p-3 rounded-xl transition-all cursor-pointer overflow-hidden group",
      active ? "text-white shadow-lg shadow-crimson/30" : "text-gray-600 hover:bg-gray-200",
      mobile ? "flex-col gap-1 text-xs justify-center p-2 flex-1" : "w-full text-left"
    )}
  >
    {active && (
        <motion.div
            layoutId={mobile ? "activeNavMobile" : "activeNavDesktop"}
            className="absolute inset-0 bg-crimson"
            initial={false}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
        />
    )}
    <div className="relative z-10 flex items-center justify-center md:justify-start gap-3 w-full">
        <Icon size={mobile ? 24 : 20} strokeWidth={active ? 2.5 : 2} className={cn("transition-transform group-hover:scale-110", active && "scale-110")} />
        <span className={mobile ? "text-[10px] font-bold" : "font-bold"}>{label}</span>
    </div>
  </button>
);

export const Layout = ({ currentView, onViewChange, children }) => {
  const navItems = [
    { id: 'dashboard', label: 'Home', icon: LayoutDashboard },
    { id: 'map', label: 'Map', icon: MapIcon },
    { id: 'study', label: 'Study', icon: BookOpen },
    { id: 'dictionary', label: 'Search', icon: Search },
    { id: 'shop', label: 'Shop', icon: ShoppingBag },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  // Mobile Bottom Nav: Slice to first 5 items, assume Settings is handled separately or in menu?
  // Actually, let's keep it simple and just show all 6. Might be crowded on mobile.
  // Re-ordering for mobile to prioritize key actions.
  const mobileNavItems = navItems.filter(i => i.id !== 'settings');

  return (
    <div className="flex h-screen bg-paper overflow-hidden font-sans text-charcoal selection:bg-crimson/30">
      {/* Desktop Sidebar */}
      <aside className="hidden md:flex flex-col w-64 bg-white/80 backdrop-blur-md border-r border-tatami p-6 relative z-50 shadow-sm">
        <div className="flex items-center gap-3 mb-10 pl-2">
            <div className="w-10 h-10 bg-crimson rounded-full flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-crimson/40">
                K
            </div>
            <div>
                <h1 className="text-2xl font-black text-crimson uppercase italic tracking-tighter leading-none">Kizuna</h1>
                <p className="text-xs text-gray-400 font-bold uppercase tracking-widest leading-none mt-1">Dojo v12.0</p>
            </div>
        </div>

        <nav className="flex-1 space-y-2">
          {navItems.map((item) => (
            <NavItem
              key={item.id}
              {...item}
              active={currentView === item.id}
              onClick={() => onViewChange(item.id)}
            />
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto relative custom-scrollbar bg-paper">
        <div className="md:p-8 p-4 pb-24 md:pb-8 max-w-7xl mx-auto min-h-full">
            <AnimatePresence mode="wait">
                <motion.div
                    key={currentView}
                    initial={{ opacity: 0, y: 10, scale: 0.98 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -10, scale: 0.98 }}
                    transition={{ duration: 0.3, ease: "easeOut" }}
                    className="h-full"
                >
                    {children}
                </motion.div>
            </AnimatePresence>
        </div>
      </main>

      {/* Mobile Bottom Nav */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white/95 backdrop-blur-lg border-t border-tatami p-2 flex justify-between z-50 pb-safe shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
        {navItems.map((item) => (
            <NavItem
              key={item.id}
              {...item}
              active={currentView === item.id}
              onClick={() => onViewChange(item.id)}
              mobile
            />
        ))}
      </div>
    </div>
  );
};
