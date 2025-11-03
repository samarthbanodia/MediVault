import { Shield, User, Stethoscope, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent } from "./ui/card";
import { useState } from "react";
import { ThemeToggle } from "./ThemeToggle";
import { useAuth } from "../contexts/AuthContext";

interface OnboardingPageProps {
  isDark: boolean;
  onToggleTheme: () => void;
  onNavigate: (page: string) => void;
}

export function OnboardingPage({ isDark, onToggleTheme, onNavigate }: OnboardingPageProps) {
  const { user, completeProfile } = useAuth();
  const [userType, setUserType] = useState<'patient' | 'doctor' | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Patient form data
  const [patientData, setPatientData] = useState({
    date_of_birth: "",
    gender: "",
    phone: "",
  });

  // Doctor form data
  const [doctorData, setDoctorData] = useState({
    license_number: "",
    specialization: "",
    hospital_affiliation: "",
    phone: "",
  });

  const handleSelectUserType = (type: 'patient' | 'doctor') => {
    setUserType(type);
    setError("");
  };

  const handlePatientSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await completeProfile('patient', patientData);
      onNavigate('dashboard');
    } catch (err: any) {
      setError(err.message || 'Failed to complete profile');
      setLoading(false);
    }
  };

  const handleDoctorSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    if (!doctorData.license_number || !doctorData.specialization) {
      setError("License number and specialization are required");
      setLoading(false);
      return;
    }

    try {
      await completeProfile('doctor', doctorData);
      onNavigate('doctor-dashboard');
    } catch (err: any) {
      setError(err.message || 'Failed to complete profile');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 to-secondary/5 p-4">
      <div className="absolute top-4 right-4">
        <ThemeToggle isDark={isDark} onToggle={onToggleTheme} />
      </div>

      <div className="max-w-2xl mx-auto py-12 space-y-8">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="flex justify-center mb-4">
            <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-lg">
              <Shield className="h-10 w-10 text-white" />
            </div>
          </div>
          <h1 className="text-3xl font-bold">Welcome to MediVault</h1>
          <p className="text-muted-foreground">
            Complete your profile to get started
          </p>
          {user && (
            <p className="text-sm text-muted-foreground">
              Signed in as: {user.email}
            </p>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
          </div>
        )}

        {/* Step 1: Select User Type */}
        {!userType && (
          <Card>
            <CardContent className="p-8">
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
                    onClick={() => handleSelectUserType('patient')}
                    className="group p-6 border-2 border-border rounded-xl hover:border-primary hover:bg-primary/5 transition-all text-left"
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
                    onClick={() => handleSelectUserType('doctor')}
                    className="group p-6 border-2 border-border rounded-xl hover:border-secondary hover:bg-secondary/5 transition-all text-left"
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
            </CardContent>
          </Card>
        )}

        {/* Step 2: Patient Form */}
        {userType === 'patient' && (
          <Card>
            <CardContent className="p-8">
              <form onSubmit={handlePatientSubmit} className="space-y-6">
                <div className="text-center mb-6">
                  <h2 className="text-xl font-semibold mb-2">Patient Information</h2>
                  <p className="text-sm text-muted-foreground">
                    Tell us a bit about yourself (optional - you can complete this later in your profile)
                  </p>
                </div>

                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="date_of_birth">Date of Birth</Label>
                    <Input
                      id="date_of_birth"
                      type="date"
                      value={patientData.date_of_birth}
                      onChange={(e) => setPatientData({ ...patientData, date_of_birth: e.target.value })}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="gender">Gender</Label>
                    <select
                      id="gender"
                      value={patientData.gender}
                      onChange={(e) => setPatientData({ ...patientData, gender: e.target.value })}
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      <option value="">Select gender</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                      <option value="other">Other</option>
                      <option value="prefer_not_to_say">Prefer not to say</option>
                    </select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="phone">Phone Number</Label>
                    <Input
                      id="phone"
                      type="tel"
                      placeholder="+1 (555) 000-0000"
                      value={patientData.phone}
                      onChange={(e) => setPatientData({ ...patientData, phone: e.target.value })}
                    />
                  </div>
                </div>

                <div className="flex gap-4 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setUserType(null)}
                    className="flex-1"
                    disabled={loading}
                  >
                    Back
                  </Button>
                  <Button
                    type="submit"
                    className="flex-1"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Completing...
                      </>
                    ) : (
                      <>
                        <CheckCircle2 className="mr-2 h-4 w-4" />
                        Complete Setup
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Step 2: Doctor Form */}
        {userType === 'doctor' && (
          <Card>
            <CardContent className="p-8">
              <form onSubmit={handleDoctorSubmit} className="space-y-6">
                <div className="text-center mb-6">
                  <h2 className="text-xl font-semibold mb-2">Healthcare Provider Information</h2>
                  <p className="text-sm text-muted-foreground">
                    Please provide your professional details
                  </p>
                </div>

                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="license_number">Medical License Number *</Label>
                    <Input
                      id="license_number"
                      placeholder="Enter your license number"
                      value={doctorData.license_number}
                      onChange={(e) => setDoctorData({ ...doctorData, license_number: e.target.value })}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="specialization">Specialization *</Label>
                    <Input
                      id="specialization"
                      placeholder="e.g., Cardiology, General Practice"
                      value={doctorData.specialization}
                      onChange={(e) => setDoctorData({ ...doctorData, specialization: e.target.value })}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="hospital_affiliation">Hospital/Clinic Affiliation</Label>
                    <Input
                      id="hospital_affiliation"
                      placeholder="Enter your primary affiliation"
                      value={doctorData.hospital_affiliation}
                      onChange={(e) => setDoctorData({ ...doctorData, hospital_affiliation: e.target.value })}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="phone">Phone Number</Label>
                    <Input
                      id="phone"
                      type="tel"
                      placeholder="+1 (555) 000-0000"
                      value={doctorData.phone}
                      onChange={(e) => setDoctorData({ ...doctorData, phone: e.target.value })}
                    />
                  </div>
                </div>

                <div className="flex gap-4 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setUserType(null)}
                    className="flex-1"
                    disabled={loading}
                  >
                    Back
                  </Button>
                  <Button
                    type="submit"
                    className="flex-1"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Completing...
                      </>
                    ) : (
                      <>
                        <CheckCircle2 className="mr-2 h-4 w-4" />
                        Complete Setup
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Privacy Notice */}
        <div className="text-center text-xs text-muted-foreground">
          <p>
            Your information is encrypted and securely stored.
            <br />
            You can update your profile anytime in settings.
          </p>
        </div>
      </div>
    </div>
  );
}
