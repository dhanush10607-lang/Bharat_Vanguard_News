'use client';
import { useEffect, Suspense } from 'react';
import { useRouter } from 'next/navigation';
import { Zap } from 'lucide-react';
import { authApi } from '@/lib/api';
import { saveAuth } from '@/lib/utils';
import { toast } from 'sonner';

function CallbackHandler() {
  const router = useRouter();

  useEffect(() => {
    const hash = window.location.hash;
    const params = new URLSearchParams(hash.replace('#', '?'));
    const accessToken = params.get('access_token');
    const error = params.get('error');
    const errorDescription = params.get('error_description');

    if (error) {
      toast.error(errorDescription || 'Google login failed');
      router.push('/login');
      return;
    }

    if (!accessToken) {
      // Also check query params (some OAuth flows use these)
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
      if (!code) {
        toast.error('No authentication token received');
        router.push('/login');
        return;
      }
    }

    if (accessToken) {
      authApi
        .verifyGoogleToken(accessToken)
        .then((result) => {
          if (result.access_token) {
            saveAuth(result.access_token, result.user || {});
            toast.success('Signed in with Google!');
            router.push('/');
          } else {
            throw new Error('No token in response');
          }
        })
        .catch((err) => {
          console.error('OAuth verify failed:', err);
          toast.error('Authentication failed. Please try again.');
          router.push('/login');
        });
    }
  }, [router]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-4">
      <div className="w-14 h-14 rounded-2xl bg-primary/20 border border-primary/30 flex items-center justify-center">
        <Zap size={24} className="text-primary animate-pulse" />
      </div>
      <div className="text-center">
        <h2 className="text-lg font-semibold text-text-primary">Signing you in…</h2>
        <p className="text-sm text-text-muted mt-1">Completing Google authentication</p>
      </div>
      <div className="flex gap-1.5 mt-2">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="w-2 h-2 rounded-full bg-primary animate-bounce"
            style={{ animationDelay: `${i * 0.15}s` }}
          />
        ))}
      </div>
    </div>
  );
}

export default function AuthCallbackPage() {
  return (
    <Suspense fallback={null}>
      <CallbackHandler />
    </Suspense>
  );
}
