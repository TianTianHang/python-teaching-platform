
import { commitSession, getSession, setUserCache } from '~/sessions.server';
import type { User } from '~/types/user';
import type { Route } from './+types/auth.set-session';

export async function action({ request }: Route.ActionArgs) {
  const formData = await request.formData();
  const accessToken = String(formData.get('accessToken'));
  const refreshToken = String(formData.get('refreshToken'));
  const userJson = String(formData.get('user'));
  
  const user: User = JSON.parse(userJson);
  
  const session = await getSession(request.headers.get('Cookie'));
  session.set('accessToken', accessToken);
  session.set('refreshToken', refreshToken);
  setUserCache(session, user);
  session.set('isAuthenticated', true);
  
  return Response.json({ success: true }, {
    headers: {
      'Set-Cookie': await commitSession(session),
    },
  });
}