
# Skills
- /web-search 从网络上查询信息
- /fetch:fetch (MCP)  将网页转为markdown文档

## Error Handling Patterns and Best Practices

### Page-Level Error Handling

All main pages now implement consistent error handling patterns:

#### 1. Single Data Source Pattern (Problems, Profile, Membership)
```typescript
// loader/clientLoader
export async function clientLoader({ request }: Route.ClientLoaderArgs) {
    try {
        const data = await clientHttp.get<Type>(endpoint);
        return data;
    } catch (error: any) {
        if (error.response?.status === 401) {
            throw redirect('/auth/login');
        }
        throw new Response(JSON.stringify({ message: error.message || '请求失败' }), {
            status: error.response?.status || 500,
            statusText: error.message || '请求失败'
        });
    }
}

// ErrorBoundary
export function ErrorBoundary({ error }: { error: Error }) {
    const errorResponse = error as any;
    const status = errorResponse.status ? parseInt(errorResponse.status) : 500;
    const message = errorResponse.message || '加载失败';

    return <ErrorCard status={status} message={message} title="加载失败" />;
}
```

#### 2. Multiple Data Source Pattern (Course Detail)
For pages with independent data sources (e.g., course + enrollment), use `Promise.allSettled`:

```typescript
export async function clientLoader({ params, request }: Route.ClientLoaderArgs) {
    const { courseId } = params;

    const results = await Promise.allSettled([
        clientHttp.get<Course>(`/courses/${courseId}`),
        clientHttp.get<Enrollment>(`/enrollments/?course=${courseId}`)
    ]);

    const courseResult = results[0];
    const enrollmentResult = results[1];

    return {
        course: {
            data: courseResult.status === 'fulfilled' ? courseResult.value : null,
            error: courseResult.status === 'rejected' ? parseError(courseResult.reason) : null
        },
        enrollment: {
            data: enrollmentResult.status === 'fulfilled' ? enrollmentResult.value : null,
            error: enrollmentResult.status === 'rejected' ? parseError(enrollmentResult.reason) : null
        }
    };
}
```

#### 3. Type Definitions
```typescript
interface SectionResult<T> {
    data: T | null;
    error: { status: number; message: string } | null;
}

function parseError(error: any): { status: number; message: string } {
    if (error.response?.status) {
        return {
            status: parseInt(error.response.status),
            message: error.response?.data?.detail || error.message || '请求失败'
        };
    }
    return {
        status: 500,
        message: error.message || '请求失败'
    };
}
```

#### 4. Component Error Handling Logic
```typescript
// Handle course loading error
if (course?.error) {
    return <ErrorCard status={course.error.status} message={course.error.message} />;
}

// Handle enrollment error while showing course
if (enrollment?.error && course?.data) {
    return (
        <>
            {/* Display course content normally */}
            {course.data.title}

            {/* Show enrollment error */}
            <ErrorCard status={enrollment.error.status} message={enrollment.error.message} />
        </>
    );
}
```

### Design Decisions

1. **ErrorCard**: Reusable component that displays friendly Chinese error messages with retry functionality
2. **401 Handling**: Always redirect to login page for authentication errors
3. **Partial Loading**: Allow some data to load successfully even if others fail
4. **YAGNI Principle**: Don't extract utilities until they're needed in multiple places
5. **SSR Compatibility**: Use clientLoader for hydration, not server loader

### Common Patterns

1. **Retry Strategy**:
   - Network errors (5xx, 429): Retryable
   - Client errors (4xx): Not retryable (except 429)

2. **User Experience**:
   - Show "重新加载" button for retriable errors
   - Show "返回首页" button on all ErrorCard instances
   - Display friendly Chinese error messages

3. **Code Organization**:
   - Keep error handling logic simple and local to each page
   - Use consistent type definitions where needed
   - Prefer direct parsing over shared utilities for simplicity
