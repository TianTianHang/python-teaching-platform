import type { User } from "./user";

export interface Thread{
    id:number;
    courses:number;
    chapter:number;
    problem:number;
    author:User;
    title:string;
    content:string; //markdown
    replies:Reply[];
    reply_count:number;
    is_pinned:boolean; //是否置顶
    is_resolved:boolean;//是否已解决（问答场景）
    is_archived:boolean;//否归档"   
    created_at:string;
    updated_at:string;
    last_activity_at:string;
}
export interface Reply{
    id:number;
    thread:number;
    author:User;
    content:string;
    mentioned_users:User[]; //@用户
    created_at:string;
    updated_at:string;
}