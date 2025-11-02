import {
  Shield,
  Upload,
  Search,
  Clock,
  FileText,
  Activity,
  AlertCircle,
  TrendingUp,
  Home,
  Settings,
  LogOut,
  Menu,
  RefreshCw,
} from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { ThemeToggle } from "./ThemeToggle";
import { StatusBadge } from "./StatusBadge";
import { Alert, AlertDescription } from "./ui/alert";
import { Avatar, AvatarFallback } from "./ui/avatar";
import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { apiService } from "../services/api";
import { cacheService } from "../services/cache";

interface DashboardProps {
  isDark: boolean;
  onToggleTheme: () => void;
  onNavigate: (page: string) => void;
}

export function Dashboard({ isDark, onToggleTheme, onNavigate }: DashboardProps) {
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  // Data state
  const [summary, setSummary] = useState<any>(null);
  const [recentRecords, setRecentRecords] = useState<any[]>([]);
  const [anomalies, setAnomalies] = useState<any[]>([]);

  // Fetch dashboard data
  const fetchDashboardData = async (useCache = true) => {
    try {
      setRefreshing(!loading);

      // Try to load from cache first for instant display
      if (useCache) {
        const cachedSummary = await cacheService.getCachedUserData('dashboard_summary');
        const cachedRecords = await cacheService.getCachedRecords();
        const cachedAnomalies = await cacheService.getCachedAnomalies();

        if (cachedSummary) setSummary(cachedSummary);
        if (cachedRecords) setRecentRecords(cachedRecords.slice(0, 3));
        if (cachedAnomalies) setAnomalies(cachedAnomalies.slice(0, 3));

        if (cachedSummary && cachedRecords && cachedAnomalies) {
          setLoading(false);
        }
      }

      // Fetch fresh data from API
      const [summaryRes, recordsRes, anomaliesRes] = await Promise.all([
        apiService.records.getSummary(),
        apiService.records.getAll({ limit: 20, offset: 0 }),
        apiService.records.getAnomalies({ critical_only: false, unacknowledged_only: true })
      ]);

      // Update state with fresh data
      setSummary(summaryRes.summary);
      setRecentRecords(recordsRes.records.slice(0, 3));
      setAnomalies(anomaliesRes.anomalies.slice(0, 3));

      // Cache the data
      await cacheService.cacheUserData('dashboard_summary', summaryRes.summary);
      await cacheService.cacheRecords(recordsRes.records);
      await cacheService.cacheAnomalies(anomaliesRes.anomalies);

      setLoading(false);
      setRefreshing(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleLogout = async () => {
    await logout();
    onNavigate("landing");
  };

  const handleRefresh = () => {
    fetchDashboardData(false); // Force fresh data
  };

  // Calculate stats from real data
  const stats = [
    {
      label: "Total Records",
      value: summary?.total_records?.toString() || "0",
      icon: FileText,
      trend: summary?.total_records > 0 ? `${summary.total_records} uploaded` : "No records yet",
      color: "text-primary",
    },
    {
      label: "Critical Alerts",
      value: summary?.critical_records?.toString() || "0",
      icon: Clock,
      trend: summary?.critical_records > 0 ? `${summary.critical_records} need attention` : "All good",
      color: summary?.critical_records > 0 ? "text-danger" : "text-success",
    },
    {
      label: "Pending Anomalies",
      value: summary?.unacknowledged_anomalies?.toString() || "0",
      icon: Activity,
      trend: summary?.unacknowledged_anomalies > 0 ? "Review recommended" : "All reviewed",
      color: "text-warning",
    },
    {
      label: "Health Score",
      value: calculateHealthScore(),
      icon: TrendingUp,
      trend: "Based on recent data",
      color: "text-success",
    },
  ];

  function calculateHealthScore() {
    if (!summary) return "—";
    const totalRecords = summary.total_records || 0;
    const criticalRecords = summary.critical_records || 0;

    if (totalRecords === 0) return "—";

    const score = Math.max(0, Math.min(100, 100 - (criticalRecords / totalRecords) * 50));
    return Math.round(score).toString();
  }

  function formatDate(dateString: string) {
    if (!dateString) return "Unknown date";
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  }

  function getStatusFromSeverity(severity: number): "normal" | "moderate" | "high" {
    if (severity >= 80) return "high";
    if (severity >= 50) return "moderate";
    return "normal";
  }

  // Get user initials
  const userInitials = user?.full_name
    ?.split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2) || 'U';

  if (loading && !summary) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? "w-64" : "w-0"
        } bg-sidebar border-r border-border transition-all duration-300 overflow-hidden flex flex-col`}
      >
        <div className="p-6 border-b border-border">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
              <Shield className="h-6 w-6 text-white" />
            </div>
            <span className="font-bold text-xl">MediVault</span>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          <Button
            variant="secondary"
            className="w-full justify-start"
            onClick={() => onNavigate("dashboard")}
          >
            <Home className="mr-2 h-4 w-4" />
            Dashboard
          </Button>
          <Button
            variant="ghost"
            className="w-full justify-start"
            onClick={() => onNavigate("upload")}
          >
            <Upload className="mr-2 h-4 w-4" />
            Upload Records
          </Button>
          <Button
            variant="ghost"
            className="w-full justify-start"
            onClick={() => onNavigate("search")}
          >
            <Search className="mr-2 h-4 w-4" />
            Search Records
          </Button>
          <Button
            variant="ghost"
            className="w-full justify-start"
            onClick={() => onNavigate("timeline")}
          >
            <Clock className="mr-2 h-4 w-4" />
            Timeline
          </Button>
          <Button variant="ghost" className="w-full justify-start">
            <Settings className="mr-2 h-4 w-4" />
            Settings
          </Button>
        </nav>

        <div className="p-4 border-t border-border space-y-2">
          <div className="flex items-center gap-3 p-2">
            <Avatar>
              <AvatarFallback className="bg-gradient-to-br from-primary to-secondary text-white">
                {userInitials}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <p className="font-medium truncate">{user?.full_name || 'User'}</p>
              <p className="text-xs text-muted-foreground truncate">{user?.email || ''}</p>
            </div>
          </div>
          <Button
            variant="ghost"
            className="w-full justify-start text-destructive hover:bg-destructive/10"
            onClick={handleLogout}
          >
            <LogOut className="mr-2 h-4 w-4" />
            Logout
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {/* Top Bar */}
        <header className="border-b border-border bg-background/80 backdrop-blur-xl sticky top-0 z-10">
          <div className="flex items-center justify-between p-4">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSidebarOpen(!sidebarOpen)}
              >
                <Menu className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-2xl font-bold">Dashboard</h1>
                <p className="text-sm text-muted-foreground">
                  Welcome back, {user?.full_name?.split(' ')[0] || 'there'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={handleRefresh}
                disabled={refreshing}
              >
                <RefreshCw className={`h-5 w-5 ${refreshing ? 'animate-spin' : ''}`} />
              </Button>
              <ThemeToggle isDark={isDark} onToggle={onToggleTheme} />
            </div>
          </div>
        </header>

        <div className="p-6 space-y-6">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {stats.map((stat) => (
              <Card key={stat.label} className="border-border bg-card/50 backdrop-blur">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <p className="text-sm text-muted-foreground">{stat.label}</p>
                      <p className="text-3xl font-bold">{stat.value}</p>
                      <p className="text-xs text-muted-foreground">{stat.trend}</p>
                    </div>
                    <div className={`p-3 rounded-xl bg-gradient-to-br from-primary/20 to-primary/10 border border-primary/20`}>
                      <stat.icon className={`h-5 w-5 ${stat.color}`} />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Health Alerts */}
          {anomalies.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold">Health Alerts</h2>
                <Button variant="outline" size="sm" onClick={() => onNavigate("timeline")}>
                  View All
                </Button>
              </div>
              {anomalies.map((anomaly) => (
                <Alert
                  key={anomaly.id}
                  className={
                    anomaly.is_critical || anomaly.severity >= 80
                      ? "border-danger bg-danger/10"
                      : anomaly.severity >= 50
                      ? "border-warning bg-warning/10"
                      : "border-info bg-info/10"
                  }
                >
                  <AlertCircle
                    className={`h-4 w-4 ${
                      anomaly.is_critical || anomaly.severity >= 80
                        ? "text-danger"
                        : anomaly.severity >= 50
                        ? "text-warning"
                        : "text-info"
                    }`}
                  />
                  <AlertDescription>
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-medium">{anomaly.title || anomaly.message}</p>
                        {anomaly.recommendation && (
                          <p className="text-sm text-muted-foreground mt-1">
                            {anomaly.recommendation}
                          </p>
                        )}
                        <p className="text-xs text-muted-foreground mt-1">
                          {formatDate(anomaly.detection_date || anomaly.created_at)}
                        </p>
                      </div>
                      <StatusBadge
                        status={
                          anomaly.is_critical || anomaly.severity >= 80
                            ? "high"
                            : anomaly.severity >= 50
                            ? "moderate"
                            : "normal"
                        }
                      />
                    </div>
                  </AlertDescription>
                </Alert>
              ))}
            </div>
          )}

          {/* Empty state for alerts */}
          {anomalies.length === 0 && (
            <Card className="border-success bg-success/10">
              <CardContent className="p-6">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-xl bg-success/20">
                    <TrendingUp className="h-5 w-5 text-success" />
                  </div>
                  <div>
                    <p className="font-medium text-success">All Clear!</p>
                    <p className="text-sm text-muted-foreground">No health alerts at this time.</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Recent Records */}
          {recentRecords.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold">Recent Records</h2>
                <Button variant="outline" onClick={() => onNavigate("timeline")}>
                  View All
                </Button>
              </div>
              <div className="grid gap-4">
                {recentRecords.map((record) => (
                  <Card key={record.id} className="hover:shadow-md transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between">
                        <div className="space-y-2 flex-1">
                          <div className="flex items-start justify-between">
                            <h3 className="font-semibold">
                              {record.document_type || record.file_name || 'Medical Record'}
                            </h3>
                            <StatusBadge status={getStatusFromSeverity(record.overall_severity || 0)} />
                          </div>
                          <div className="space-y-1 text-sm text-muted-foreground">
                            {record.issuing_hospital && <p>{record.issuing_hospital}</p>}
                            {record.issuing_doctor && <p>{record.issuing_doctor}</p>}
                            <p>{formatDate(record.document_date || record.created_at)}</p>
                            {record.clinical_summary && (
                              <p className="text-xs mt-2 line-clamp-2">{record.clinical_summary}</p>
                            )}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* Empty state for records */}
          {recentRecords.length === 0 && (
            <Card className="border-dashed">
              <CardContent className="p-12 text-center">
                <div className="mx-auto w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                  <FileText className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-lg font-semibold mb-2">No Medical Records Yet</h3>
                <p className="text-muted-foreground mb-4">
                  Start by uploading your first medical document
                </p>
                <Button onClick={() => onNavigate("upload")}>
                  <Upload className="mr-2 h-4 w-4" />
                  Upload Your First Record
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Quick Actions */}
          <Card className="relative overflow-hidden border-0">
            <div className="absolute inset-0 bg-gradient-to-r from-primary via-blue-500 to-secondary" />
            <div className="relative">
              <CardHeader>
                <CardTitle className="text-white">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="flex flex-wrap gap-4">
                <Button
                  variant="secondary"
                  className="bg-white text-black hover:bg-gray-100"
                  onClick={() => onNavigate("upload")}
                >
                  <Upload className="mr-2 h-4 w-4" />
                  Upload New Record
                </Button>
                <Button
                  variant="secondary"
                  className="bg-white/90 text-black hover:bg-white"
                  onClick={() => onNavigate("search")}
                >
                  <Search className="mr-2 h-4 w-4" />
                  Search Records
                </Button>
                <Button
                  variant="secondary"
                  className="bg-white/80 text-black hover:bg-white"
                  onClick={() => onNavigate("timeline")}
                >
                  <Clock className="mr-2 h-4 w-4" />
                  View Timeline
                </Button>
              </CardContent>
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
}
