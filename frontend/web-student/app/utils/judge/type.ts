export interface Language{
    id:number;
    name:string;
}
export interface SubmissionRequest{
    source_code:string;
    language_id:number;
    stdin?:string;
    cpu_time_limit?:number;
    memory_limit?:number;
}
export interface SubmissionResponse{
    token:string;
    status:{id:number,describe:string;};  
    status_id:number;
    stdout?:string;
    stderr?:string;
    time?:string; //second
    compile_output?:string;
    memory?:number;// MB
    created_at:string;
    finished_at?:string;
}
