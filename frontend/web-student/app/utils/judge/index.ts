import { JudgeService } from "./service";

const judge = new JudgeService(import.meta.env.VITE_JUDGE_API_BASE_URL || 'http://localhost:2358')
export default judge