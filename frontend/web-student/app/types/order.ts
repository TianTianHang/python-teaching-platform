import type { MembershipType, Subscription } from "./user";

export interface Order {
    id:number;
    order_number:string;
    user:string;
    membership_type:MembershipType;
    status:'pending'|'paid'|'cancelled'|'failed';
    amount:number;
    created_at:string;
    paid_at:string;
    cancelled_at:string;
    subscription:Subscription;
    transaction_id:string;
}