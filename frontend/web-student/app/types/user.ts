
export interface User {
    id: number;
    avatar: string;
    username: string;
    stNumber: string; //xuehao
    email: string;
    firstName: string;
    lastName: string;
    isActive: boolean;
    isStaff: boolean;
    isSuperuser: boolean;
    dateJoined: Date;
    lastLogin?: Date; // 可能为空（从未登录过）
    current_subscription:Subscription;
    has_active_subscription:boolean;
};

export interface Token {
    access: string;
    refresh: string;
};

export interface Subscription {
    id: number;
    membership_type: MembershipType;
    start_date: string;
    end_date: string;
    is_active:boolean;
}
export interface MembershipType {
    id: number;
    name: string;
    description: string;
    price: number;
    duration_days: number;
}