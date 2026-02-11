import React, { useState, useEffect } from 'react';
import { getCurriculum } from '../api';
import { clsx } from 'clsx';
import { Lock, BookOpen, Sword } from 'lucide-react';

const getColorClass = (color, type) => {
    const map = {
        red: { text: 'text-red-600', bg: 'bg-red-100', border: 'border-red-500', softBorder: 'border-red-200' },
        blue: { text: 'text-blue-600', bg: 'bg-blue-100', border: 'border-blue-500', softBorder: 'border-blue-200' },
        green: { text: 'text-green-600', bg: 'bg-green-100', border: 'border-green-500', softBorder: 'border-green-200' },
        purple: { text: 'text-purple-600', bg: 'bg-purple-100', border: 'border-purple-500', softBorder: 'border-purple-200' },
        yellow: { text: 'text-yellow-600', bg: 'bg-yellow-100', border: 'border-yellow-500', softBorder: 'border-yellow-200' },
    };
    // Fallback to red
    return map[color]?.[type] || map['red'][type];
};

export const Map = ({ onStartLesson }) => {
    const [curriculum, setCurriculum] = useState(null);

    useEffect(() => {
        getCurriculum().then(setCurriculum);
    }, []);

    if (!curriculum) return <div className="text-center p-10 animate-pulse text-gray-400 font-bold">Unfolding the Scroll...</div>;

    return (
        <div className="relative max-w-lg mx-auto pb-20 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {/* Spine */}
            <div className="absolute left-1/2 top-0 bottom-0 w-4 bg-tatami -translate-x-1/2 rounded-full" />

            {curriculum.units.map((unit, uIdx) => (
                <div key={unit.title} className="relative z-10 mb-12">
                     <div className={clsx(
                         "bg-white p-6 rounded-2xl border-l-8 shadow-lg mb-12 relative mx-4",
                         getColorClass(unit.color, 'border')
                     )}>
                        <h3 className={clsx("text-2xl font-black uppercase italic", getColorClass(unit.color, 'text'))}>{unit.title}</h3>
                        <p className="text-gray-500 font-medium">{unit.description}</p>
                     </div>

                     <div className="space-y-16">
                        {unit.lessons.map((lesson, lIdx) => {
                            const isLocked = uIdx > 0; // Logic for locking based on index
                            const isBoss = lesson.type === 'boss';
                            const color = unit.color;

                            return (
                                <div key={lesson.id} className="flex flex-col items-center relative group">
                                    <button
                                        onClick={() => !isLocked && onStartLesson(lesson.id)}
                                        className={clsx(
                                            "w-24 h-24 rotate-45 rounded-2xl border-4 flex items-center justify-center shadow-xl transition-all transform hover:rotate-0 hover:scale-110",
                                            isLocked ? "bg-gray-200 border-gray-300 text-gray-400 cursor-not-allowed" :
                                            `${getColorClass(color, 'bg')} ${getColorClass(color, 'border')} ${getColorClass(color, 'text')} cursor-pointer`
                                        )}
                                    >
                                        <div className="-rotate-45 group-hover:rotate-0 transition-transform">
                                            {isLocked ? <Lock size={32} /> :
                                             isBoss ? <Sword size={32} strokeWidth={2.5} /> : <BookOpen size={32} strokeWidth={2.5} />}
                                        </div>
                                    </button>

                                    <div className={clsx(
                                        "mt-8 bg-white px-6 py-2 rounded-full border-2 shadow-sm font-bold text-sm tracking-wide uppercase",
                                        isLocked ? "text-gray-400 border-gray-200" : `${getColorClass(color, 'text')} ${getColorClass(color, 'softBorder')}`
                                    )}>
                                        {lesson.title}
                                    </div>
                                </div>
                            );
                        })}
                     </div>
                </div>
            ))}
        </div>
    );
};
