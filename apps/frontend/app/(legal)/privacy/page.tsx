import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Privacy Policy — Bharat Vanguard News (BVN)',
  description: 'Privacy policy for Bharat Vanguard News.',
};

export default function PrivacyPolicyPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 pt-16 pb-24 article-body">
      <h1 className="text-4xl font-bold text-text-primary mb-8">Privacy Policy</h1>
      <p className="text-text-secondary leading-relaxed mb-6">
        At Bharat Vanguard News, we take your privacy seriously. This privacy policy describes how we collect, use, and handle your information.
      </p>
      
      <h2 className="text-2xl font-bold mt-10 mb-4 text-text-primary">Information Collection</h2>
      <p className="text-text-secondary leading-relaxed mb-6">
        We collect standard analytics information to improve our services. When you subscribe to our newsletter, we collect your email address. We do not sell your personal data to third parties.
      </p>
      
      <h2 className="text-2xl font-bold mt-10 mb-4 text-text-primary">Cookies</h2>
      <p className="text-text-secondary leading-relaxed mb-6">
        We use essential cookies to maintain user sessions and preferences (such as Dark Mode settings). We do not use intrusive third-party tracking cookies.
      </p>
    </div>
  );
}
