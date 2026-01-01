import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function HomePage() {
  const features = [
    {
      title: 'Self-Sovereign Identity',
      description: 'Control your digital identity with DID registry on Solana blockchain',
    },
    {
      title: 'Verifiable Credentials',
      description: 'Issue, store, and share tamper-proof credentials with zero-knowledge proofs',
    },
    {
      title: 'AI-Powered Verification',
      description: 'Automated document validation using Claude Agent SDK',
    },
    {
      title: 'Privacy-First',
      description: 'Hash-only commitments on-chain, encrypted data off-chain (IPFS)',
    },
  ];

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="text-center space-y-6 py-12">
        <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
          Self-Sovereign Identity on Solana
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Secure, decentralized identity platform powered by Solana blockchain and Claude Agent SDK
        </p>
        <div className="flex gap-4 justify-center">
          <Button asChild size="lg">
            <Link href="/identity/create">Create Your Identity</Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <Link href="/dashboard">View Dashboard</Link>
          </Button>
        </div>
      </section>

      {/* Features Grid */}
      <section className="grid md:grid-cols-2 gap-6">
        {features.map((feature) => (
          <Card key={feature.title}>
            <CardHeader>
              <CardTitle>{feature.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>{feature.description}</CardDescription>
            </CardContent>
          </Card>
        ))}
      </section>

      {/* Architecture Overview */}
      <section className="space-y-4">
        <h2 className="text-3xl font-bold text-center">Architecture</h2>
        <div className="grid md:grid-cols-3 gap-6 text-center">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Layer 2: Agent Layer</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                4 Claude Agent SDK agents for document validation, fraud detection, compliance, and orchestration
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Layer 1: API Gateway</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                FastAPI gateway with JWT authentication, rate limiting, and agent proxy endpoints
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Layer 0: Solana</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                2 lightweight Anchor programs for DID registry and verifiable credentials
              </p>
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  );
}
