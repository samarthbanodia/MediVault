import { Shield, AlertCircle, User, Stethoscope, Loader2, ArrowLeft, Mail, Lock, UserCircle } from "lucide-react";
import { Button } from "./ui/button";
import { ThemeToggle } from "./ThemeToggle";
import { useState } from "react";
import { useAuth } from "../contexts/AuthContext";

interface SignupPageProps {
  isDark: boolean;
  onToggleTheme: () => void;
  onNavigate: (page: string) => void;
}

export function SignupPage({ isDark, onToggleTheme, onNavigate }: SignupPageProps) {
  const { signup } = useAuth();
  const [selectedType, setSelectedType] = useState<'patient' | 'doctor' | null>(null);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedType) {
      setError("Please select whether you are a Patient or Healthcare Provider");
      return;
    }

    setError("");
    setLoading(true);

    try {
      await signup(email, password, fullName, selectedType);
      // User will be redirected by App.tsx useEffect
    } catch (err: any) {
      setError(err.message || "Signup failed. Please try again.");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 to-secondary/5 p-4">
      <div className="absolute top-4 right-4">
        <ThemeToggle isDark={isDark} onToggle={onToggleTheme} />
      </div>

      {/* Back Button */}
      <button
        onClick={() => onNavigate("landing")}
        className="absolute top-4 left-4 p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
      >
        <ArrowLeft className="h-5 w-5" />
      </button>

      <div className="max-w-2xl mx-auto py-12 space-y-8">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="flex justify-center mb-4">
            <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-lg">
              <Shield className="h-10 w-10 text-white" />
            </div>
          </div>
          <h1 className="text-3xl font-bold">Create Your Account</h1>
          <p className="text-muted-foreground">
            Sign up to get started with MediVault
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
          </div>
        )}

        <div className="bg-card rounded-xl border border-border shadow-sm p-8">
          {!selectedType ? (
            /* Step 1: Select User Type */
            <div className="space-y-6">
              <div className="text-center">
                <h2 className="text-xl font-semibold mb-2">I am a...</h2>
                <p className="text-sm text-muted-foreground">
                  Select your role to personalize your experience
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                {/* Patient Card */}
                <button
                  onClick={() => setSelectedType('patient')}
                  className="group p-6 border-2 border-border rounded-xl hover:border-primary hover:bg-primary/5 transition-all text-left"
                  disabled={loading}
                >
                  <div className="flex flex-col items-center text-center space-y-4">
                    <div className="h-16 w-16 rounded-full bg-primary/10 group-hover:bg-primary/20 flex items-center justify-center transition-colors">
                      <User className="h-8 w-8 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg mb-1">Patient</h3>
                      <p className="text-sm text-muted-foreground">
                        Store and manage your medical records
                      </p>
                    </div>
                  </div>
                </button>

                {/* Doctor Card */}
                <button
                  onClick={() => setSelectedType('doctor')}
                  className="group p-6 border-2 border-border rounded-xl hover:border-secondary hover:bg-secondary/5 transition-all text-left"
                  disabled={loading}
                >
                  <div className="flex flex-col items-center text-center space-y-4">
                    <div className="h-16 w-16 rounded-full bg-secondary/10 group-hover:bg-secondary/20 flex items-center justify-center transition-colors">
                      <Stethoscope className="h-8 w-8 text-secondary" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg mb-1">Healthcare Provider</h3>
                      <p className="text-sm text-muted-foreground">
                        Access and manage patient records
                      </p>
                    </div>
                  </div>
                </button>
              </div>
            </div>
          ) : (
            /* Step 2: Signup Form */
            <div className="space-y-6">
              <div className="text-center">
                <h2 className="text-xl font-semibold mb-2">
                  Sign up as {selectedType === 'patient' ? 'Patient' : 'Healthcare Provider'}
                </h2>
                <p className="text-sm text-muted-foreground">
                  Fill in your details to create your account
                </p>
              </div>

              <form onSubmit={handleSignup} className="space-y-4">
                {/* Full Name Field */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Full Name
                  </label>
                  <div className="relative">
                    <UserCircle className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                    <input
                      type="text"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      className="w-full pl-10 pr-4 py-3 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="John Doe"
                      required
                      disabled={loading}
                    />
                  </div>
                </div>

                {/* Email Field */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Email Address
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full pl-10 pr-4 py-3 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="you@example.com"
                      required
                      disabled={loading}
                    />
                  </div>
                </div>

                {/* Password Field */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full pl-10 pr-4 py-3 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="••••••••"
                      required
                      minLength={6}
                      disabled={loading}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Must be at least 6 characters
                  </p>
                </div>

                <Button
                  type="submit"
                  className="w-full h-12"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Creating account...
                    </>
                  ) : (
                    'Create Account'
                  )}
                </Button>

                <Button
                  type="button"
                  variant="outline"
                  className="w-full"
                  onClick={() => setSelectedType(null)}
                  disabled={loading}
                >
                  Back
                </Button>
              </form>
            </div>
          )}
        </div>

        {/* Login Link */}
        <div className="text-center">
          <p className="text-sm text-muted-foreground">
            Already have an account?{" "}
            <button
              onClick={() => onNavigate("login")}
              className="text-primary hover:underline font-medium"
            >
              Log in
            </button>
          </p>
        </div>

        {/* Privacy Notice */}
        <div className="text-center text-xs text-muted-foreground">
          <p>
            Your information is encrypted and securely stored.
            <br />
            By signing up, you agree to our{" "}
            <button className="underline hover:text-foreground">Terms</button> and{" "}
            <button className="underline hover:text-foreground">Privacy Policy</button>
          </p>
        </div>
      </div>
    </div>
  );
}
