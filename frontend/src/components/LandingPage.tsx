import { Shield, Clock, Lock, Users, CheckCircle2, Star, ArrowRight, Zap, Activity } from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";
import { ThemeToggle } from "./ThemeToggle";

interface LandingPageProps {
  isDark: boolean;
  onToggleTheme: () => void;
  onNavigate: (page: string) => void;
}

export function LandingPage({ isDark, onToggleTheme, onNavigate }: LandingPageProps) {
  const features = [
    {
      icon: Shield,
      title: "Military-Grade Security",
      description: "End-to-end encryption keeps your medical records completely private and secure",
    },
    {
      icon: Zap,
      title: "Instant Access",
      description: "Access your complete health history in seconds, from anywhere, on any device",
    },
    {
      icon: Activity,
      title: "Smart Analytics",
      description: "AI-powered insights help you understand your health trends and biomarkers",
    },
  ];

  const testimonials = [
    {
      name: "Sarah Johnson",
      role: "Chronic Care Patient",
      content: "MediVault transformed how I manage multiple specialists. Everything is finally in one secure place.",
      rating: 5,
      avatar: "SJ",
    },
    {
      name: "Dr. Michael Chen",
      role: "Cardiologist",
      content: "Having instant access to complete patient history has significantly improved the quality of care I can provide.",
      rating: 5,
      avatar: "MC",
    },
    {
      name: "Emily Rodriguez",
      role: "Family Medicine",
      content: "The timeline view makes it incredibly easy to track patient progress over time. Game-changer for chronic disease management.",
      rating: 5,
      avatar: "ER",
    },
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b border-border backdrop-blur-xl bg-background/80 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                <Shield className="h-6 w-6 text-white" />
              </div>
              <span className="font-bold text-xl">MediVault</span>
            </div>
            <div className="hidden md:flex items-center gap-8">
              <button className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Features
              </button>
              <button className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Pricing
              </button>
              <button className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                About
              </button>
              <button className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Docs
              </button>
            </div>
            <div className="flex items-center gap-3">
              <ThemeToggle isDark={isDark} onToggle={onToggleTheme} />
              <Button variant="ghost" onClick={() => onNavigate("login")}>
                Log In
              </Button>
              <Button 
                onClick={() => onNavigate("signup")}
                className="bg-primary hover:bg-primary/90"
              >
                Try for Free <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background Gradients */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/20 via-background to-background" />
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/30 rounded-full blur-3xl" />
        <div className="absolute top-20 right-1/4 w-96 h-96 bg-secondary/20 rounded-full blur-3xl" />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
          <div className="text-center space-y-8 max-w-4xl mx-auto">
            {/* Announcement Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-primary">
              <Zap className="h-4 w-4" />
              <span className="text-sm font-medium">Announcing our $5M Series A</span>
              <ArrowRight className="h-3 w-3" />
            </div>

            {/* Main Heading */}
            <h1 className="text-5xl lg:text-7xl font-bold tracking-tight">
              Your complete health records with{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary">
                long-term memory
              </span>
            </h1>

            {/* Subheading */}
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Securely store, organize, and share your medical records. AI-powered insights help you take control of your health journey.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button 
                size="lg"
                className="bg-primary hover:bg-primary/90 h-14 px-8 text-base"
                onClick={() => onNavigate("signup")}
              >
                Setup in 5 mins <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
              <Button 
                size="lg"
                variant="outline"
                className="h-14 px-8 text-base border-border hover:bg-card"
              >
                Explore Docs
              </Button>
            </div>

            {/* Social Proof */}
            <div className="flex items-center justify-center gap-8 pt-8">
              <div className="flex -space-x-3">
                {["JD", "SK", "AL", "MR"].map((initials, i) => (
                  <div
                    key={i}
                    className="h-10 w-10 rounded-full bg-gradient-to-br from-primary to-secondary border-2 border-background flex items-center justify-center text-white text-xs font-medium"
                  >
                    {initials}
                  </div>
                ))}
              </div>
              <div className="text-left">
                <div className="flex gap-0.5">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  Trusted by 50,000+ patients
                </p>
              </div>
            </div>
          </div>

          {/* Floating UI Elements */}
          <div className="relative mt-16 flex justify-center gap-8">
            {/* Mock 3D Cards */}
            <div className="hidden lg:block absolute -left-20 top-20 w-48 h-32 bg-gradient-to-br from-card to-card/50 border border-border rounded-2xl shadow-2xl transform -rotate-6 backdrop-blur-xl">
              <div className="p-4 space-y-2">
                <div className="flex items-center gap-2">
                  <Activity className="h-5 w-5 text-primary" />
                  <span className="text-sm font-medium">Blood Pressure</span>
                </div>
                <p className="text-2xl font-bold">120/80</p>
                <p className="text-xs text-muted-foreground">Normal Range</p>
              </div>
            </div>
            
            <div className="hidden lg:block absolute -right-20 top-32 w-48 h-32 bg-gradient-to-br from-card to-card/50 border border-border rounded-2xl shadow-2xl transform rotate-6 backdrop-blur-xl">
              <div className="p-4 space-y-2">
                <div className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-secondary" />
                  <span className="text-sm font-medium">Records</span>
                </div>
                <p className="text-2xl font-bold">142</p>
                <p className="text-xs text-muted-foreground">Securely Stored</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">Why Choose MediVault?</h2>
          <p className="text-xl text-muted-foreground">
            Everything you need to manage your health records effectively
          </p>
        </div>
        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feature) => (
            <Card key={feature.title} className="border-border bg-card/50 backdrop-blur hover:bg-card transition-colors">
              <CardContent className="p-8 space-y-4">
                <div className="h-14 w-14 rounded-xl bg-gradient-to-br from-primary/20 to-secondary/20 border border-primary/20 flex items-center justify-center">
                  <feature.icon className="h-7 w-7 text-primary" />
                </div>
                <h3 className="text-xl font-bold">{feature.title}</h3>
                <p className="text-muted-foreground leading-relaxed">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Features List */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <h2 className="text-4xl font-bold">Everything You Need</h2>
            <p className="text-lg text-muted-foreground">
              A complete platform designed for modern healthcare management
            </p>
            <div className="space-y-4">
              {[
                "Upload and organize unlimited medical documents",
                "AI-powered search to find records instantly",
                "Share records securely with healthcare providers",
                "Track biomarkers and health metrics over time",
                "Automatic reminders for appointments and medications",
                "Export comprehensive reports for insurance claims",
              ].map((item) => (
                <div key={item} className="flex items-start gap-3">
                  <div className="h-6 w-6 rounded-full bg-secondary/20 flex items-center justify-center shrink-0 mt-0.5">
                    <CheckCircle2 className="h-4 w-4 text-secondary" />
                  </div>
                  <span className="text-base">{item}</span>
                </div>
              ))}
            </div>
            <Button size="lg" className="mt-4" onClick={() => onNavigate("signup")}>
              Get Started <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
          <div className="relative">
            <div className="aspect-square bg-gradient-to-br from-card to-card/50 border border-border rounded-3xl shadow-2xl backdrop-blur-xl p-8 flex items-center justify-center">
              <Users className="h-48 w-48 text-muted-foreground/20" />
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">Trusted by Thousands</h2>
          <p className="text-xl text-muted-foreground">
            See what our users have to say
          </p>
        </div>
        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((testimonial) => (
            <Card key={testimonial.name} className="border-border bg-card/50 backdrop-blur">
              <CardContent className="p-8 space-y-4">
                <div className="flex gap-1">
                  {Array.from({ length: testimonial.rating }).map((_, i) => (
                    <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                <p className="text-muted-foreground">{testimonial.content}</p>
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white text-sm font-medium">
                    {testimonial.avatar}
                  </div>
                  <div>
                    <p className="font-semibold">{testimonial.name}</p>
                    <p className="text-sm text-muted-foreground">{testimonial.role}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="relative overflow-hidden rounded-3xl">
          <div className="absolute inset-0 bg-gradient-to-r from-primary via-blue-500 to-secondary" />
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-transparent via-transparent to-black/20" />
          <div className="relative p-16 text-center space-y-6 text-white">
            <h2 className="text-4xl font-bold">Ready to Get Started?</h2>
            <p className="text-xl opacity-90 max-w-2xl mx-auto">
              Join thousands of users who trust MediVault with their health records
            </p>
            <Button 
              size="lg" 
              variant="secondary"
              className="bg-white text-black hover:bg-gray-100 h-14 px-8"
              onClick={() => onNavigate("signup")}
            >
              Create Free Account <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border mt-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                  <Shield className="h-5 w-5 text-white" />
                </div>
                <span className="font-bold">MediVault</span>
              </div>
              <p className="text-sm text-muted-foreground">
                Secure medical record management for everyone
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="hover:text-foreground cursor-pointer">Features</li>
                <li className="hover:text-foreground cursor-pointer">Pricing</li>
                <li className="hover:text-foreground cursor-pointer">Security</li>
                <li className="hover:text-foreground cursor-pointer">Updates</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="hover:text-foreground cursor-pointer">About</li>
                <li className="hover:text-foreground cursor-pointer">Blog</li>
                <li className="hover:text-foreground cursor-pointer">Careers</li>
                <li className="hover:text-foreground cursor-pointer">Contact</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="hover:text-foreground cursor-pointer">Privacy</li>
                <li className="hover:text-foreground cursor-pointer">Terms</li>
                <li className="hover:text-foreground cursor-pointer">HIPAA Compliance</li>
                <li className="hover:text-foreground cursor-pointer">Cookies</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-border mt-12 pt-8 text-center text-sm text-muted-foreground">
            © 2025 MediVault. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}
