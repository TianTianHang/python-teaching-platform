
export interface User {
    id: number;
    avatar:string;
    username: string;
    stNumber:string; //xuehao
    email: string;
    firstName: string;
    lastName: string;
    isActive: boolean;
    isStaff: boolean;
    isSuperuser: boolean;
    dateJoined: Date;
    lastLogin?: Date; // 可能为空（从未登录过）
};

export interface Token {
    access: string;
    refresh: string;
};