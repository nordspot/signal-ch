import { create } from "zustand";
import { api, type User } from "./api";

interface AuthStore {
  user: User | null;
  loading: boolean;
  setUser: (user: User | null) => void;
  login: (email: string, password: string) => Promise<void>;
  register: (data: { email: string; password: string; display_name?: string }) => Promise<void>;
  logout: () => void;
  init: () => Promise<void>;
}

export const useAuth = create<AuthStore>((set) => ({
  user: null,
  loading: true,
  setUser: (user) => set({ user }),
  login: async (email, password) => {
    const res = await api.login(email, password);
    api.setToken(res.access_token);
    set({ user: res.user });
  },
  register: async (data) => {
    const res = await api.register(data);
    api.setToken(res.access_token);
    set({ user: res.user });
  },
  logout: () => {
    api.setToken(null);
    set({ user: null });
  },
  init: async () => {
    try {
      if (api.getToken()) {
        const user = await api.getMe();
        set({ user, loading: false });
      } else {
        set({ loading: false });
      }
    } catch {
      api.setToken(null);
      set({ user: null, loading: false });
    }
  },
}));

interface ThemeStore {
  dark: boolean;
  toggle: () => void;
}

export const useTheme = create<ThemeStore>((set, get) => ({
  dark: false,
  toggle: () => {
    const next = !get().dark;
    set({ dark: next });
    if (typeof document !== "undefined") {
      document.documentElement.classList.toggle("dark", next);
    }
  },
}));
