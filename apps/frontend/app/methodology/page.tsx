import type { Metadata } from 'next';
import { Scale, CheckCircle2, ShieldAlert, Cpu } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Methodology — Bharat Vanguard News (BVN)',
  description: 'Learn how Bharat Vanguard News calculates Trust Scores using AI and cross-referencing techniques.',
};

export default function MethodologyPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 pt-16 pb-24">
      <h1 className="text-4xl sm:text-5xl font-bold text-text-primary mb-6">Our Methodology</h1>
      <p className="text-xl text-text-secondary leading-relaxed mb-12">
        At Bharat Vanguard News (BVN), our core mission is to bring transparency and evidence-based verification to the news ecosystem. We utilize advanced Artificial Intelligence (AI) to evaluate the credibility of news stories before they reach you.
      </p>

      <section className="mb-12">
        <h2 className="text-2xl font-bold text-text-primary mb-6 flex items-center gap-3">
          <Scale className="text-primary" /> The Trust Score Algorithm
        </h2>
        <p className="text-lg text-text-secondary leading-relaxed mb-6">
          The <strong>Trust Score (0-100)</strong> is an automated metric that indicates the strength of the evidence supporting a news article. It is calculated by a fine-tuned Natural Language Processing (NLP) model that assesses multiple dimensions of a text.
        </p>
        
        <div className="grid gap-6">
          <div className="bg-surface p-6 rounded-2xl border border-border">
            <h3 className="text-lg font-bold text-text-primary mb-2 flex items-center gap-2">
              <CheckCircle2 size={18} className="text-emerald" /> Fact-Based Reporting (40%)
            </h3>
            <p className="text-text-muted">
              The algorithm evaluates whether the article relies on primary sources, verifiable data, direct quotes, and empirical evidence rather than anonymous hearsay.
            </p>
          </div>
          
          <div className="bg-surface p-6 rounded-2xl border border-border">
            <h3 className="text-lg font-bold text-text-primary mb-2 flex items-center gap-2">
              <ShieldAlert size={18} className="text-amber" /> Bias & Emotion Mitigation (30%)
            </h3>
            <p className="text-text-muted">
              We penalize highly sensationalized language, emotional manipulation, and partisan framing. Articles that maintain a neutral, objective tone receive higher scores.
            </p>
          </div>

          <div className="bg-surface p-6 rounded-2xl border border-border">
            <h3 className="text-lg font-bold text-text-primary mb-2 flex items-center gap-2">
              <Cpu size={18} className="text-primary" /> Cross-Referencing Consensus (30%)
            </h3>
            <p className="text-text-muted">
              Our backend cross-references the core claims of an article against other reputable publishers. If a claim is an outlier with no corroborating coverage, the trust score is dynamically lowered.
            </p>
          </div>
        </div>
      </section>

      <section className="mb-12">
        <h2 className="text-2xl font-bold text-text-primary mb-4">Limitations of the AI</h2>
        <p className="text-lg text-text-secondary leading-relaxed">
          While our AI models are trained on millions of data points, they are not perfect. The Trust Score evaluates the <em>structural integrity</em> of the reporting, not the absolute ground truth of the event. An opinion piece may receive a low Trust Score because it lacks objective facts, even if the author's opinion is valid. We encourage readers to use the Trust Score as a tool for critical thinking, not as the final arbiter of truth.
        </p>
      </section>

    </div>
  );
}
