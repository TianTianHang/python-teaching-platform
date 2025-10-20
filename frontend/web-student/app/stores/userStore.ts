import { create } from 'zustand';
import type { Token, User } from '~/types/user';
import http from '~/utils/http';
interface UserState {
    user?: User|null;
    token: Token|null;
    login: ({ username, password }: { username: string, password: string }) => void;

}
const useUserStore = create<UserState>()((set) => ({
    user: null,
    token:null,
    login:async ({ username, password })=>{
        const token = await http.post<Token>("login",{username,password})
        const user = await http
    }
}));