import { create } from "zustand";

interface GlobalState{
    error:{title:string;message:string;}|null;
    setError:(error:{title:string;message:string;})=>void;
}

export const useGolbalStore =create<GlobalState>()((set, get) => ({
        error:null,
        setError:(error)=>{
            set({error:error});
        }
}))

