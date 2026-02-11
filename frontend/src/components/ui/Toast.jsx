import React, { createContext, useContext, useState, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { CheckCircle, XCircle, Info, AlertTriangle, X } from 'lucide-react';
import { clsx } from 'clsx';

const ToastContext = createContext();

export const useToast = () => {
    const context = useContext(ToastContext);
    if (!context) {
        throw new Error("useToast must be used within a ToastProvider");
    }
    return context;
};

export const ToastProvider = ({ children }) => {
    const [toasts, setToasts] = useState([]);

    const addToast = (message, type = 'info', duration = 3000) => {
        const id = Date.now();
        setToasts(prev => [...prev, { id, message, type, duration }]);
    };

    const removeToast = (id) => {
        setToasts(prev => prev.filter(t => t.id !== id));
    };

    return (
        <ToastContext.Provider value={{ addToast }}>
            {children}
            <div className="fixed bottom-4 right-4 z-[9999] flex flex-col gap-2 pointer-events-none">
                <AnimatePresence mode="popLayout">
                    {toasts.map(toast => (
                        <Toast key={toast.id} {...toast} onRemove={removeToast} />
                    ))}
                </AnimatePresence>
            </div>
        </ToastContext.Provider>
    );
};

const Toast = ({ id, message, type, duration, onRemove }) => {
    useEffect(() => {
        const timer = setTimeout(() => onRemove(id), duration);
        return () => clearTimeout(timer);
    }, [id, duration, onRemove]);

    const variants = {
        hidden: { opacity: 0, x: 50, scale: 0.9 },
        visible: { opacity: 1, x: 0, scale: 1 },
        exit: { opacity: 0, scale: 0.9, x: 20, transition: { duration: 0.2 } }
    };

    const typeStyles = {
        success: { bg: 'bg-green-100', border: 'border-l-green-500', text: 'text-green-800', icon: CheckCircle },
        error: { bg: 'bg-red-100', border: 'border-l-red-500', text: 'text-red-800', icon: XCircle },
        warning: { bg: 'bg-yellow-100', border: 'border-l-yellow-500', text: 'text-yellow-800', icon: AlertTriangle },
        info: { bg: 'bg-blue-100', border: 'border-l-blue-500', text: 'text-blue-800', icon: Info },
    };

    const style = typeStyles[type] || typeStyles.info;
    const Icon = style.icon;

    return (
        <motion.div
            layout
            variants={variants}
            initial="hidden"
            animate="visible"
            exit="exit"
            className={clsx(
                "pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-xl border-l-4 shadow-lg min-w-[300px] max-w-sm backdrop-blur-md",
                style.bg,
                style.border
            )}
        >
            <Icon className={clsx("shrink-0", style.text)} size={20} />
            <p className={clsx("flex-1 text-sm font-bold", style.text)}>{message}</p>
            <button onClick={() => onRemove(id)} className={clsx("p-1 rounded-full hover:bg-black/5 transition-colors", style.text)}>
                <X size={16} />
            </button>
        </motion.div>
    );
};
