import { withAuth } from "~/utils/loaderWrapper"
import type { Route } from "./+types/upload.$type.$"
import { fileServices } from "~/localstorage.server";
import { data } from "react-router";



export const loader = withAuth(async ({params, request}:Route.LoaderArgs)=>{
   
  const type = params.type;
  const keyWithExt=params["*"];

  if (!type || !keyWithExt) {
    throw data("Bad request", { status: 400 });
  }

  // 分离 key 和扩展名（如 "user123.jpg" → key="user123", ext=".jpg"）
  const lastDotIndex = keyWithExt.lastIndexOf(".");
  if (lastDotIndex === -1) {
    throw data("Missing file extension", { status: 400 });
  }

  const key = keyWithExt.substring(0, lastDotIndex);
  const ext = keyWithExt.substring(lastDotIndex); // 包含 "."

  // 根据 type 获取对应的 FileService 实例
  const service = fileServices().get(type);
  if (!service) {
    throw data("Invalid file type", { status: 404 });
  }

  // 获取文件元数据和内容
  const { buffer, mimeType, etag } = await service.getFileMetadata(key, ext);

  // 检查 ETag 缓存（可选优化）
  const ifNoneMatch = request.headers.get("If-None-Match");
  if (ifNoneMatch === etag) {
    return data(null, { status: 304 });
  }

  // 构造响应
  const headers = new Headers({
    "Content-Type": mimeType,
    "Content-Length": buffer.length.toString(),
    "Cache-Control": "public, max-age=86400", // 可按需调整
    ETag: etag,
  });

  return data(new Uint8Array(buffer), { headers });
})