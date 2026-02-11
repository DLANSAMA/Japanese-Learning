import React from 'react';
import { LayoutDashboard, Map as MapIcon, BookOpen, ShoppingBag, Settings, Menu, Search } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export const cn = (...inputs) => twMerge(clsx(inputs));

const NavItem = ({ icon: Icon, label, active, onClick, mobile }) => (
  <button
    onClick={onClick}
    className={cn(
      "flex items-center gap-3 p-3 rounded-xl transition-all cursor-pointer",
      active ? "bg-crimson text-white shadow-lg shadow-crimson/30" : "text-gray-600 hover:bg-gray-200",
      mobile ? "flex-col gap-1 text-xs justify-center p-2" : "w-full text-left"
    )}
  >
    <Icon size={mobile ? 24 : 20} strokeWidth={active ? 2.5 : 2} />
    <span className={mobile ? "text-[10px] font-bold" : "font-bold"}>{label}</span>
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

  return (
    <div className="flex h-screen bg-paper overflow-hidden font-sans text-charcoal">
      {/* Desktop Sidebar */}
      <aside className="hidden md:flex w-64 flex-col bg-white/50 backdrop-blur-md border-r border-tatami p-6 relative">
        <div className="flex items-center gap-3 mb-10">
            <div className="w-10 h-10 bg-crimson rounded-full flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-crimson/40">
                K
            </div>
            <h1 className="text-2xl font-black text-crimson uppercase italic tracking-tighter">Kizuna</h1>
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
      <main className="flex-1 overflow-auto relative">
        <div className="md:p-8 p-4 pb-24 md:pb-8 max-w-7xl mx-auto h-full">
            {children}
        </div>
      </main>

      {/* Mobile Bottom Nav */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white/90 backdrop-blur-lg border-t border-tatami p-2 flex justify-around z-50 pb-safe">
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
