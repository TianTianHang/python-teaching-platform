// app/utils/redirect.ts
import { redirect } from "react-router";


// 从环境变量或构建时注入部署前缀
const DEPLOY_PREFIX = process.env.DEPLOY_PREFIX || "";

export function safeRedirect(
  url: string,
  init?: number | ResponseInit
){
  // 如果 url 是内部路径（以 / 开头但不是 // 或 http）
  if (url.startsWith("/") && !url.startsWith("//") && !url.startsWith("/http")) {
    const cleanPrefix = DEPLOY_PREFIX.replace(/\/$/, "");
    const cleanUrl = url.replace(/^\/+/, "");
    url = `${cleanPrefix}/${cleanUrl}`;
  }
  return redirect(url, init);
}