import { create } from 'zustand';

interface AppState {
  activeThread: string | null;
  setActiveThread: (id: string | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
  activeThread: null,
  setActiveThread: (id) => set({ activeThread: id }),
}));

export default useAppStore;
