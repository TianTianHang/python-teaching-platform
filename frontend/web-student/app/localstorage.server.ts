// app/utils/FileService.ts

import { readFile, writeFile, mkdir, access } from "fs/promises";
import { join, extname } from "path";
import { randomBytes } from "crypto";
import mime from "mime";
export type FileServiceOptions = {
  /** 存储目录（相对于项目根目录或绝对路径） */
  storageDir: string;
  /** 公开访问的基础路径（如 "/uploads/avatars"） */
  publicPathPrefix: string;
  /** 允许的 MIME 类型 */
  allowedMimeTypes?: string[];
  /** 允许的扩展名（小写） */
  allowedExtensions?: string[];
  /** 最大文件大小（字节） */
  maxSize?: number;
  /**
   * 是否为公开文件：
   * - true：生成可被 Nginx 直接访问的 URL，不提供 downloadResponse（或仅 fallback）
   * - false：文件私有，必须通过 createDownloadResponse 访问
   */
  isPublic?: boolean;
};

export class FileService {
  private options: Required<Omit<FileServiceOptions, "allowedMimeTypes" | "allowedExtensions">> & {
    allowedMimeTypes: string[];
    allowedExtensions: string[];
  };

  constructor(options: FileServiceOptions) {
    this.options = {
      storageDir: options.storageDir,
      publicPathPrefix: options.publicPathPrefix.replace(/\/+$/, ""), // 去尾斜杠
      allowedMimeTypes: options.allowedMimeTypes || [],
      allowedExtensions: options.allowedExtensions || [],
      maxSize: options.maxSize ?? 5 * 1024 * 1024, // 5MB
      isPublic: options.isPublic ?? true,
    };
  }

  /**
   * 上传文件并绑定到逻辑 key（如 "user-123-avatar"）
   * 实际保存为 "user-123-avatar.<ext>"
   */
  async upload(key: string, fileUpload: File): Promise<string> {
    // 1. 验证 MIME 类型
    if (
      this.options.allowedMimeTypes.length > 0 &&
      !this.options.allowedMimeTypes.includes(fileUpload.type)
    ) {
      throw new Error(`Disallowed MIME type: ${fileUpload.type}`);
    }

    // 2. 获取并验证扩展名
    const originalFilename = fileUpload.name || "";
    const ext = extname(originalFilename).toLowerCase();

    if (
      this.options.allowedExtensions.length > 0 &&
      !this.options.allowedExtensions.includes(ext)
    ) {
      throw new Error(`Disallowed file extension: ${ext}`);
    }

    // 3. 检查文件大小
    const arrayBuffer = await fileUpload.arrayBuffer();
    if (arrayBuffer.byteLength > this.options.maxSize) {
      throw new Error(`File too large. Max: ${this.options.maxSize / 1024 / 1024}MB`);
    }

    // 4. 构造真实文件名
    const realFilename = `${key}${ext}`;
    const absoluteDir = join(process.cwd(), this.options.storageDir);
    const filePath = join(absoluteDir, realFilename);

    // 5. 确保目录存在并写入
    await mkdir(absoluteDir, { recursive: true });
    await writeFile(filePath, Buffer.from(arrayBuffer));

    // 6. 返回公开 URL（即使私有也返回，但生产环境不应暴露）
    return `${this.options.publicPathPrefix}/${realFilename}`.replace(/\/+/g, "/");
  }

  /**
   * 获取公开访问 URL（适用于 isPublic=true 的场景）
   * 注意：此方法不检查文件是否存在！
   */
  getPublicUrl(key: string, originalExt: string): string {
    const ext = originalExt.toLowerCase();
    if (
      this.options.allowedExtensions.length > 0 &&
      !this.options.allowedExtensions.includes(ext)
    ) {
      throw new Error("Invalid extension for public URL");
    }
    return `${this.options.publicPathPrefix}/${key}${ext}`.replace(/\/+/g, "/");
  }

  /**
   * （仅私有文件使用）创建文件下载 Response
   * 需要调用方确保 key + ext 对应的文件存在
   */
  async createDownloadResponse(
    key: string,
    contentType: string,
    originalExt: string,
    filename?: string,
    inline: boolean = true
  ): Promise<Response> {
    if (this.options.isPublic) {
      console.warn("Warning: createDownloadResponse called on a public FileService.");
    }

    const ext = originalExt.toLowerCase();
    const realFilename = `${key}${ext}`;
    const absolutePath = join(process.cwd(), this.options.storageDir, realFilename);

    // 检查文件是否存在
    try {
      await access(absolutePath);
    } catch {
      throw new Response("File not found", { status: 404 });
    }

    const buffer = await readFile(absolutePath);
    const headers: HeadersInit = {
      "Content-Type": contentType,
      "Content-Length": buffer.length.toString(),
    };

    if (filename) {
      const disposition = inline ? "inline" : "attachment";
      headers["Content-Disposition"] = `${disposition}; filename="${encodeURIComponent(filename)}"`;
    }

    return new Response(new Uint8Array(buffer), { headers });
  }
  /**
 * 读取文件原始 Buffer（内部使用）
 */
  async readFileBuffer(key: string, ext: string): Promise<Buffer> {
    const realFilename = `${key}${ext.toLowerCase()}`;
    const absolutePath = join(process.cwd(), this.options.storageDir, realFilename);
    try {
      await access(absolutePath);
      return await readFile(absolutePath);
    } catch {
      throw new Response("File not found", { status: 404 });
    }
  }
  /**
 * 获取文件元数据（MIME、大小、扩展名等）
 */
  async getFileMetadata(key: string, ext: string) {
    const buffer = await this.readFileBuffer(key, ext);
    const mimeType = mime.getType(ext) || "application/octet-stream";
    const etag = `"${buffer.subarray(0, 16).toString("hex")}-${buffer.length}"`; // 简易 ETag
    return {
      buffer,
      mimeType,
      size: buffer.length,
      etag,
    };
  }
  /**
   * （可选）删除文件 TODO
   */
  async delete(key: string, ext: string): Promise<void> {
    const realFilename = `${key}${ext.toLowerCase()}`;
    const absolutePath = join(process.cwd(), this.options.storageDir, realFilename);
    // 使用 fs.unlink 实现（略）
  }
}


const services = new Map<string, FileService>();
// 初始化所有服务（只运行一次）
function initServices() {
  if (services.size > 0) return;

  services.set(
    "avatars",
    new FileService({
      storageDir: "./public/uploads/avatars",
      publicPathPrefix: "/upload/avatars", // 注意：现在统一走 /files 路由
      allowedMimeTypes: ["image/jpeg", "image/png", "image/webp", "image/gif"],
      allowedExtensions: [".jpg", ".jpeg", ".png", ".webp", ".gif"],
      maxSize: 10 * 1024 * 1024,
      isPublic: true,
    })
  );

  services.set(
    "documents",
    new FileService({
      storageDir: "./private-uploads/documents",
      publicPathPrefix: "/upload/documents",
      allowedMimeTypes: ["application/pdf"],
      allowedExtensions: [".pdf"],
      maxSize: 20 * 1024 * 1024,
      isPublic: false,
    })
  );
  console.log("file service init success!")
}

export function fileServices() {
  if(services.size==0){
     initServices();
  }
 
  return services;
}
initServices();
// 导出单例实例供上传使用
export const avatarService = services.get("avatars")!;
export const documentService = services.get("documents")!;
