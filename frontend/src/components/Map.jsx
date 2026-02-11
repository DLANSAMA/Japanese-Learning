import React, { useState, useEffect } from 'react';
import { getCurriculum } from '../api';
import { clsx } from 'clsx';
import { Lock, BookOpen, Sword, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';

const getColorClass = (color, type) => {
    const map = {
        red: { text: 'text-red-600', bg: 'bg-red-100', border: 'border-red-500', softBorder: 'border-red-200' },
        blue: { text: 'text-blue-600', bg: 'bg-blue-100', border: 'border-blue-500', softBorder: 'border-blue-200' },
        green: { text: 'text-green-600', bg: 'bg-green-100', border: 'border-green-500', softBorder: 'border-green-200' },
        purple: { text: 'text-purple-600', bg: 'bg-purple-100', border: 'border-purple-500', softBorder: 'border-purple-200' },
        yellow: { text: 'text-yellow-600', bg: 'bg-yellow-100', border: 'border-yellow-500', softBorder: 'border-yellow-200' },
    };
    return map[color]?.[type] || map['red'][type];
};

export const Map = ({ onStartLesson }) => {
    const [curriculum, setCurriculum] = useState(null);

    useEffect(() => {
        getCurriculum().then(setCurriculum);
    }, []);

    if (!curriculum) return <div className="flex justify-center items-center h-full"><Loader2 className="animate-spin text-crimson" size={48} /></div>;

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: {
                staggerChildren: 0.2
            }
        }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 50 },
        visible: { opacity: 1, y: 0 }
    };

    return (
        <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="relative max-w-lg mx-auto pb-20 pt-10"
        >
            {/* Spine */}
            <motion.div
                initial={{ height: 0 }}
                animate={{ height: '100%' }}
                transition={{ duration: 1.5, ease: "easeInOut" }}
                className="absolute left-1/2 top-0 bottom-0 w-4 bg-tatami -translate-x-1/2 rounded-full"
            />

            {curriculum.units.map((unit, uIdx) => (
                <div key={unit.title} className="relative z-10 mb-20">
                     <motion.div
                        variants={itemVariants}
                        className={clsx(
                             "bg-white p-6 rounded-2xl border-l-8 shadow-lg mb-12 relative mx-4 hover:scale-[1.02] transition-transform",
                             getColorClass(unit.color, 'border')
                        )}
                     >
                        <h3 className={clsx("text-2xl font-black uppercase italic", getColorClass(unit.color, 'text'))}>{unit.title}</h3>
                        <p className="text-gray-500 font-medium">{unit.description}</p>
                     </motion.div>

                     <div className="space-y-16">
                        {unit.lessons.map((lesson, lIdx) => {
                            const isLocked = uIdx > 0;
                            const isBoss = lesson.type === 'boss';
                            const color = unit.color;

                            return (
                                <motion.div
                                    variants={itemVariants}
                                    key={lesson.id}
                                    className="flex flex-col items-center relative group"
                                >
                                    <motion.button
                                        whileHover={!isLocked ? { scale: 1.1, rotate: 0 } : {}}
                                        whileTap={!isLocked ? { scale: 0.95 } : {}}
                                        onClick={() => !isLocked && onStartLesson(lesson.id)}
                                        className={clsx(
                                            "w-24 h-24 rotate-45 rounded-3xl border-[6px] flex items-center justify-center shadow-xl transition-colors z-20",
                                            isLocked ? "bg-gray-100 border-gray-200 text-gray-300 cursor-not-allowed" :
                                            `${getColorClass(color, 'bg')} ${getColorClass(color, 'border')} ${getColorClass(color, 'text')} cursor-pointer hover:shadow-${color}-500/50`
                                        )}
                                    >
                                        <div className="-rotate-45">
                                            {isLocked ? <Lock size={32} /> :
                                             isBoss ? <Sword size={36} strokeWidth={2.5} /> : <BookOpen size={32} strokeWidth={2.5} />}
                                        </div>
                                    </motion.button>

                                    <div className={clsx(
                                        "mt-8 bg-white px-6 py-2 rounded-full border-2 shadow-sm font-bold text-sm tracking-wide uppercase transition-all group-hover:-translate-y-1",
                                        isLocked ? "text-gray-300 border-gray-100" : `${getColorClass(color, 'text')} ${getColorClass(color, 'softBorder')}`
                                    )}>
                                        {lesson.title}
                                    </div>
                                </motion.div>
                            );
                        })}
                     </div>
                </div>
            ))}
        </motion.div>
    );
};
