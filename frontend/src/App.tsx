import { useState, useEffect } from "react";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { LandingPage } from "./components/LandingPage";
import { LoginPage } from "./components/LoginPage";
import { SignupPage } from "./components/SignupPage";
import { OnboardingPage } from "./components/OnboardingPage";
import { Dashboard } from "./components/Dashboard";
import { UploadPage } from "./components/UploadPage";
import { SearchPage } from "./components/SearchPage";
import { TimelinePage } from "./components/TimelinePage";
import { DoctorDashboard } from "./components/DoctorDashboard";

type Page =
  | "landing"
  | "login"
  | "signup"
  | "onboarding"
  | "dashboard"
  | "upload"
  | "search"
  | "timeline"
  | "doctor-dashboard";

function AppContent() {
  const { isAuthenticated, isLoading, user } = useAuth();
  const [currentPage, setCurrentPage] = useState<Page>("landing");
  const [isDark, setIsDark] = useState(false);

  // Initialize dark mode from localStorage or system preference (default to dark)
  useEffect(() => {
    const savedTheme = localStorage.getItem("theme");

    // Default to dark mode unless explicitly set to light
    if (savedTheme === "light") {
      setIsDark(false);
      document.documentElement.classList.remove("dark");
    } else {
      setIsDark(true);
      document.documentElement.classList.add("dark");
    }
  }, []);

  // Handle authentication state changes - SIMPLIFIED
  useEffect(() => {
    console.log('🔍 Auth State:', { isLoading, isAuthenticated, user, currentPage });

    if (!isLoading && isAuthenticated && user) {
      // Redirect to dashboard after authentication
      if (currentPage === "landing" || currentPage === "login" || currentPage === "signup") {
        console.log('✅ User authenticated, redirecting to dashboard');
        // Always go to patient dashboard for now (simplified)
        setCurrentPage("dashboard");
      }
    } else if (!isLoading && !isAuthenticated) {
      // Redirect to landing if not authenticated and trying to access protected pages
      const protectedPages: Page[] = ["dashboard", "upload", "search", "timeline", "doctor-dashboard"];
      if (protectedPages.includes(currentPage)) {
        console.log('❌ Not authenticated, redirecting to landing');
        setCurrentPage("landing");
      }
    }
  }, [isAuthenticated, isLoading, user, currentPage]);

  // Toggle dark mode
  const toggleTheme = () => {
    setIsDark(!isDark);
    if (!isDark) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  };

  const navigate = (page: Page) => {
    setCurrentPage(page);
  };

  // Show loading screen while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  const renderPage = () => {
    const commonProps = {
      isDark,
      onToggleTheme: toggleTheme,
      onNavigate: navigate,
    };

    switch (currentPage) {
      case "landing":
        return <LandingPage {...commonProps} />;
      case "login":
        return <LoginPage {...commonProps} />;
      case "signup":
        return <SignupPage {...commonProps} />;
      case "onboarding":
        return <OnboardingPage {...commonProps} />;
      case "dashboard":
        return <Dashboard {...commonProps} />;
      case "upload":
        return <UploadPage {...commonProps} />;
      case "search":
        return <SearchPage {...commonProps} />;
      case "timeline":
        return <TimelinePage {...commonProps} />;
      case "doctor-dashboard":
        return <DoctorDashboard {...commonProps} />;
      default:
        return <LandingPage {...commonProps} />;
    }
  };

  return <div className="min-h-screen">{renderPage()}</div>;
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
