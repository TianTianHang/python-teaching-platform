import http from "~/utils/http";
import type { Language, SubmissionRequest, SubmissionResponse } from "./type";

export class JudgeService{
    private baseUrl:string;
    constructor(baseUrl:string){
        this.baseUrl=baseUrl;
    }
    async getLanguage():Promise<Language[]>{
        const lang_list = await http.get<Language[]>(`${this.baseUrl}/languages`);
        return lang_list;
    }
    async submission(resquest:SubmissionRequest):Promise<SubmissionResponse>{
        const result = await http.post(`${this.baseUrl}/submissions`,resquest)
        return result;
    }
    async getResult(token:string):Promise<SubmissionResponse>{
        const result = await http.get(`${this.baseUrl}/submissions/${token}`)
        return result;
    }
}