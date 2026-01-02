'use client';

import { useEffect } from 'react';
import { useToastStore } from '@/stores/toast';
import type { ToastProps } from '@/lib/types';

const TOAST_STYLES = {
  success: 'bg-emerald-500 text-white border-emerald-600',
  error: 'bg-red-500 text-white border-red-600',
  info: 'bg-blue-500 text-white border-blue-600',
};

const ICONS = {
  success: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
    </svg>
  ),
  error: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
    </svg>
  ),
  info: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
};

function ToastItem({ toast, onRemove }: { toast: ToastProps; onRemove: (id: string) => void }) {
  useEffect(() => {
    // Auto-dismiss on duration
    if (toast.duration && toast.duration > 0) {
      const timer = setTimeout(() => onRemove(toast.id), toast.duration);
      return () => clearTimeout(timer);
    }
  }, [toast.id, toast.duration, onRemove]);

  return (
    <div
      className={`${TOAST_STYLES[toast.type]} flex items-center gap-3 px-4 py-3 rounded-lg border shadow-lg animate-slide-in`}
      role="alert"
    >
      <div className="flex-shrink-0">{ICONS[toast.type]}</div>
      <p className="flex-1 text-sm font-medium">{toast.message}</p>
      <button
        onClick={() => onRemove(toast.id)}
        className="flex-shrink-0 p-1 hover:bg-white/20 rounded transition-colors"
        aria-label="Close"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
}

export function ToastContainer() {
  const { toasts, removeToast } = useToastStore();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onRemove={removeToast} />
      ))}
    </div>
  );
}

// Convenience hook for components
export function useToast() {
  return {
    success: (message: string, duration?: number) => useToastStore.getState().addToast({ type: 'success', message, duration }),
    error: (message: string, duration?: number) => useToastStore.getState().addToast({ type: 'error', message, duration }),
    info: (message: string, duration?: number) => useToastStore.getState().addToast({ type: 'info', message, duration }),
  };
}
