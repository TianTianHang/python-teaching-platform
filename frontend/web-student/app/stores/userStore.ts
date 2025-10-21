import { create } from 'zustand';
import type { Token, User } from '~/types/user';
import http from '~/utils/http';
interface UserState {
    isAuthenticated: boolean;
    user?: User | null;
    token: Token | null;
    login: ({ username, password }: { username: string, password: string }) => void;
    register: ({ username, password }: { username: string, password: string }) => void;
    setUser: (userData: User) => void;
    setToken: (token: Token) => void;
}
export const useUserStore = create<UserState>()((set, get) => ({
    isAuthenticated: false,
    user: null,
    token: null,
    login: async ({ username, password }) => {
        const token = await http.post<Token>("auth/login", { username, password },{skipNotification:true})
        localStorage.setItem("accessToken", token.access);
        localStorage.setItem("refreshToken", token.refresh);
        const user = await http.get<User>("auth/me")
        set({
            isAuthenticated: true,
            user: user,
            token: token
        })
    },
    register: async ({ username, password }) => {
        const { user, access, refresh } = await http.post<{
            user: User,
            access: string,
            refresh: string
        }>("auth/register", { username, password },{skipNotification:true})
        localStorage.setItem("accessToken", access);
        localStorage.setItem("refreshToken", refresh);
        set({ user: user, token: { refresh: refresh, access: access } })
    },
    logout: async () => {
        const currentToken = get().token; // 获取当前的 token
        if (currentToken && currentToken.refresh) {
            await http.post<Token>("auth/logout", { refresh: currentToken.refresh },{skipNotification:true});
        }
        localStorage.removeItem("accessToken");
        localStorage.removeItem("refreshToken");
        set({
            isAuthenticated: false,
            user: null,
            token: null,
        });
    },
    setUser: (userData: User) => {
        set({ user: userData });
    },
    setToken: (token: Token) => {
        set({ token: token });
    },
}));